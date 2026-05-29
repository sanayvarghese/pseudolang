"""
Pass 2 - Mapping Resolver (Section 22.1 of spec).

For each line in the block tree:
  1. Check comment → COMMENT
  2. Check function DEF → FuncDefNode
  3. Check function CALL → FuncCallNode (name in symbol table)
  4. Check builtin CALL → FuncCallNode
  5. Run .pmap trie lookup → canonical AST node
  6. Try expression evaluator → expression node
  7. Nothing matched → ParseError with suggestions

Injects context flags (Section 4.9):
  TOP_LEVEL, FUNCTION_BODY, LOOP_BODY, IF_BODY, CONDITION

Handles complex constructs:
  - if / else if / else chaining
  - try / catch / finally
  - Swap with arr[i] form
"""

from typing import Dict, List, Optional, Tuple, Any
from ..parser.indent_parser import Block, RawLine
from ..parser.normalizer import normalize_content
from ..parser.tokenizer import tokenize, Token
from ..parser.ast_nodes import *
from .pass1_register import SymbolTable, _is_valid_identifier, _KEYWORDS
from ..parser.expr_parser import parse_expression, parse_expression_list, ExpressionParser
from .pmap_loader import PmapLoader, MatchResult


# ──────────────────────────────────────────────────────────────
# Built-in function names (Section 15)
# ──────────────────────────────────────────────────────────────

BUILTIN_FUNCTIONS = frozenset([
    # List
    'len', 'append', 'prepend', 'remove', 'pop', 'insert', 'sort', 'sorted',
    'reverse', 'reversed', 'index', 'find', 'count', 'sum', 'min', 'max',
    'range', 'list', 'copy', 'flatten', 'zip', 'enumerate',
    # String
    'upper', 'lower', 'strip', 'lstrip', 'rstrip', 'split', 'join',
    'replace', 'contains', 'startswith', 'endswith', 'starts_with', 'ends_with',
    'substring', 'char', 'ord', 'chr', 'format', 'trim',
    'isdigit', 'isalpha', 'isalnum', 'str',
    # Math
    'abs', 'round', 'floor', 'ceil', 'sqrt', 'pow', 'power',
    'log', 'log2', 'log10', 'exp',
    'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'atan2',
    'gcd', 'lcm', 'factorial',
    # Type conversion
    'int', 'float', 'bool', 'char_to_int', 'int_to_char',
    # Type checking
    'is_number', 'is_string', 'is_list', 'is_bool', 'is_null', 'type',
    # Utility
    'print', 'input', 'assert',
    # Data structures (constructors)
    'Stack', 'Queue', 'HashMap', 'Set', 'MinHeap', 'MaxHeap',
    'TreeNode', 'ListNode', 'Graph', 'linkedList',
    # Data structure ops
    'push', 'peek', 'isEmpty', 'is_empty', 'size',
    'enqueue', 'dequeue',
    'put', 'get', 'has', 'keys', 'values', 'entries',
    'add', 'union', 'intersection', 'difference',
    'addVertex', 'addEdge', 'neighbors', 'hasEdge', 'vertices',
    'addvertex', 'addedge', 'hasedge',
])


# ──────────────────────────────────────────────────────────────
# Context constants
# ──────────────────────────────────────────────────────────────

CTX_TOP_LEVEL       = 'TOP_LEVEL'
CTX_FUNCTION_BODY   = 'FUNCTION_BODY'
CTX_LOOP_BODY       = 'LOOP_BODY'
CTX_IF_BODY         = 'IF_BODY'
CTX_CONDITION       = 'CONDITION'


# ──────────────────────────────────────────────────────────────
# ParseError
# ──────────────────────────────────────────────────────────────

class ParseError(Exception):
    def __init__(self, message: str, line_no: int, suggestions: List[str] = None):
        super().__init__(message)
        self.line_no = line_no
        self.suggestions = suggestions or []


# ──────────────────────────────────────────────────────────────
# Mapping Resolver
# ──────────────────────────────────────────────────────────────

