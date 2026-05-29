"""Main compiler pipeline - ties all passes together."""

import os
import sys
from typing import List, Optional

# Fix Windows Unicode output
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from .parser.indent_parser import parse_indentation, build_block_tree, IndentationError_
from .parser.normalizer import normalize_content
from .resolver.pass1_register import run_registration_pass, SymbolTable
from .resolver.pass2_resolver import MappingResolver, ParseError
from .analyzer.semantic import SemanticAnalyzer, SemanticError, SemanticWarning
from .resolver.pmap_loader import PmapLoader
from .parser.ast_nodes import ProgramNode
from .interpreter.interpreter import Interpreter, display_value
from .analyzer.complexity import ComplexityEngine, format_complexity
from .install import setup_home

# Ensure ~/.pseudo/ is up to date on every import
try:
    setup_home()
except Exception:
    pass  # Never crash on install errors



PSEUDO_HOME = os.path.join(os.path.expanduser('~'), '.pseudo')
DEFAULT_PMAP = os.path.join(PSEUDO_HOME, 'core', 'default.pmap')
CACHE_DIR    = os.path.join(PSEUDO_HOME, 'cache')


class CompileError(Exception):
    def __init__(self, msg, line=0):
        super().__init__(msg)
        self.line = line


def _get_local_config_pmap() -> Optional[str]:
    # Look for pseudo.config or .pseudorc in current working directory
    for fname in ('pseudo.config', '.pseudorc'):
        if os.path.exists(fname):
            try:
                with open(fname, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                if not content:
                    continue
                # Try to parse as JSON first
                if content.startswith('{'):
                    import json
                    data = json.loads(content)
                    path = data.get('pmap') or data.get('pmap_path')
                    if path:
                        return os.path.abspath(path)
                else:
                    # Otherwise treat the entire file content as the path
                    return os.path.abspath(content)
            except Exception:
                pass
    return None


def _get_pmap_path(source_path: str, explicit_pmap: Optional[str] = None) -> str:
    """Determine which .pmap to use based on filename or explicit flag."""
    if explicit_pmap:
        if os.path.exists(explicit_pmap):
            return os.path.abspath(explicit_pmap)
        # Try ~/.pseudo/custom/
        custom = os.path.join(PSEUDO_HOME, 'custom', explicit_pmap)
        if os.path.exists(custom):
            return custom
        # Try current working directory
        cwd_path = os.path.join(os.getcwd(), explicit_pmap)
        if os.path.exists(cwd_path):
            return cwd_path
        return explicit_pmap

    # Check for local config in current working directory
    local_pmap = _get_local_config_pmap()
    if local_pmap and os.path.exists(local_pmap):
        return local_pmap

    # Try custom.pmap first
    custom = os.path.join(PSEUDO_HOME, 'custom', 'custom.pmap')
    if os.path.exists(custom):
        return custom

    return DEFAULT_PMAP


def compile_source(source: str, source_path: str = '<stdin>',
                   pmap_path: Optional[str] = None) -> tuple:
    """
    Full compile pipeline.
    Returns (program_node, symbol_table, warnings).
    Raises CompileError on failure.
    """
    # 1. Validate extension
    _check_extension(source_path)

    # 2. Indentation parser
    try:
        raw_lines = parse_indentation(source)
    except IndentationError_ as e:
        raise CompileError(str(e), e.line_no)

    blocks = build_block_tree(raw_lines)

    # 3. Pass 1 - registration
    symbol_table = run_registration_pass(blocks)

    # 4. Load .pmap
    effective_pmap = pmap_path or _get_pmap_path(source_path)
    if not os.path.exists(effective_pmap):
        # Fall back to bundled default
        effective_pmap = _bundled_default_pmap()

    loader = PmapLoader(effective_pmap, cache_dir=CACHE_DIR)
    try:
        loader.load()
    except Exception as e:
        raise CompileError(str(e))

    # 5. Pass 2 - mapping resolver
    resolver = MappingResolver(symbol_table, loader)
    try:
        stmts = resolver.resolve_blocks(blocks)
    except ParseError as e:
        msg = str(e)
        if e.suggestions:
            msg += "\n  Did you mean?\n" + '\n'.join(f"    {s}" for s in e.suggestions)
        raise CompileError(msg, e.line_no)

    program = ProgramNode(body=stmts)
    program.line_resolutions = resolver.line_resolutions

    # 6. Semantic analysis
    analyzer = SemanticAnalyzer(symbol_table)
    try:
        warnings = analyzer.analyze(program)
    except SemanticError as e:
        raise CompileError(str(e), e.line_no)

    return program, symbol_table, warnings


def run_program(source: str, source_path: str = '<stdin>',
                pmap_path: Optional[str] = None,
                inputs: Optional[List[str]] = None,
                timeout: float = 5.0,
                max_iter: int = 10_000_000,
                analyze: bool = False,
                explain: bool = False,
                summary: bool = False,
                dry_run: bool = False,
                step_mode: bool = False,
                no_auto_print: bool = False) -> None:
    """Full run pipeline with output."""
    try:
        program, symbol_table, warnings = compile_source(source, source_path, pmap_path)
    except CompileError as e:
        line_part = f"\n   Line {e.line}" if e.line else ""
        print(f"✗ {e}{line_part}", file=sys.stderr)
        return

    # Show warnings
    for w in warnings:
        print(str(w), file=sys.stderr)
        if 'Run anyway? (y/n)' in str(w):
            try:
                ans = input().strip().lower()
                if ans != 'y':
                    return
            except EOFError:
                pass

    if dry_run:
        _dry_run_output(program, source)
        return

    # Parse inputs
    parsed_inputs = _parse_inputs(inputs) if inputs else []

    interp = Interpreter(
        timeout=timeout,
        max_iter=max_iter,
        inputs=parsed_inputs,
        step_mode=step_mode,
        no_auto_print=no_auto_print,
    )

    try:
        interp.run(program, source=source)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)

    if analyze:
        engine = ComplexityEngine()
        results = engine.analyze(program)
        print()
        print(format_complexity(results, explain=explain, summary=summary))


