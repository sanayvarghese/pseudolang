"""
Expression Parser - recursive descent parser for pseudo expressions.

Handles (Section 12 of spec):
  - Arithmetic: + - * / // % ** ^ x^n  x power n
  - Comparison: > < >= <= == != equals greater than less than at least at most
  - Logical: and or not && || ! both...and either...or isn't
  - String/List operations
  - Function calls: name(args)
  - Method calls: obj.method(args) and obj.attr
  - Indexing: arr[i]
  - Slicing: arr[start:end]
  - String interpolation: "hello {name}"
  - Literals: number, string, bool, null, list, dict, set
  - Variables

NO eval() used anywhere.
"""

from typing import Any, List, Optional, Tuple
from .tokenizer import tokenize, Token, TokenStream
from .ast_nodes import (
    NumberLiteralNode, StringLiteralNode, BoolLiteralNode, NullLiteralNode,
    ListLiteralNode, SetLiteralNode, DictLiteralNode,
    VariableNode, BinaryOpNode, UnaryOpNode, IndexNode, SliceNode,
    CallNode, AttributeNode, AttributeCallNode, InterpolatedStringNode,
    TernaryNode,
)


# ──────────────────────────────────────────────────────────────
# English operator aliases
# ──────────────────────────────────────────────────────────────

COMPARISON_ENGLISH = {
    'greater than or equal': '>=',
    'less than or equal': '<=',
    'greater than': '>',
    'less than': '<',
    'at least': '>=',
    'at most': '<=',
    'is equal to': '==',
    'not equal to': '!=',
    'not equals': '!=',
    'same as': '==',
    'different from': '!=',
    'equals': '==',
}