class MappingResolver:
    """
    Pass 2: resolves each source line to a canonical AST node.
    """

    def __init__(self, symbol_table: SymbolTable, pmap_loader: PmapLoader):
        self.symbol_table = symbol_table
        self.pmap_loader = pmap_loader
        self.line_resolutions: Dict[int, List[str]] = {}

    def resolve_blocks(self, blocks: List[Block], context: str = CTX_TOP_LEVEL) -> List[Any]:
        """Resolve a list of Block objects into AST nodes."""
        result: List[Any] = []
        i = 0
        while i < len(blocks):
            block = blocks[i]
            rl = block.line
            content = normalize_content(rl.content)
            lineno = rl.number

            # Skip blank lines
            if not content:
                i += 1
                continue

            # ── 1. Comment check ─────────────────────────────
            if content.startswith('#'):
                result.append(CommentNode(text=content, line=lineno))
                self.line_resolutions[lineno] = ["↓ Resolution: COMMENT"]
                i += 1
                continue

            # Strip trailing colon and semicolons
            content_clean = content.rstrip(';').rstrip()
            if content_clean.endswith(':'):
                content_clean = content_clean[:-1].rstrip()

            # ── 2. Function DEF check ─────────────────────────
            if block.children:
                func_name, func_params = self._try_parse_func_def(content_clean, lineno)
                if func_name is not None:
                    body = self.resolve_blocks(block.children, CTX_FUNCTION_BODY)
                    result.append(FuncDefNode(
                        name=func_name,
                        params=func_params,
                        body=body,
                        line=lineno
                    ))
                    next_line = block.children[0].line.number if block.children else (lineno + 1)
                    self.line_resolutions[lineno] = [
                        f"↓ Resolution: FUNC_DEF (body follows at line {next_line})"
                    ]
                    i += 1
                    continue

            # ── If / Else chain handling ──────────────────────
            if_node = self._try_parse_if_chain(blocks, i, context)
            if if_node is not None:
                node, consumed = if_node
                result.append(node)
                i += consumed
                continue

            # ── Try/Catch/Finally chain ───────────────────────
            try_node = self._try_parse_try_chain(blocks, i, context)
            if try_node is not None:
                node, consumed = try_node
                result.append(node)
                i += consumed
                continue

            # Resolve single block
            node = self._resolve_single(block, context)
            if node is not None:
                result.append(node)
            i += 1

        return result

    def _resolve_single(self, block: Block, context: str) -> Optional[Any]:
        """Resolve a single block line to an AST node."""
        rl = block.line
        content = normalize_content(rl.content)
        lineno = rl.number

        if not content:
            return None

        # Strip trailing colon/semicolons
        content_clean = content.rstrip(';').rstrip()
        if content_clean.endswith(':'):
            content_clean = content_clean[:-1].rstrip()

        # Tokenize
        tokens = [t for t in tokenize(content_clean, lineno)
                  if t.type not in ('COMMENT', 'SEMICOLON', 'EOF')]
        if not tokens:
            return None

        words = _collapse_dot_chains(tokens)
        words_lower = [w.lower() for w in words]

        # ── 3. Function CALL check ────────────────────────────
        call_result = self._try_parse_call(content_clean, lineno, block.children, context)
        if call_result is not None:
            return call_result

        # ── 3b. Explicit assignment detection ─────────────────
        assign_node = self._try_parse_assignment(content_clean, lineno)
        if assign_node is not None:
            from ..parser.ast_nodes import AssignNode, IndexAssignNode, AttributeAssignNode
            if isinstance(assign_node, AssignNode):
                tokens = [t.value for t in tokenize(content_clean, lineno) if t.type not in ('COMMENT', 'SEMICOLON', 'EOF')]
                if tokens and tokens[0].lower() == 'set':
                    var_name = tokens[1]
                    val_str = ' '.join(tokens[3:])
                elif tokens and tokens[0].lower() == 'let':
                    var_name = tokens[1]
                    val_str = ' '.join(tokens[3:])
                elif tokens and tokens[0].lower() == 'store':
                    var_name = tokens[-1]
                    val_str = ' '.join(tokens[1:-2])
                else:
                    var_name = assign_node.name
                    op_idx = -1
                    for op in (':=', '<-', '='):
                        idx = content_clean.find(op)
                        if idx > 0:
                            if op == '=' and idx + 1 < len(content_clean) and content_clean[idx+1] == '=':
                                continue
                            op_idx = idx + len(op)
                            break
                    val_str = content_clean[op_idx:].strip() if op_idx > 0 else ''
                self.line_resolutions[lineno] = [
                    "↓ Mapping: ASSIGN",
                    f"↓ {'{var:name}':<12} = {var_name!r}",
                    f"↓ {'{value:expr}':<12} = {val_str!r}"
                ]
            elif isinstance(assign_node, IndexAssignNode):
                self.line_resolutions[lineno] = ["↓ Mapping: INDEX_ASSIGN"]
            elif isinstance(assign_node, AttributeAssignNode):
                self.line_resolutions[lineno] = ["↓ Mapping: ATTRIBUTE_ASSIGN"]
            return assign_node

        # ── 4. Builtin call check ─────────────────────────────
        builtin_call = self._try_parse_builtin_call(content_clean, lineno, block.children)
        if builtin_call is not None:
            return builtin_call

        # ── 5. .pmap trie lookup ──────────────────────────────
        pmap_node = self._try_pmap_match(words, words_lower, lineno, block.children, context)
        if pmap_node is not None:
            return pmap_node

        # ── 6. Expression evaluator ───────────────────────────
        try:
            expr = parse_expression(content_clean, lineno)
            if expr is not None:
                return AutoPrintNode(value=expr, line=lineno)
        except Exception:
            pass

        # ── 7. ParseError with suggestions ───────────────────
        suggestions = self._suggest(content_clean)
        raise ParseError(
            f"ParseError: Cannot parse line {lineno}: {content_clean!r}",
            lineno,
            suggestions,
        )

    # ── Assignment detection ───────────────────────────────────

    def _try_parse_assignment(self, content: str, lineno: int) -> Optional[Any]:
        """
        Detect all forms of assignment:
          x = expr, x := expr, x <- expr
          set x to expr, let x be expr, store expr in x
          arr[i] = expr  (index assignment)
        """
        tokens = [t for t in tokenize(content, lineno)
                  if t.type not in ('COMMENT', 'SEMICOLON', 'EOF')]
        if len(tokens) < 3:
            return None

        # Simple: name = / := / <- expr
        if (tokens[0].type == 'WORD' and
                tokens[1].type == 'OP' and tokens[1].value in ('=', ':=', '<-')):
            # Avoid == and >=, <=, !=
            if tokens[1].value == '=' and (
                    len(tokens) > 2 and tokens[2].type == 'OP' and tokens[2].value == '='
            ):
                return None
            name = tokens[0].value
            if name.lower() in _KEYWORDS:
                return None
            val_str = content[content.index(tokens[1].value) + len(tokens[1].value):].lstrip()
            val = parse_expression(val_str, lineno)
            return AssignNode(name=name, value=val, line=lineno)

        # set x to expr
        if (tokens[0].type == 'WORD' and tokens[0].value.lower() == 'set' and
                len(tokens) >= 4 and tokens[1].type == 'WORD' and
                tokens[2].type == 'WORD' and tokens[2].value.lower() == 'to'):
            name = tokens[1].value
            val_str = ' '.join(t.value for t in tokens[3:])
            return AssignNode(name=name, value=parse_expression(val_str, lineno), line=lineno)

        # let x be expr
        if (tokens[0].type == 'WORD' and tokens[0].value.lower() == 'let' and
                len(tokens) >= 4 and tokens[1].type == 'WORD' and
                tokens[2].type == 'WORD' and tokens[2].value.lower() == 'be'):
            name = tokens[1].value
            val_str = ' '.join(t.value for t in tokens[3:])
            return AssignNode(name=name, value=parse_expression(val_str, lineno), line=lineno)

        # store expr in x
        if (tokens[0].type == 'WORD' and tokens[0].value.lower() == 'store' and
                tokens[-1].type == 'WORD' and len(tokens) >= 4 and
                tokens[-2].type == 'WORD' and tokens[-2].value.lower() == 'in'):
            name = tokens[-1].value
            # expression is everything between 'store' and 'in x'
            val_str = content[content.lower().index('store') + 5:].rstrip()
            in_idx = val_str.lower().rfind(' in ')
            if in_idx >= 0:
                val_str = val_str[:in_idx].strip()
            return AssignNode(name=name, value=parse_expression(val_str, lineno), line=lineno)

        # arr[i] = expr - index assignment
        if '[' in content:
            eq_pos = -1
            for op in ('=', ':=', '<-'):
                p = content.find(op)
                if p > 0:
                    # Check not ==
                    if op == '=' and p + 1 < len(content) and content[p+1] == '=':
                        continue
                    if op == '=' and content[p-1] in ('<', '>', '!', ':'):
                        continue
                    eq_pos = p
                    eq_op = op
                    break
            if eq_pos > 0:
                left = content[:eq_pos].rstrip()
                right = content[eq_pos + len(eq_op):].lstrip()
                if '[' in left:
                    try:
                        obj_expr = parse_expression(left, lineno)
                        val_expr = parse_expression(right, lineno)
                        from ..parser.ast_nodes import IndexNode, IndexAssignNode
                        if isinstance(obj_expr, IndexNode):
                            return IndexAssignNode(obj=obj_expr.obj, index=obj_expr.index,
                                                   value=val_expr, line=lineno)
                    except Exception:
                        pass

        # obj.attr = expr - attribute assignment (e.g. root.left = TreeNode(3))
        if '.' in content and '=' in content:
            for op in ('=', ':=', '<-'):
                p = content.find(op)
                if p <= 0:
                    continue
                if op == '=' and p + 1 < len(content) and content[p+1] == '=':
                    continue
                if op == '=' and content[p-1] in ('<', '>', '!', ':'):
                    continue
                left = content[:p].rstrip()
                right = content[p + len(op):].lstrip()
                # Check left is obj.attr form
                dot_pos = left.rfind('.')
                if dot_pos > 0:
                    obj_part = left[:dot_pos].strip()
                    attr_part = left[dot_pos+1:].strip()
                    if _is_valid_identifier(attr_part):
                        try:
                            obj_expr = parse_expression(obj_part, lineno)
                            val_expr = parse_expression(right, lineno)
                            from ..parser.ast_nodes import AttributeAssignNode
                            return AttributeAssignNode(obj=obj_expr, attr=attr_part,
                                                       value=val_expr, line=lineno)
                        except Exception:
                            pass
                break

        return None

    # ── Function DEF detection ─────────────────────────────────

    def _try_parse_func_def(self, content: str, lineno: int):
        """Returns (name, params) or (None, None)."""
        paren_open = content.rfind('(')
        paren_close = content.rfind(')')
        if paren_open == -1 or paren_close < paren_open:
            return None, None
        before_paren = content[:paren_open].rstrip()
        if not before_paren:
            return None, None
        parts = before_paren.split()
        if not parts or len(parts) > 2:
            return None, None
        if len(parts) == 2:
            if parts[0].lower() not in ('def', 'func', 'function', 'define', 'procedure',
                                        'algorithm', 'recursive', 'helper', 'method'):
                return None, None
        func_name = parts[-1]
        if not _is_valid_identifier(func_name):
            return None, None
        if func_name.lower() in _KEYWORDS:
            return None, None
        # Verify this is registered in symbol table
        if not self.symbol_table.has_function(func_name):
            return None, None
        params_str = content[paren_open+1:paren_close].strip()
        params = [p.strip() for p in params_str.split(',') if p.strip()] if params_str else []
        return func_name, params

    # ── Function CALL detection ────────────────────────────────

    def _try_parse_call(self, content: str, lineno: int,
                        children: List[Block], context: str) -> Optional[Any]:
        """Detect a call to a user-defined function."""
        content_stripped = content.rstrip()
        paren_open = content_stripped.find('(')
        paren_close = content_stripped.rfind(')')
        if paren_open == -1 or paren_close != len(content_stripped) - 1:
            return None

        before_paren = content_stripped[:paren_open].rstrip()
        parts = before_paren.split()
        if len(parts) != 1:
            return None

        func_name = parts[0]
        if not _is_valid_identifier(func_name):
            return None
        if not self.symbol_table.has_function(func_name):
            return None

        # No indented body → this is a call
        if not children:
            args_str = content_stripped[paren_open+1:paren_close]
            args = parse_expression_list(args_str, lineno)
            node = FuncCallNode(name=func_name, args=args, line=lineno)
            # Add resolution logging
            if context == CTX_TOP_LEVEL:
                self.line_resolutions[lineno] = [
                    "↓ Resolution: FUNC_CALL (top level → auto-print)"
                ]
            else:
                raw_args = [a.strip() for a in args_str.split(',')] if args_str.strip() else []
                self.line_resolutions[lineno] = [
                    f"↓ Resolution: FUNC_CALL ({func_name} in symbol table)",
                    f"↓ args = {raw_args}"
                ]
            # Top-level bare call → auto-print
            if context in (CTX_TOP_LEVEL, CTX_FUNCTION_BODY, CTX_LOOP_BODY, CTX_IF_BODY):
                # Wrap in AutoPrintNode so the interpreter auto-prints return value
                return AutoPrintNode(value=node, line=lineno)
            return node

        return None

    def _try_parse_builtin_call(self, content: str, lineno: int,
                                 children: List[Block]) -> Optional[Any]:
        """Detect a call to a built-in function."""
        content_stripped = content.rstrip()
        paren_open = content_stripped.find('(')
        paren_close = content_stripped.rfind(')')
        if paren_open == -1 or paren_close != len(content_stripped) - 1:
            return None

        before_paren = content_stripped[:paren_open].rstrip()
        parts = before_paren.split()
        if len(parts) != 1:
            return None

        func_name = parts[0]
        if func_name.lower() not in BUILTIN_FUNCTIONS:
            return None

        args_str = content_stripped[paren_open+1:paren_close]
        args = parse_expression_list(args_str, lineno)
        node = CallNode(name=func_name, args=args, line=lineno)
        _VOID_BUILTINS = frozenset([
            'append', 'prepend', 'remove', 'insert', 'sort', 'reverse',
            'push', 'enqueue', 'add',
            'pop', 'dequeue',
            'put', 'has',  # map ops that return void in statement context
            'addVertex', 'addEdge', 'addvertex', 'addedge',
            'assert',
        ])
        if func_name.lower() in _VOID_BUILTINS:
            return node  # no auto-print wrapper
        return AutoPrintNode(value=node, line=lineno)

    # ── .pmap lookup ────────────────────────────────────────────

    def _try_pmap_match(self, words: List[str], words_lower: List[str],
                        lineno: int, children: List[Block],
                        context: str) -> Optional[Any]:
        """Try matching words against the .pmap trie."""
        if not words:
            return None

        result = self.pmap_loader.match(words, context)
        if result is None:
            return None

        return self._build_ast_from_match(result, lineno, children, context, words)

    def _build_ast_from_match(self, match: MatchResult, lineno: int,
                               children: List[Block], context: str,
                               original_words: List[str]) -> Optional[Any]:
        """Convert a MatchResult to the appropriate AST node."""
        c = match.canonical
        caps = match.captures

        # Record resolution mapping for .pmap match
        res_lines = [f"↓ Mapping: {c}"]
        if match.pattern:
            for tok in match.pattern.tokens:
                if tok.is_placeholder:
                    ph = tok.placeholder
                    val = caps.get(ph.var_name, '').strip()
                    ph_str = f"{{{ph.var_name}:{ph.ph_type}}}"
                    res_lines.append(f"↓ {ph_str:<12} = {val!r}")
        else:
            for k, v in caps.items():
                res_lines.append(f"↓ {k:<12} = {v.strip()!r}")
        self.line_resolutions[lineno] = res_lines

        def get(key: str, default: str = '') -> str:
            return caps.get(key, default).strip()

        # For single-tail expr captures (e.g. print {value:expr}) the pmap
        # stop-token mechanism can truncate the capture at 'not'/'and'/'or'/etc.
        # We fix this by finding what literal tokens the pattern consumed, then
        # re-slicing the original_words from that point onward.
        def _raw_tail_for_last_expr(key: str) -> str:
            """Return the full raw source tail for the last expr-type placeholder."""
            if not match.pattern:
                return get(key)
            ptoks = match.pattern.tokens
            # Find index of the placeholder with this key in the pattern
            ph_idx = None
            for pi, pt in enumerate(ptoks):
                if pt.is_placeholder and pt.placeholder.var_name == key:
                    ph_idx = pi
                    break
            if ph_idx is None:
                return get(key)
            # Is it the last (or only) placeholder with no literals after it?
            has_literal_after = any(
                not ptoks[pp].is_placeholder for pp in range(ph_idx + 1, len(ptoks))
            )
            if has_literal_after:
                return get(key)  # bounded capture, pmap is fine
            # Count how many literal pattern tokens precede this placeholder
            literals_before = [pt for pt in ptoks[:ph_idx] if not pt.is_placeholder]
            # Find where those literals end in the original_words
            start_idx = 0
            for lit in literals_before:
                for wi in range(start_idx, len(original_words)):
                    if original_words[wi].lower() == lit.literal:
                        start_idx = wi + 1
                        break
            tail = ' '.join(original_words[start_idx:])
            return tail if tail.strip() else get(key)

        def parse_expr(key: str) -> Any:
            # Prefer full raw tail for terminal expr placeholders
            if match.pattern:
                ptoks = match.pattern.tokens
                last_expr_ph = None
                for pt in ptoks:
                    if pt.is_placeholder and pt.placeholder.ph_type in ('expr', 'condition', 'collection'):
                        last_expr_ph = pt.placeholder.var_name
                if key == last_expr_ph:
                    s = _raw_tail_for_last_expr(key)
                    return parse_expression(s, lineno) if s.strip() else NullLiteralNode(lineno)
            s = get(key)
            return parse_expression(s, lineno) if s else NullLiteralNode(lineno)

        def parse_body() -> List[Any]:
            return self.resolve_blocks(children, body_context())

        def body_context() -> str:
            if c in ('FOR_LOOP', 'FOR_EACH', 'WHILE_LOOP', 'UNTIL_LOOP'):
                return CTX_LOOP_BODY
            if c in ('IF', 'ELSE_IF', 'ELSE'):
                return CTX_IF_BODY
            return CTX_FUNCTION_BODY

        if c == 'FOR_LOOP':
            var = get('var')
            start = parse_expr('start')
            end = parse_expr('end')
            step_str = get('step')
            step = parse_expression(step_str, lineno) if step_str else NumberLiteralNode(1, lineno)
            return ForLoopNode(var=var, start=start, end=end, step=step,
                               body=parse_body(), line=lineno)

        if c == 'FOR_EACH':
            item = get('item')
            coll = parse_expr('collection')
            return ForEachNode(item=item, collection=coll, body=parse_body(), line=lineno)

        if c == 'WHILE_LOOP':
            # Use full captured condition - but also handle or/and not being stopped
            cond_str = get('condition')
            # Fallback: reconstruct from original_words after first keyword
            if not cond_str or (len(original_words) > 1):
                # Find the end of literal keyword words in the pattern
                from .pmap_loader import _parse_pattern
                n_literals = sum(1 for t in self.pmap_loader._patterns
                                  if t.canonical == 'WHILE_LOOP'
                                  for tok in t.tokens if not tok.is_placeholder
                                  if tok.literal.lower() == original_words[0].lower())
                # Simple heuristic: count leading keyword words
                kw_map = {
                    'while': 1, 'until': 1,
                    'keep': 3,   # keep going while
                    'as': 3,     # as long as
                    'loop': 2,   # loop while
                    'repeat': 2, # repeat while
                }
                skip = kw_map.get(original_words[0].lower(), 1) if original_words else 1
                cond_str = ' '.join(original_words[skip:])
            cond = parse_expression(cond_str, lineno)
            return WhileNode(condition=cond, body=parse_body(), line=lineno)

        if c == 'UNTIL_LOOP':
            kw_map = {'until': 1, 'loop': 2, 'repeat': 2}
            skip = kw_map.get(original_words[0].lower(), 1) if original_words else 1
            cond_str = ' '.join(original_words[skip:])
            cond = parse_expression(cond_str, lineno)
            return UntilNode(condition=cond, body=parse_body(), line=lineno)

        if c == 'IF':
            cond = parse_expr('condition')
            return IfNode(condition=cond, body=parse_body(), line=lineno)

        if c == 'ELSE_IF':
            cond = parse_expr('condition')
            return IfNode(condition=cond, body=parse_body(), line=lineno)

        if c == 'ELSE':
            return IfNode(condition=BoolLiteralNode(True, lineno),
                          body=parse_body(), line=lineno)

        if c == 'RETURN':
            val_str = get('value')
            val = parse_expression(val_str, lineno) if val_str else None
            return ReturnNode(value=val, line=lineno)

        if c == 'BREAK':
            return BreakNode(line=lineno)

        if c == 'CONTINUE':
            return ContinueNode(line=lineno)

        if c == 'ASSIGN':
            var = get('var')
            val = parse_expr('value')
            return AssignNode(name=var, value=val, line=lineno)

        if c == 'PRINT':
            val = parse_expr('value')
            return PrintNode(value=val, line=lineno)

        if c == 'INPUT':
            prompt = get('prompt') or None
            type_hint = get('type') or None
            return InputNode(prompt=prompt, type_hint=type_hint, line=lineno)

        if c == 'TRY':
            return TryNode(body=parse_body(), line=lineno)

        if c == 'CATCH':
            error_name = get('error') or None
            return TryNode(body=[], catch_clauses=[(error_name, parse_body())], line=lineno)

        if c == 'FINALLY':
            return TryNode(body=[], finally_body=parse_body(), line=lineno)

        if c == 'RAISE':
            err_str = get('error')
            err = parse_expression(err_str, lineno) if err_str else StringLiteralNode('Error', lineno)
            return RaiseNode(error=err, line=lineno)

        if c == 'GLOBAL':
            return GlobalNode(name=get('var'), line=lineno)

        if c == 'COMMENT':
            return CommentNode(text=get('text'), line=lineno)

        if c == 'SWAP':
            a_str = get('a')
            b_str = get('b')
            a = parse_expression(a_str, lineno)
            b = parse_expression(b_str, lineno)
            return SwapNode(a=a, b=b, line=lineno)

        if c == 'FUNC_DEF':
            # Handled higher up via block children check
            name = get('name')
            args_str = get('args')
            params = [p.strip() for p in args_str.split(',') if p.strip()] if args_str else []
            return FuncDefNode(name=name, params=params, body=parse_body(), line=lineno)

        if c == 'FUNC_CALL':
            name = get('name')
            args_str = get('args')
            args = parse_expression_list(args_str, lineno) if args_str else []
            return AutoPrintNode(value=FuncCallNode(name=name, args=args, line=lineno), line=lineno)

        # Unknown canonical - try as expression
        return None

    # ── If/Else chain handler ─────────────────────────────────

    def _try_parse_if_chain(self, blocks: List[Block], start: int,
                             context: str) -> Optional[Tuple[Any, int]]:
        """
        Detect and consume an if / else-if / else chain starting at `start`.
        Returns (IfNode, count_consumed) or None.
        """
        block = blocks[start]
        rl = block.line
        content = normalize_content(rl.content).rstrip(';:').rstrip()
        lineno = rl.number
        raw_tokens = [t for t in tokenize(content, lineno)
                      if t.type not in ('COMMENT', 'SEMICOLON', 'EOF')]
        words = _collapse_dot_chains(raw_tokens)
        if not words:
            return None

        w0 = words[0].lower()
        if w0 not in ('if', 'when', 'check', 'given'):
            return None

        # Extract condition as FULL text after first keyword
        # Reconstruct from re-quoted words to preserve string literals
        keyword_words = 1
        cond_str = ' '.join(words[keyword_words:])
        try:
            cond = parse_expression(cond_str, lineno)
        except Exception:
            # Last-resort: use raw content substring
            kw_end = content.find(words[0]) + len(words[0])
            cond_str = content[kw_end:].strip()
            cond = parse_expression(cond_str, lineno)

        body = self.resolve_blocks(block.children, CTX_IF_BODY)
        self.line_resolutions[lineno] = [
            "↓ Mapping: IF",
            f"↓ {'{condition:expr}':<12} = {cond_str!r}"
        ]

        # Collect else-if and else branches
        elif_clauses: List[Tuple[Any, List[Any]]] = []
        else_body: Optional[List[Any]] = None
        consumed = 1

        while start + consumed < len(blocks):
            next_block = blocks[start + consumed]
            nc = normalize_content(next_block.line.content).rstrip(';:').rstrip()
            nc_raw = [t for t in tokenize(nc, next_block.line.number)
                      if t.type not in ('COMMENT', 'SEMICOLON', 'EOF')]
            nc_words = _collapse_dot_chains(nc_raw)
            if not nc_words:
                break

            w = nc_words[0].lower()

            # else if / elif / otherwise when / or if
            if _is_else_if(nc_words):
                # extract condition as full text after the keyword(s)
                w0, w1 = nc_words[0].lower(), (nc_words[1].lower() if len(nc_words) > 1 else '')
                if w0 in ('else', 'or') and w1 in ('if', 'when'):
                    skip = 2
                elif w0 == 'otherwise' and w1 in ('if', 'when'):
                    skip = 2
                elif w0 == 'elif':
                    skip = 1
                else:
                    skip = 2
                el_cond_str = ' '.join(nc_words[skip:])
                el_cond = parse_expression(el_cond_str, next_block.line.number)
                el_body = self.resolve_blocks(next_block.children, CTX_IF_BODY)
                elif_clauses.append((el_cond, el_body))
                self.line_resolutions[next_block.line.number] = [
                    "↓ Mapping: ELSE_IF",
                    f"↓ {'{condition:expr}':<12} = {el_cond_str!r}"
                ]
                consumed += 1
                continue

            # else / otherwise / if not
            if _is_else(nc_words):
                else_body = self.resolve_blocks(next_block.children, CTX_IF_BODY)
                self.line_resolutions[next_block.line.number] = [
                    "↓ Mapping: ELSE"
                ]
                consumed += 1
                break

            break

        return (IfNode(condition=cond, body=body,
                       elif_clauses=elif_clauses,
                       else_body=else_body,
                       line=lineno), consumed)

    # ── Try/Catch/Finally handler ──────────────────────────────

    def _try_parse_try_chain(self, blocks: List[Block], start: int,
                              context: str) -> Optional[Tuple[Any, int]]:
        block = blocks[start]
        content = normalize_content(block.line.content).rstrip(';:').rstrip()
        words = [t.value for t in tokenize(content, block.line.number)
                 if t.type not in ('COMMENT', 'SEMICOLON', 'EOF')]
        if not words:
            return None
        w0 = words[0].lower()
        if w0 not in ('try', 'attempt'):
            return None

        try_body = self.resolve_blocks(block.children, context)
        self.line_resolutions[block.line.number] = ["↓ Mapping: TRY"]
        catch_clauses: List[Tuple[Optional[str], List[Any]]] = []
        finally_body: Optional[List[Any]] = None
        consumed = 1

        while start + consumed < len(blocks):
            nb = blocks[start + consumed]
            nc = normalize_content(nb.line.content).rstrip(';:').rstrip()
            nc_raw = [t for t in tokenize(nc, nb.line.number)
                      if t.type not in ('COMMENT', 'SEMICOLON', 'EOF')]
            nc_words = _collapse_dot_chains(nc_raw)
            if not nc_words:
                break
            w = nc_words[0].lower()

            if w in ('catch', 'except', 'if', 'on') or (
                    w == 'if' and len(nc_words) > 1 and nc_words[1].lower() in ('error', 'fails')):
                # Catch with optional error type
                error_type = None
                if len(nc_words) > 1:
                    last = nc_words[-1]
                    if _is_valid_identifier(last) and last[0].isupper():
                        error_type = last
                    elif len(nc_words) >= 3 and nc_words[1].lower() not in ('error', 'fail', 'fails'):
                        error_type = nc_words[-1]
                cb = self.resolve_blocks(nb.children, context)
                catch_clauses.append((error_type, cb))
                if error_type:
                    self.line_resolutions[nb.line.number] = [
                        "↓ Mapping: CATCH",
                        f"↓ {'{error:type}':<12} = {error_type!r}"
                    ]
                else:
                    self.line_resolutions[nb.line.number] = ["↓ Mapping: CATCH"]
                consumed += 1
                continue

            if w in ('finally', 'always', 'cleanup'):
                finally_body = self.resolve_blocks(nb.children, context)
                self.line_resolutions[nb.line.number] = ["↓ Mapping: FINALLY"]
                consumed += 1
                break

            break

        return (TryNode(body=try_body, catch_clauses=catch_clauses,
                        finally_body=finally_body, line=block.line.number), consumed)

    # ── Suggestions ───────────────────────────────────────────

    def _suggest(self, content: str) -> List[str]:
        words = content.lower().split()
        suggestions = []
        if words:
            w = words[0]
            SUGGESTION_MAP = {
                'traverse': '"for each item in list" → FOR_EACH',
                'go': '"for i from 0 to n" → FOR_LOOP',
                'loop': '"while condition" → WHILE_LOOP',
                'output': '"print value" → PRINT',
            }
            if w in SUGGESTION_MAP:
                suggestions.append(SUGGESTION_MAP[w])
        return suggestions


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────

