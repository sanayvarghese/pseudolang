"""
Pass 1 - Registration Pass (Section 7.3 of spec).

Scans the entire source (block tree) without execution.
Collects:
  - All function definition names and their parameter lists
  - All global variable names (assigned at top level)

Builds a complete symbol table BEFORE any execution happens.
This enables mutual recursion and forward references.

Function definition detection heuristic:
  - Line matches name(args) pattern (word before opening paren)
  - AND has at least one child line (indented body)
"""

from typing import Dict, List, Optional, Set
from ..parser.indent_parser import Block, RawLine
from ..parser.normalizer import normalize_content
from ..parser.tokenizer import tokenize


# ──────────────────────────────────────────────────────────────
# Symbol table entries
# ──────────────────────────────────────────────────────────────

class FuncDef:
    def __init__(self, name: str, params: List[str], line: int):
        self.name = name
        self.params = params
        self.line = line

    def __repr__(self):
        return f"FuncDef({self.name}, params={self.params}, line={self.line})"


class SymbolTable:
    def __init__(self):
        self.functions: Dict[str, FuncDef] = {}
        self.global_vars: Set[str] = set()

    def register_function(self, name: str, params: List[str], line: int):
        self.functions[name] = FuncDef(name, params, line)

    def has_function(self, name: str) -> bool:
        return name in self.functions

    def get_function(self, name: str) -> Optional[FuncDef]:
        return self.functions.get(name)

    def register_global(self, name: str):
        self.global_vars.add(name)


# ──────────────────────────────────────────────────────────────
# Registration pass
# ──────────────────────────────────────────────────────────────

def run_registration_pass(blocks: List[Block]) -> SymbolTable:
    """
    Pass 1: scan block tree and register all function definitions
    and top-level global variable names.
    """
    table = SymbolTable()
    _scan_blocks(blocks, table, top_level=True)
    return table


def _scan_blocks(blocks: List[Block], table: SymbolTable, top_level: bool):
    for block in blocks:
        rl = block.line
        content = normalize_content(rl.content)
        lineno = rl.number

        # Skip blank and comment lines
        if not content or content.startswith('#'):
            continue

        # Strip optional trailing colon and semicolons
        content_stripped = content.rstrip(':;').rstrip()

        # Check if this block is a function definition:
        # Must have children (indented body) AND match name(args) pattern
        if block.children:
            func_name, params = _try_extract_func_def(content_stripped, lineno)
            if func_name is not None:
                table.register_function(func_name, params, lineno)
                # Recurse into children but NOT top_level (function body)
                continue   # don't descend for registration purposes

        # Top-level assignment - register as global var
        if top_level:
            varname = _try_extract_assignment_target(content_stripped)
            if varname:
                table.register_global(varname)


def _try_extract_func_def(content: str, lineno: int):
    """
    Detect function definition pattern: [prefix words] name(args)
    Returns (name, params) or (None, None).
    """
    # Find the last ( before end of line
    paren_open = content.rfind('(')
    paren_close = content.rfind(')')
    if paren_open == -1 or paren_close < paren_open:
        return None, None

    # The function name is the last word before the (
    before_paren = content[:paren_open].rstrip()
    if not before_paren:
        return None, None

    # Extract last word as function name
    parts = before_paren.split()
    if not parts or len(parts) > 2:
        return None, None
    if len(parts) == 2:
        if parts[0].lower() not in ('def', 'func', 'function', 'define', 'procedure',
                                    'algorithm', 'recursive', 'helper', 'method'):
            return None, None

    func_name = parts[-1]
    # Must be a valid identifier
    if not _is_valid_identifier(func_name):
        return None, None

    # Reject if func_name is a keyword
    if func_name.lower() in _KEYWORDS:
        return None, None

    # Parse parameters
    params_str = content[paren_open+1:paren_close].strip()
    if not params_str:
        params = []
    else:
        params = [p.strip() for p in params_str.split(',') if p.strip()]

    return func_name, params


def _try_extract_assignment_target(content: str) -> Optional[str]:
    """
    Try to extract the target variable name from an assignment line.
    Handles: x = ..., x := ..., x <- ..., set x to ..., let x be ..., x is ...
    """
    tokens = tokenize(content)
    if not tokens:
        return None

    # x = / x := / x <-
    if (len(tokens) >= 3 and tokens[0].type == 'WORD' and
            tokens[1].type == 'OP' and tokens[1].value in ('=', ':=', '<-')):
        name = tokens[0].value
        if _is_valid_identifier(name) and name.lower() not in _KEYWORDS:
            return name

    # set x to ... / let x be ...
    if (len(tokens) >= 3 and tokens[0].type == 'WORD' and
            tokens[0].value.lower() in ('set', 'let') and tokens[1].type == 'WORD'):
        name = tokens[1].value
        if _is_valid_identifier(name) and name.lower() not in _KEYWORDS:
            return name

    # store ... in x
    if (tokens[-1].type == 'WORD' and len(tokens) >= 3):
        last = tokens[-1].value
        if (len(tokens) >= 2 and tokens[-2].type == 'WORD' and
                tokens[-2].value.lower() == 'in'):
            if _is_valid_identifier(last) and last.lower() not in _KEYWORDS:
                return last

    return None


def _is_valid_identifier(name: str) -> bool:
    if not name:
        return False
    if not (name[0].isalpha() or name[0] == '_'):
        return False
    for ch in name[1:]:
        if not (ch.isalnum() or ch == '_'):
            return False
    return True


# Keywords that cannot be function or variable names
_KEYWORDS = frozenset([
    'if', 'else', 'for', 'while', 'until', 'return', 'break', 'continue',
    'and', 'or', 'not', 'true', 'false', 'null', 'none', 'nil',
    'def', 'func', 'function', 'define', 'procedure', 'algorithm',
    'recursive', 'helper', 'method', 'global', 'try', 'catch', 'except',
    'finally', 'raise', 'throw', 'print', 'show', 'display', 'say',
    'in', 'as', 'is', 'to', 'from', 'step', 'each', 'every', 'through',
    'when', 'check', 'given', 'otherwise', 'elif', 'each', 'foreach',
    'traverse', 'loop', 'repeat', 'iterate', 'attempt', 'swap', 'exchange',
    'set', 'let', 'store', 'give', 'back', 'output', 'send', 'skip', 'next',
    'stop', 'exit',
])