class ExpressionParser:
    """
    Parse a raw expression string (or token list) into an AST node.
    Uses recursive descent with standard precedence.
    """

    def __init__(self, source: str, line_no: int = 0):
        self.source = source
        self.line_no = line_no
        tokens = tokenize(source, line_no)
        # Filter out SEMICOLON tokens
        tokens = [t for t in tokens if t.type != 'SEMICOLON']
        self.stream = TokenStream(tokens)

    def parse(self) -> Any:
        if self.stream.peek().type == 'EOF':
            return NullLiteralNode(line=self.line_no)
        node = self._parse_ternary()
        if self.stream.peek().type != 'EOF':
            raise SyntaxError(f"Unexpected token {self.stream.peek().value!r}")
        return node

    # ── Precedence levels (low → high) ────────────────────────

    def _parse_ternary(self) -> Any:
        cond = self._parse_or()
        if self.stream.peek().type == 'QUESTION':
            self.stream.advance()  # consume '?'
            true_val = self._parse_ternary()
            self.stream.expect('COLON')
            false_val = self._parse_ternary()
            return TernaryNode(cond, true_val, false_val, self.line_no)
        return cond

    def _parse_or(self) -> Any:
        left = self._parse_and()
        while True:
            if self._match_word('or') or self._match_op('||'):
                self.stream.advance()
                right = self._parse_and()
                left = BinaryOpNode(left, 'or', right, self.line_no)
            elif self._peek_words(['either']):
                # "either A or B"
                self.stream.advance()  # either
                left_inner = self._parse_and()
                self._expect_word('or')
                right = self._parse_and()
                left = BinaryOpNode(left_inner, 'or', right, self.line_no)
            else:
                break
        return left

    def _parse_and(self) -> Any:
        left = self._parse_not()
        while True:
            if self._match_word('and') or self._match_op('&&'):
                self.stream.advance()
                right = self._parse_not()
                left = BinaryOpNode(left, 'and', right, self.line_no)
            elif self._peek_words(['both']):
                self.stream.advance()  # both
                left_inner = self._parse_not()
                self._expect_word('and')
                right = self._parse_not()
                left = BinaryOpNode(left_inner, 'and', right, self.line_no)
            else:
                break
        return left

    def _parse_not(self) -> Any:
        if self._match_word('not') or self._match_op('!'):
            self.stream.advance()
            operand = self._parse_not()
            return UnaryOpNode('not', operand, self.line_no)
        if self._peek_words(["isn't"]):
            self.stream.advance()
            operand = self._parse_not()
            return UnaryOpNode('not', operand, self.line_no)
        return self._parse_comparison()

    def _parse_comparison(self) -> Any:
        # Try english multi-word comparisons first
        english_result = self._try_english_comparison()
        if english_result is not None:
            return english_result

        left = self._parse_add_sub()
        while True:
            op = self._peek_comparison_op()
            if op is None:
                break
            # consume tokens for this op
            self._consume_comparison_op(op)
            right = self._parse_add_sub()
            left = BinaryOpNode(left, op, right, self.line_no)
        return left

    def _peek_comparison_op(self) -> Optional[str]:
        tok = self.stream.peek()
        if tok.type == 'OP':
            if tok.value in ('>', '<', '>=', '<=', '==', '!='):
                return tok.value
        if tok.type == 'WORD':
            w = tok.value.lower()
            if w == 'in':
                return 'in'
            if w == 'not' and self.stream.peek(1).type == 'WORD' and self.stream.peek(1).value.lower() == 'in':
                return 'not in'
            if w == 'equals':
                return '=='
            if w == 'is' and self.stream.peek(1).type == 'WORD':
                w2 = self.stream.peek(1).value.lower()
                if w2 == 'equal':
                    return '=='
                if w2 == 'not':
                    return '!='
            # Multi-word English comparisons - detect by peeking ahead
            for phrase, op in COMPARISON_ENGLISH.items():
                words = phrase.split()
                match = all(
                    self.stream.peek(i).type == 'WORD' and
                    self.stream.peek(i).value.lower() == words[i]
                    for i in range(len(words))
                )
                if match:
                    return op
        return None

    def _consume_comparison_op(self, op: str):
        tok = self.stream.peek()
        if tok.type == 'OP' and tok.value == op:
            self.stream.advance()
            return
        if tok.type == 'WORD':
            w = tok.value.lower()
            if w == 'in' and op == 'in':
                self.stream.advance()
                return
            if w == 'not' and op == 'not in':
                self.stream.advance()  # not
                self.stream.advance()  # in
                return
        # English forms - consume correct number of words
        for phrase, mapped_op in COMPARISON_ENGLISH.items():
            if mapped_op != op:
                continue
            words = phrase.split()
            match = all(
                self.stream.peek(i).type == 'WORD' and
                self.stream.peek(i).value.lower() == words[i]
                for i in range(len(words))
            )
            if match:
                for _ in words:
                    self.stream.advance()
                return
        # Single-word English forms
        w = tok.value.lower() if tok.type == 'WORD' else ''
        if w == 'equals':
            self.stream.advance()
            return
        if w == 'is':
            self.stream.advance()
            nxt = self.stream.peek()
            if nxt.type == 'WORD' and nxt.value.lower() in ('equal', 'not'):
                self.stream.advance()
                if self.stream.peek().type == 'WORD' and self.stream.peek().value.lower() == 'to':
                    self.stream.advance()

    def _try_english_comparison(self) -> Optional[Any]:
        """Not used - English comparisons now handled in _peek/_consume_comparison_op."""
        return None

    def _parse_add_sub(self) -> Any:
        left = self._parse_mul_div()
        while True:
            tok = self.stream.peek()
            if tok.type == 'OP' and tok.value in ('+', '-'):
                op = tok.value
                self.stream.advance()
                right = self._parse_mul_div()
                left = BinaryOpNode(left, op, right, self.line_no)
            else:
                break
        return left

    def _parse_mul_div(self) -> Any:
        left = self._parse_power()
        while True:
            tok = self.stream.peek()
            if tok.type == 'OP' and tok.value in ('*', '/', '//', '%'):
                op = tok.value
                self.stream.advance()
                right = self._parse_power()
                left = BinaryOpNode(left, op, right, self.line_no)
            else:
                break
        return left

    def _parse_power(self) -> Any:
        left = self._parse_unary()
        tok = self.stream.peek()
        if tok.type == 'OP' and tok.value in ('**', '^'):
            self.stream.advance()
            right = self._parse_power()   # right-associative
            return BinaryOpNode(left, '**', right, self.line_no)
        if tok.type == 'WORD' and tok.value.lower() == 'power':
            self.stream.advance()
            right = self._parse_power()
            return BinaryOpNode(left, '**', right, self.line_no)
        return left

    def _parse_unary(self) -> Any:
        tok = self.stream.peek()
        if tok.type == 'OP' and tok.value == '-':
            self.stream.advance()
            operand = self._parse_postfix()
            return UnaryOpNode('-', operand, self.line_no)
        if tok.type == 'OP' and tok.value == '+':
            self.stream.advance()
            return self._parse_postfix()
        return self._parse_postfix()

    def _parse_postfix(self) -> Any:
        """Handles indexing arr[i], slicing arr[i:j], method calls obj.method(), obj.attr"""
        node = self._parse_primary()
        while True:
            tok = self.stream.peek()
            if tok.type == 'LBRACKET':
                self.stream.advance()
                # Check for slice
                if self.stream.peek().type == 'COLON':
                    # [:end]
                    self.stream.advance()
                    end = self._parse_ternary() if self.stream.peek().type != 'RBRACKET' else None
                    self.stream.consume_if('RBRACKET')
                    node = SliceNode(node, None, end, self.line_no)
                else:
                    idx = self._parse_ternary()
                    if self.stream.peek().type == 'COLON':
                        self.stream.advance()
                        end = self._parse_ternary() if self.stream.peek().type != 'RBRACKET' else None
                        self.stream.consume_if('RBRACKET')
                        node = SliceNode(node, idx, end, self.line_no)
                    else:
                        self.stream.consume_if('RBRACKET')
                        node = IndexNode(node, idx, self.line_no)
            elif tok.type == 'DOT':
                self.stream.advance()
                attr_tok = self.stream.advance()
                attr = attr_tok.value
                if attr.startswith('_'):
                    raise SyntaxError(f"SecurityError: Access to private attribute {attr!r} is forbidden")
                if self.stream.peek().type == 'LPAREN':
                    # Method call
                    self.stream.advance()
                    args = self._parse_arg_list()
                    self.stream.consume_if('RPAREN')
                    node = AttributeCallNode(node, attr, args, self.line_no)
                else:
                    node = AttributeNode(node, attr, self.line_no)
            else:
                break
        return node

    def _parse_primary(self) -> Any:
        tok = self.stream.peek()

        # Number
        if tok.type == 'NUMBER':
            self.stream.advance()
            val = tok.value
            if '.' in val:
                return NumberLiteralNode(float(val), self.line_no)
            return NumberLiteralNode(int(val), self.line_no)

        # String
        if tok.type == 'STRING':
            self.stream.advance()
            return _parse_interpolated_string(tok.value, self.line_no)

        # Parenthesised expression
        if tok.type == 'LPAREN':
            self.stream.advance()
            node = self._parse_ternary()
            self.stream.consume_if('RPAREN')
            return node

        # List literal
        if tok.type == 'LBRACKET':
            self.stream.advance()
            elements = []
            while self.stream.peek().type not in ('RBRACKET', 'EOF'):
                elements.append(self._parse_ternary())
                self.stream.consume_if('COMMA')
            self.stream.consume_if('RBRACKET')
            return ListLiteralNode(elements, self.line_no)

        # Dict / Set literal {key: val, ...} or {item, item, ...}
        if tok.type == 'LBRACE':
            return self._parse_dict_or_set()

        # $input
        if tok.type == 'DOLLAR':
            self.stream.advance()
            # $input or $input(prompt) or $input as type
            if self.stream.peek().type == 'WORD' and self.stream.peek().value.lower() == 'input':
                self.stream.advance()
                # just return a special node - handled by caller
                from .ast_nodes import InputNode
                prompt = None
                type_hint = None
                if self.stream.peek().type == 'LPAREN':
                    self.stream.advance()
                    prompt_tok = self.stream.peek()
                    if prompt_tok.type == 'STRING':
                        prompt = prompt_tok.value
                        self.stream.advance()
                    self.stream.consume_if('RPAREN')
                if (self.stream.peek().type == 'WORD' and
                        self.stream.peek().value.lower() == 'as'):
                    self.stream.advance()
                    type_tok = self.stream.advance()
                    type_hint = type_tok.value.lower()
                return InputNode(prompt=prompt, type_hint=type_hint, line=self.line_no)
            return VariableNode('$input', self.line_no)

        # Words (identifiers, keywords, literals)
        if tok.type == 'WORD':
            word = tok.value.lower()

            # Boolean literals
            if word == 'true':
                self.stream.advance()
                return BoolLiteralNode(True, self.line_no)
            if word == 'false':
                self.stream.advance()
                return BoolLiteralNode(False, self.line_no)

            # null
            if word in ('null', 'none', 'nil'):
                self.stream.advance()
                return NullLiteralNode(self.line_no)

            # pi / e constants
            if word == 'pi':
                self.stream.advance()
                import math
                return NumberLiteralNode(math.pi, self.line_no)
            if word == 'e':
                self.stream.advance()
                import math
                return NumberLiteralNode(math.e, self.line_no)

            # Function call or identifier
            self.stream.advance()
            if self.stream.peek().type == 'LPAREN':
                # Function call
                self.stream.advance()
                args = self._parse_arg_list()
                self.stream.consume_if('RPAREN')
                return CallNode(tok.value, args, self.line_no)

            return VariableNode(tok.value, self.line_no)

        # Negative number special case (unary minus handled above, but
        # sometimes we get here with a minus that is part of a negative literal)
        if tok.type == 'OP' and tok.value == '-':
            self.stream.advance()
            right = self._parse_primary()
            return UnaryOpNode('-', right, self.line_no)

        # Fallback - return null literal
        return NullLiteralNode(self.line_no)

    def _parse_dict_or_set(self) -> Any:
        self.stream.advance()  # consume {
        if self.stream.peek().type == 'RBRACE':
            self.stream.advance()
            return DictLiteralNode([], self.line_no)  # empty dict

        first = self._parse_ternary()
        if self.stream.peek().type == 'COLON':
            # Dict
            self.stream.advance()
            val = self._parse_ternary()
            pairs = [(first, val)]
            while self.stream.consume_if('COMMA'):
                if self.stream.peek().type == 'RBRACE':
                    break
                k = self._parse_ternary()
                self.stream.consume_if('COLON')
                v = self._parse_ternary()
                pairs.append((k, v))
            self.stream.consume_if('RBRACE')
            return DictLiteralNode(pairs, self.line_no)
        else:
            # Set
            elements = [first]
            while self.stream.consume_if('COMMA'):
                if self.stream.peek().type == 'RBRACE':
                    break
                elements.append(self._parse_ternary())
            self.stream.consume_if('RBRACE')
            return SetLiteralNode(elements, self.line_no)

    def _parse_arg_list(self) -> List[Any]:
        args = []
        while self.stream.peek().type not in ('RPAREN', 'EOF'):
            args.append(self._parse_ternary())
            self.stream.consume_if('COMMA')
        return args

    # ── Helper matchers ────────────────────────────────────────

    def _match_word(self, word: str) -> bool:
        tok = self.stream.peek()
        return tok.type == 'WORD' and tok.value.lower() == word.lower()

    def _match_op(self, op: str) -> bool:
        tok = self.stream.peek()
        return tok.type == 'OP' and tok.value == op

    def _peek_words(self, words: List[str]) -> bool:
        for i, w in enumerate(words):
            tok = self.stream.peek(i)
            if tok.type != 'WORD' or tok.value.lower() != w.lower():
                return False
        return True

    def _expect_word(self, word: str):
        tok = self.stream.advance()
        if tok.type != 'WORD' or tok.value.lower() != word.lower():
            raise SyntaxError(f"Expected '{word}' got {tok.value!r}")