def _is_else_if(words: List[str]) -> bool:
    if not words:
        return False
    w = [w.lower() for w in words]
    if w[0] == 'else' and len(w) > 1 and w[1] == 'if':
        return True
    if w[0] == 'elif':
        return True
    if w[0] == 'otherwise' and len(w) > 1 and w[1] in ('when', 'if'):
        return True
    if w[0] == 'or' and len(w) > 1 and w[1] == 'if':
        return True
    return False


def _is_else(words: List[str]) -> bool:
    if not words:
        return False
    w = [w.lower() for w in words]
    if w[0] == 'else':
        return True
    if w[0] == 'otherwise' and (len(w) == 1 or w[1] not in ('when', 'if')):
        return True
    if len(w) >= 2 and w[0] == 'if' and w[1] == 'not':
        return True
    return False


# ──────────────────────────────────────────────────────────────
# Index assignment detection (arr[i] = value)
# ──────────────────────────────────────────────────────────────

def try_parse_index_assign(content: str, lineno: int) -> Optional[IndexAssignNode]:
    """
    Detect patterns like:
      arr[i] = value
      arr[i] := value
    """
    # Find assignment operator
    for op in ('=', ':='):
        idx = content.find(op)
        if idx == -1:
            continue
        # Avoid ==
        if op == '=' and idx + 1 < len(content) and content[idx+1] == '=':
            continue
        if op == '=' and idx > 0 and content[idx-1] in ('<', '>', '!', ':'):
            continue
        left = content[:idx].rstrip()
        right = content[idx+len(op):].lstrip()
        # Check if left contains [
        if '[' in left:
            try:
                obj_node = parse_expression(left, lineno)
                val_node = parse_expression(right, lineno)
                if isinstance(obj_node, IndexNode):
                    return IndexAssignNode(obj=obj_node.obj, index=obj_node.index,
                                          value=val_node, line=lineno)
            except Exception:
                pass
    return None


# ──────────────────────────────────────────────────────────────
# Token utility helpers
# ──────────────────────────────────────────────────────────────

def _collapse_dot_chains(tokens) -> List[str]:
    """
    Collapse sequences like WORD DOT WORD DOT WORD into a single 'word.word.word' token.
    This prevents attribute names (next, val, left, right, skip...) from being treated as
    pmap stop-tokens during expression placeholder capture.
    STRING tokens are re-quoted to preserve their literal form.
    """
    result = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        # Start of possible dot chain: WORD followed by DOT followed by WORD
        if (t.type == 'WORD' and
                i + 2 < len(tokens) and
                tokens[i + 1].type == 'DOT' and
                tokens[i + 2].type == 'WORD'):
            chain = t.value
            while (i + 1 < len(tokens) and tokens[i + 1].type == 'DOT' and
                   i + 2 < len(tokens) and tokens[i + 2].type == 'WORD'):
                chain += '.' + tokens[i + 2].value
                i += 2
            result.append(chain)
        elif t.type == 'STRING':
            result.append(f'"{t.value}"')
        else:
            result.append(t.value)
        i += 1
    return result
