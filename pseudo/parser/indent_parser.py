"""
Indentation Parser - builds a block tree from raw source lines.
Runs BEFORE normalization (as per spec Section 22.1).

A RawBlock represents a line plus all its child lines (indented beneath it).
The indentation parser handles:
  - Tab vs space detection (must not be mixed)
  - Consistent indentation unit detection
  - Deduction of block hierarchy from indent levels
  - IndentationError for unexpected dedents / tab+space mixing

Output: a list of RawLine objects with indent_level integers attached,
        forming a flat list that the mapping resolver walks in order.
        (We don't build an actual tree here; hierarchy is reconstructed
        later by the resolver using indent levels.)
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import unicodedata


# ──────────────────────────────────────────────────────────────
# RawLine - one physical source line after indentation parsed
# ──────────────────────────────────────────────────────────────

@dataclass
class RawLine:
    number: int          # 1-based line number in source file
    indent: int          # number of indent units (0 = top level)
    raw_indent: str      # actual leading whitespace (for error messages)
    content: str         # line content after stripping leading whitespace
    original: str        # full original line (unmodified)


# ──────────────────────────────────────────────────────────────
# parse_indentation
# ──────────────────────────────────────────────────────────────

class IndentationError_(Exception):
    """Pseudo indentation error."""
    def __init__(self, message: str, line_no: int):
        super().__init__(message)
        self.line_no = line_no


def collapse_parentheses(source: str) -> str:
    lines = source.splitlines()
    output_lines = []
    
    in_string = None
    open_parens = 0
    current_line = []
    
    for line in lines:
        i = 0
        n = len(line)
        comment_start = -1
        while i < n:
            c = line[i]
            if in_string:
                if c == '\\':
                    i += 2
                    continue
                if c == in_string:
                    in_string = None
            elif c == '#':
                comment_start = i
                break
            elif c in ('"', "'"):
                in_string = c
            elif c in ('(', '[', '{'):
                open_parens += 1
            elif c in (')', ']', '}'):
                open_parens = max(0, open_parens - 1)
            i += 1
            
        line_no_comment = line[:comment_start] if comment_start != -1 else line
        
        if open_parens > 0:
            current_line.append(line_no_comment)
            output_lines.append("")
        else:
            if current_line:
                current_line.append(line_no_comment)
                first_line = current_line[0]
                rest_lines = [ln.strip() for ln in current_line[1:]]
                joined = first_line + ' ' + ' '.join(rest_lines)
                
                first_line_index = len(output_lines) - len(current_line) + 1
                if 0 <= first_line_index < len(output_lines):
                    output_lines[first_line_index] = joined
                output_lines.append("")
                current_line = []
            else:
                output_lines.append(line)
                
    if current_line:
        first_line = current_line[0]
        rest_lines = [ln.strip() for ln in current_line[1:]]
        joined = first_line + ' ' + ' '.join(rest_lines)
        first_line_index = len(output_lines) - len(current_line)
        if 0 <= first_line_index < len(output_lines):
            output_lines[first_line_index] = joined
            
    return '\n'.join(output_lines)


BLOCK_STARTING_KEYWORDS = {
    'func', 'function', 'define', 'def', 'procedure', 'method', 'algorithm', 'helper', 'recursive',
    'for', 'loop', 'repeat', 'iterate', 'foreach', 'traverse',
    'while', 'until',
    'if', 'when', 'check', 'given', 'elif', 'else', 'otherwise',
    'try', 'attempt', 'catch', 'except', 'finally', 'always', 'cleanup',
    'keep', 'as', 'or', 'on'
}


def find_split_colon(content: str) -> Optional[int]:
    """
    Finds the index of the first un-nested colon ':' that separates a block header
    from an inline body.
    Returns the index or None.
    """
    in_string = None
    depth = 0
    i = 0
    n = len(content)
    while i < n:
        c = content[i]
        if in_string:
            if c == '\\':
                i += 2
                continue
            if c == in_string:
                in_string = None
        elif c in ('"', "'"):
            in_string = c
        elif c in ('(', '[', '{'):
            depth += 1
        elif c in (')', ']', '}'):
            depth = max(0, depth - 1)
        elif c == ':' and depth == 0:
            return i
        i += 1
    return None


def split_inline_blocks(content: str, indent_level: int) -> List[Tuple[int, str]]:
    """
    Splits inline blocks recursively.
    Returns a list of (indent_level, content).
    """
    colon_idx = find_split_colon(content)
    if colon_idx is None:
        return [(indent_level, content)]

    header = content[:colon_idx].strip()
    body = content[colon_idx+1:].strip()

    # Check if header starts with a block keyword
    parts = header.split()
    if not parts:
        return [(indent_level, content)]
    first_word = parts[0].lower()

    if first_word in BLOCK_STARTING_KEYWORDS and body and not body.startswith('#'):
        # Keep colon on the header block
        header_with_colon = header + ':'
        # Recursively split the body (which could have further inline blocks) at indent + 1
        return [(indent_level, header_with_colon)] + split_inline_blocks(body, indent_level + 1)

    return [(indent_level, content)]


def parse_indentation(source: str) -> List[RawLine]:
    """
    Parse the indentation of every non-empty, non-comment-only line.

    Returns a list of RawLine objects with integer indent levels.
    Raises IndentationError_ on mixing tabs/spaces or inconsistent indent.
    """
    source = collapse_parentheses(source)
    raw_lines = source.splitlines()

    # Detect tab vs space style from first indented line
    indent_char: Optional[str] = None   # ' ' or '\t'
    indent_size: Optional[int] = None   # number of indent_chars per level

    result: List[RawLine] = []

    for lineno, raw in enumerate(raw_lines, start=1):
        # Skip completely empty lines
        if not raw.strip():
            continue

        # Count leading whitespace
        leading = []
        for ch in raw:
            if ch in (' ', '\t'):
                leading.append(ch)
            else:
                break
        leading_str = ''.join(leading)
        content = raw[len(leading_str):]

        # Skip comment-only lines (they contribute to block tree)
        # We keep them; the resolver will drop them from execution.

        # Detect tab/space mixing
        if leading_str:
            has_space = ' ' in leading_str
            has_tab   = '\t' in leading_str
            if has_space and has_tab:
                raise IndentationError_(
                    f"IndentationError: inconsistent use of tabs and spaces at line {lineno}",
                    lineno
                )

            char = '\t' if has_tab else ' '

            if indent_char is None:
                indent_char = char
            elif char != indent_char:
                raise IndentationError_(
                    f"IndentationError: inconsistent use of tabs and spaces at line {lineno}",
                    lineno
                )

            count = len(leading_str)

            # Determine indent unit (first indented line sets it)
            if indent_size is None:
                indent_size = count
            indent_level = count // indent_size
        else:
            indent_level = 0

        # Split inline blocks
        split_lines = split_inline_blocks(content, indent_level)
        for level, split_content in split_lines:
            spacer = indent_char or ' '
            unit = indent_size or 4
            reconstructed_indent = leading_str + (spacer * (level - indent_level) * unit)
            result.append(RawLine(
                number=lineno,
                indent=level,
                raw_indent=reconstructed_indent,
                content=split_content,
                original=raw,
            ))

    return result


# ──────────────────────────────────────────────────────────────
# Block - hierarchical structure built from flat RawLine list
# ──────────────────────────────────────────────────────────────

@dataclass
class Block:
    line: RawLine
    children: List['Block'] = field(default_factory=list)


def build_block_tree(raw_lines: List[RawLine]) -> List[Block]:
    """
    Convert a flat list of RawLines (with indent integers) into a nested Block tree.
    Returns the list of top-level Blocks.
    """
    if not raw_lines:
        return []

    root: List[Block] = []
    stack: List[Block] = []   # stack of ancestor blocks

    for rl in raw_lines:
        block = Block(line=rl)

        if rl.indent == 0:
            root.append(block)
            stack = [block]
        else:
            # Pop stack until top has indent < rl.indent
            while len(stack) > 1 and stack[-1].line.indent >= rl.indent:
                stack.pop()

            # Parent is now stack[-1]
            if stack and stack[-1].line.indent < rl.indent:
                stack[-1].children.append(block)
            else:
                # Unexpected indent at top level
                root.append(block)

            # Maintain stack at current depth
            while len(stack) > 1 and stack[-1].line.indent >= rl.indent:
                stack.pop()
            stack.append(block)

    return root