# ──────────────────────────────────────────────────────────────
# String interpolation parser
# ──────────────────────────────────────────────────────────────

def _parse_interpolated_string(raw: str, line_no: int) -> Any:
    """
    Parse a string value for {expr} interpolation.
    Returns StringLiteralNode if no interpolation, else InterpolatedStringNode.
    """
    parts = []
    i = 0
    current_text = []
    has_interp = False

    while i < len(raw):
        ch = raw[i]
        if ch == '{':
            # Check it wasn't escaped (already handled in tokenizer via \\{)
            if i + 1 < len(raw) and raw[i+1] == '}':
                # empty braces → literal {}
                current_text.append('{}')
                i += 2
                continue
            # Find matching closing brace
            depth = 1
            j = i + 1
            while j < len(raw) and depth > 0:
                if raw[j] == '{': depth += 1
                elif raw[j] == '}': depth -= 1
                j += 1
            expr_str = raw[i+1:j-1]
            if current_text:
                parts.append(StringLiteralNode(''.join(current_text), line_no))
                current_text = []
            try:
                ep = ExpressionParser(expr_str, line_no)
                expr_node = ep.parse()
            except Exception:
                expr_node = StringLiteralNode(expr_str, line_no)
            parts.append(expr_node)
            has_interp = True
            i = j
        else:
            current_text.append(ch)
            i += 1

    if current_text:
        parts.append(StringLiteralNode(''.join(current_text), line_no))

    if not has_interp:
        return StringLiteralNode(raw, line_no)
    return InterpolatedStringNode(parts, line_no)


# ──────────────────────────────────────────────────────────────
# Convenience function
# ──────────────────────────────────────────────────────────────

def parse_expression(source: str, line_no: int = 0) -> Any:
    """Parse expression string → AST node."""
    ep = ExpressionParser(source.strip(), line_no)
    return ep.parse()


def parse_expression_list(source: str, line_no: int = 0) -> List[Any]:
    """Parse comma-separated expression list → list of AST nodes."""
    # Tokenize and split on top-level commas
    parts = _split_on_top_level_commas(source)
    return [parse_expression(p.strip(), line_no) for p in parts if p.strip()]


def _split_on_top_level_commas(source: str) -> List[str]:
    """Split source on commas that are not inside brackets/parens."""
    parts = []
    depth = 0
    current = []
    for ch in source:
        if ch in ('(', '[', '{'):
            depth += 1
            current.append(ch)
        elif ch in (')', ']', '}'):
            depth -= 1
            current.append(ch)
        elif ch == ',' and depth == 0:
            parts.append(''.join(current))
            current = []
        else:
            current.append(ch)
    if current:
        parts.append(''.join(current))
    return parts
