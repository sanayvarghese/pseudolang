"""
Tokenizer / Lexer for the Pseudo language.

Tokenizes a single line of content (after indentation has been stripped).
No regex - custom character-by-character scanner.

Token types:
  WORD       - identifier or keyword
  NUMBER     - numeric literal (int or float)
  STRING     - quoted string literal
  OP         - operator characters
  LPAREN     - (
  RPAREN     - )
  LBRACKET   - [
  RBRACKET   - ]
  LBRACE     - {
  RBRACE     - }
  COMMA      - ,
  COLON      - :
  DOLLAR     - $ (for $input)
  SEMICOLON  - ;
  NEWLINE    - end of line (synthetic)
  EOF        - end of token stream
"""

from dataclasses import dataclass
from typing import List, Optional

# ──────────────────────────────────────────────────────────────
# Token definition
# ──────────────────────────────────────────────────────────────


@dataclass
class Token:
    type: str
    value: str
    line: int = 0
    col: int = 0

    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"


# ──────────────────────────────────────────────────────────────
# Multi-character operators
# ──────────────────────────────────────────────────────────────

MULTI_OPS = [":=", "<-", "<=", ">=", "!=", "==", "**", "//", "&&", "||", "->"]

SINGLE_OPS = set("+-*/%<>!&|^=@")


# ──────────────────────────────────────────────────────────────
# Tokenizer
# ──────────────────────────────────────────────────────────────


def tokenize(line: str, line_no: int = 0) -> List[Token]:
    """
    Tokenize a single line of pseudo source (indentation already stripped).
    Returns a flat list of Token objects.
    """
    tokens: List[Token] = []
    i = 0
    n = len(line)

    while i < n:
        c = line[i]

        # ── whitespace ─────────────────────────────────────────
        if c in " \t":
            i += 1
            continue

        # ── comment (#) ────────────────────────────────────────
        if c == "#":
            tokens.append(Token("COMMENT", line[i:], line_no, i))
            break

        # ── string literal ─────────────────────────────────────
        if c in ('"', "'"):
            tok, i = _scan_string(line, i, line_no)
            tokens.append(tok)
            continue

        # ── number ─────────────────────────────────────────────
        if c.isdigit() or (
            c == "-"
            and i + 1 < n
            and line[i + 1].isdigit()
            and (
                not tokens
                or tokens[-1].type in ("OP", "LPAREN", "LBRACKET", "COMMA", "COLON")
            )
        ):
            tok, i = _scan_number(line, i, line_no)
            tokens.append(tok)
            continue

        # ── dollar sign ────────────────────────────────────────
        if c == "$":
            tokens.append(Token("DOLLAR", "$", line_no, i))
            i += 1
            continue

        # ── single-char punctuation ────────────────────────────
        if c == "(":
            tokens.append(Token("LPAREN", "(", line_no, i))
            i += 1
            continue
        if c == ")":
            tokens.append(Token("RPAREN", ")", line_no, i))
            i += 1
            continue
        if c == "[":
            tokens.append(Token("LBRACKET", "[", line_no, i))
            i += 1
            continue
        if c == "]":
            tokens.append(Token("RBRACKET", "]", line_no, i))
            i += 1
            continue
        if c == "{":
            tokens.append(Token("LBRACE", "{", line_no, i))
            i += 1
            continue
        if c == "}":
            tokens.append(Token("RBRACE", "}", line_no, i))
            i += 1
            continue
        if c == ",":
            tokens.append(Token("COMMA", ",", line_no, i))
            i += 1
            continue
        # NOTE: ':' is handled AFTER multi-char ops so that ':=' is one OP token
        if c == ";":
            tokens.append(Token("SEMICOLON", ";", line_no, i))
            i += 1
            continue
        if c == ".":
            tokens.append(Token("DOT", ".", line_no, i))
            i += 1
            continue
        if c == "?":
            tokens.append(Token("QUESTION", "?", line_no, i))
            i += 1
            continue

        # ── multi-char operators ────────────────────────────────
        found_multi = False
        for op in MULTI_OPS:
            if line[i : i + len(op)] == op:
                tokens.append(Token("OP", op, line_no, i))
                i += len(op)
                found_multi = True
                break
        if found_multi:
            continue

        # ── single-char operators ───────────────────────────────
        if c in SINGLE_OPS:
            tokens.append(Token("OP", c, line_no, i))
            i += 1
            continue

        # ── colon (after multi-char check so := is caught first) ──
        if c == ":":
            tokens.append(Token("COLON", ":", line_no, i))
            i += 1
            continue

        # ── identifiers / keywords / words ─────────────────────
        if c.isalpha() or c == "_":
            tok, i = _scan_word(line, i, line_no)
            tokens.append(tok)
            continue

        # ── unknown character - skip ────────────────────────────
        i += 1

    tokens.append(Token("EOF", "", line_no, n))
    return tokens


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────