def _check_extension(path: str):
    if path == '<stdin>':
        return
    _, ext = os.path.splitext(path)
    if ext == '.pseudo':
        raise CompileError("FileError: Did you mean .pseudo? (common misspelling)")
    if ext == '.txt':
        raise CompileError("FileError: pseudo only accepts .pseudo or .psu files")
    if ext == '.py':
        raise CompileError("FileError: That looks like a Python file")
    if ext not in ('.pseudo', '.psu'):
        raise CompileError(f"FileError: pseudo only accepts .pseudo or .psu files (got {ext!r})")


def _parse_inputs(inputs: List[str]) -> List[str]:
    result = []
    for inp in inputs:
        # Could be a filename or inline string with \n
        if os.path.isfile(inp):
            with open(inp) as f:
                result.extend(line.rstrip('\n') for line in f)
        else:
            result.extend(inp.replace('\\n', '\n').split('\n'))
    return result


def _dry_run_output(program: ProgramNode, source: str):
    source_lines = source.splitlines()
    line_resolutions = getattr(program, 'line_resolutions', {})
    
    # We want to print for each line that has a resolution
    # Let's iterate in order of line number
    for lineno in sorted(line_resolutions.keys()):
        if 1 <= lineno <= len(source_lines):
            line_text = source_lines[lineno - 1]
            print(f"  Line {lineno}:  \"{line_text}\"")
            for res_line in line_resolutions[lineno]:
                print(f"           {res_line}")
            print()
    print("No errors found. Safe to run.")


def _bundled_default_pmap() -> str:
    """Return path to the bundled default.pmap that ships with pseudo."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, 'pseudo', 'data', 'default.pmap')
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, 'data', 'default.pmap')
