"""CLI entry point for the pseudo command (Section 19)."""

import os
import sys
import argparse


def main():
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        prog='pseudo',
        description='Pseudo - run pseudocode as a real language'
    )
    subparsers = parser.add_subparsers(dest='command')

    # ── pseudo run ────────────────────────────────────────────
    run_p = subparsers.add_parser('run', help='Run a .pseudo or .psu file')
    run_p.add_argument('file', help='Source file (.pseudo or .psu)')
    run_p.add_argument('--lang', metavar='PMAP', help='Use specific .pmap file')
    run_p.add_argument('-i', metavar='INPUT', dest='input', action='append',
                       help='Inline input or input file (repeatable)')
    run_p.add_argument('--analyze', action='store_true', help='Show complexity analysis')
    run_p.add_argument('--explain', action='store_true', help='With --analyze: show reasoning')
    run_p.add_argument('--summary', action='store_true', help='With --analyze: one line output')
    run_p.add_argument('--timeout', type=float, default=5.0, metavar='N',
                       help='Execution timeout in seconds (0 = unlimited)')
    run_p.add_argument('--max-iter', type=int, default=10_000_000, metavar='N',
                       help='Maximum loop iterations')
    run_p.add_argument('--dry-run', action='store_true', help='Show mapping, do not execute')
    run_p.add_argument('--step', action='store_true', help='Step through line by line')
    run_p.add_argument('--no-auto-print', action='store_true', help='Disable automatic printing of standalone expressions')

    # ── pseudo validate ───────────────────────────────────────
    val_p = subparsers.add_parser('validate', help='Validate a .pseudo or .pmap file')
    val_p.add_argument('file', help='File to validate')

    # ── pseudo explain ────────────────────────────────────────
    exp_p = subparsers.add_parser('explain', help='Explain what a line maps to')
    exp_p.add_argument('line', nargs='?', help='Line of pseudo code to explain')
    exp_p.add_argument('--list', metavar='CANONICAL', help='List all patterns for a canonical')

    # ── pseudo init ───────────────────────────────────────────
    subparsers.add_parser('init', help='Create custom.pmap in ~/.pseudo/custom/')

    # ── pseudo version ────────────────────────────────────────
    subparsers.add_parser('version', help='Show version')

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    if args.command == 'version':
        from . import __version__
        print(f"pseudo {__version__}")
        return

    if args.command == 'init':
        _cmd_init()
        return

    if args.command == 'run':
        _cmd_run(args)
        return

    if args.command == 'validate':
        _cmd_validate(args)
        return

    if args.command == 'explain':
        _cmd_explain(args)
        return

    parser.print_help()


# ── Commands ──────────────────────────────────────────────────

def _cmd_run(args):
    path = args.file
    if not os.path.exists(path):
        print(f"✗ FileError: File not found: {path}")
        sys.exit(1)

    with open(path, 'r', encoding='utf-8') as f:
        source = f.read()

    from .compiler import run_program
    run_program(
        source=source,
        source_path=path,
        pmap_path=args.lang,
        inputs=args.input or [],
        timeout=args.timeout,
        max_iter=args.max_iter,
        analyze=args.analyze,
        explain=args.explain,
        summary=args.summary,
        dry_run=args.dry_run,
        step_mode=args.step,
        no_auto_print=args.no_auto_print,
    )


def _cmd_validate(args):
    path = args.file
    if not os.path.exists(path):
        print(f"✗ FileError: File not found: {path}")
        sys.exit(1)

    _, ext = os.path.splitext(path)
    if ext == '.pmap':
        _validate_pmap(path)
    else:
        _validate_source(path)