def _scan_string(line: str, start: int, line_no: int):
    """Scan a quoted string, handling escape sequences."""
    quote = line[start]
    i = start + 1
    buf = []
    while i < len(line):
        c = line[i]
        if c == "\\" and i + 1 < len(line):
            nxt = line[i + 1]
            escapes = {
                "n": "\n",
                "t": "\t",
                "r": "\r",
                "\\": "\\",
                '"': '"',
                "'": "'",
                "{": "{",
                "}": "}",
            }
            buf.append(escapes.get(nxt, nxt))
            i += 2
        elif c == quote:
            i += 1
            break
        else:
            buf.append(c)
            i += 1
    return Token("STRING", "".join(buf), line_no, start), i


def _scan_number(line: str, start: int, line_no: int):
    """Scan an integer or float literal."""
    i = start
    if line[i] == "-":
        i += 1
    while i < len(line) and line[i].isdigit():
        i += 1
    if i < len(line) and line[i] == "." and i + 1 < len(line) and line[i + 1].isdigit():
        i += 1
        while i < len(line) and line[i].isdigit():
            i += 1
    return Token("NUMBER", line[start:i], line_no, start), i


def _scan_word(line: str, start: int, line_no: int):
    """Scan an identifier or keyword word."""
    i = start
    while i < len(line) and (line[i].isalnum() or line[i] == "_"):
        i += 1
    # Check for apostrophe contractions like "isn't"
    if i < len(line) and line[i] == "'" and i + 1 < len(line) and line[i + 1].isalpha():
        i += 1
        while i < len(line) and (line[i].isalnum() or line[i] == "_"):
            i += 1
    return Token("WORD", line[start:i], line_no, start), i


# ──────────────────────────────────────────────────────────────
# Utility: token stream helpers
# ──────────────────────────────────────────────────────────────


class TokenStream:
    """Cursor-based token stream for parsers."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self, offset: int = 0) -> Token:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return Token("EOF", "")

    def advance(self) -> Token:
        tok = self.peek()
        if tok.type != "EOF":
            self.pos += 1
        return tok

    def expect(self, type_: str, value: Optional[str] = None) -> Token:
        tok = self.advance()
        if tok.type != type_:
            raise SyntaxError(f"Expected {type_!r} got {tok.type!r} ({tok.value!r})")
        if value is not None and tok.value.lower() != value.lower():
            raise SyntaxError(f"Expected {value!r} got {tok.value!r}")
        return tok

    def match(self, type_: str, value: Optional[str] = None) -> bool:
        tok = self.peek()
        if tok.type != type_:
            return False
        if value is not None and tok.value.lower() != value.lower():
            return False
        return True

    def consume_if(self, type_: str, value: Optional[str] = None) -> Optional[Token]:
        if self.match(type_, value):
            return self.advance()
        return None

    def at_end(self) -> bool:
        return self.peek().type == "EOF"

    def remaining_words(self) -> List[str]:
        """Return lowercase word values from current pos to EOF (excluding EOF)."""
        result = []
        for tok in self.tokens[self.pos :]:
            if tok.type == "EOF":
                break
            if tok.type not in ("SEMICOLON", "COMMENT"):
                result.append(tok.value)
        return result