def _validate_source(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        source = f.read()
    from .compiler import compile_source, CompileError, _dry_run_output
    print(f"Validating {path}...")
    try:
        program, symbol_table, warnings = compile_source(source, path)
        _dry_run_output(program, source)
        for w in warnings:
            print(f"  {w}")
    except CompileError as e:
        print(f"  ✗ {e}")


def _validate_pmap(path: str):
    from .resolver.pmap_loader import PmapLoader, PmapError
    print(f"Validating {path}...")
    try:
        loader = PmapLoader(path)
        trie = loader.load()
        patterns = trie.all_patterns()
        print(f"  ✓ {len(patterns)} patterns loaded.")
        if loader.warnings:
            for w in loader.warnings:
                print(f"  ⚠ {w}")
        else:
            print("  No errors found.")
    except PmapError as e:
        print(f"  ✗ {e}")


def _cmd_explain(args):
    from .compiler import _get_pmap_path, _bundled_default_pmap
    from .resolver.pmap_loader import PmapLoader

    if not args.list and not args.line:
        print("Error: Specify a line of code to explain or use --list CANONICAL")
        return

    if args.list:
        pmap_path = _bundled_default_pmap()
        loader = PmapLoader(pmap_path)
        trie = loader.load()
        print(f"{args.list} patterns:")
        for i, p in enumerate(trie.all_patterns(), 1):
            if p.canonical == args.list.upper():
                toks = ' '.join(
                    t.literal if not t.is_placeholder
                    else '{' + t.placeholder.var_name + ':' + t.placeholder.ph_type + '}'
                    for t in p.tokens
                )
                print(f"  {i}. {toks}")
        return

    if args.line:
        pmap_path = _bundled_default_pmap()
        loader = PmapLoader(pmap_path)
        loader.load()
        from .parser.tokenizer import tokenize
        words = [t.value for t in tokenize(args.line) if t.type not in ('EOF', 'COMMENT', 'SEMICOLON')]
        result = loader.match(words)
        if result:
            print("  Using: default.pmap")
            print()
            if result.pattern:
                pat_str = ' '.join(
                    t.literal if not t.is_placeholder
                    else '{' + t.placeholder.var_name + ':' + t.placeholder.ph_type + '}'
                    for t in result.pattern.tokens
                )
                print(f"  Matched pattern : {pat_str!r}")
            print(f"  Canonical form  : {result.canonical}")
            print("  Captures        :")
            for k, v in result.captures.items():
                print(f"    {{{k}}} = {v!r}")
        else:
            print("No match found.")
            print("Hint: Add a pattern to your custom.pmap")


def _cmd_init():
    print("Initializing Pseudo project...")
    try:
        pmap_input = input("Enter a new name for your custom pmap (e.g., custom.pmap) or enter name/location of an existing pmap: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nInitialization cancelled.")
        return

    # If empty, default to 'custom.pmap'
    if not pmap_input:
        pmap_input = 'custom.pmap'

    # Ensure it ends with .pmap
    if not pmap_input.endswith('.pmap'):
        pmap_input += '.pmap'

    target_pmap_path = os.path.abspath(pmap_input)
    
    # If the pmap file doesn't exist, create it from template
    if not os.path.exists(target_pmap_path):
        template = _custom_pmap_template()
        try:
            # Create any parent directories if needed
            os.makedirs(os.path.dirname(target_pmap_path), exist_ok=True)
            with open(target_pmap_path, 'w', encoding='utf-8') as f:
                f.write(template)
            print(f"✓ Created new custom pmap file at: {target_pmap_path}")
        except Exception as e:
            print(f"✗ Error creating pmap file: {e}")
            return
    else:
        print(f"✓ Found existing pmap file at: {target_pmap_path}")

    # Now create the config file in the current working directory
    # Let's write it to 'pseudo.config' as JSON
    config_data = {
        "pmap": pmap_input
    }
    import json
    config_path = os.path.join(os.getcwd(), 'pseudo.config')
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4)
        print(f"✓ Created local config file at: {config_path}")
        print(f"  Linked pmap: {pmap_input}")
    except Exception as e:
        print(f"✗ Error creating config file: {e}")


def _custom_pmap_template() -> str:
    return """\
@pmap-version 1.0
@pseudo-version >=1.0 <2.0
@language "Custom"
@author ""
@inherit default.pmap

# ─────────────────────────────────────────────────────────────
# Custom mapping file - generated by: pseudo init
#
# This file APPENDS to default.pmap (patterns tried FIRST).
# Remove or change @inherit to fully replace the default.
#
# PLACEHOLDER TYPES:
#   {name:name}        single identifier word
#   {value:expr}       full expression
#   {n:number}         numeric literal only
#   {condition:expr}   boolean expression
#   {type:word}        single type keyword
#   {collection:expr}  iterable expression
#   {text:any}         everything to end of line
# ─────────────────────────────────────────────────────────────

# Example: add new ways to write a for loop
# [FOR_LOOP]
# go through {var:name} from {start:expr} to {end:expr}
# count {var:name} from {start:expr} until {end:expr}

# Example: completely replace how PRINT works
# [PRINT] @replace
# yell {value:expr}
# scream {value:expr}

"""


if __name__ == '__main__':
    main()
