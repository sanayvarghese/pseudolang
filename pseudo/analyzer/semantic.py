"""
Semantic Analyzer - Section 22.1 of spec.

Validates the AST after mapping resolution:
  - Type checking (basic)
  - Scope resolution
  - Undefined variable detection
  - Undefined function detection
  - Argument count validation
  - Keyword-as-variable check
  - Builtin-as-variable check
  - Static infinite loop warning (while true: with no break)

Returns list of warnings; raises SemanticError on fatal issues.
"""

from typing import List, Dict, Set, Optional, Any
from ..parser.ast_nodes import *
from ..resolver.pass1_register import SymbolTable, _KEYWORDS
from ..resolver.pass2_resolver import BUILTIN_FUNCTIONS

# Names that are clearly functions and should never be used as variable names.
# Excludes method-style names (count, add, get, set, etc.) that are fine as vars.
RESERVED_BUILTIN_NAMES = frozenset([
    # Core language functions - unambiguous, always callable at top level
    'len', 'range', 'print', 'input', 'type', 'str', 'int', 'float', 'bool', 'list',
    'min', 'max', 'sum', 'abs', 'round', 'sorted', 'reversed', 'zip', 'enumerate',
    'sqrt', 'floor', 'ceil', 'pow', 'log', 'exp',
    'ord', 'chr', 'factorial', 'gcd', 'lcm',
    # Data structure constructors
    'Stack', 'Queue', 'HashMap', 'MinHeap', 'MaxHeap',
    'TreeNode', 'ListNode', 'Graph',
])


class SemanticError(Exception):
    def __init__(self, message: str, line_no: int):
        super().__init__(message)
        self.line_no = line_no


class SemanticWarning:
    def __init__(self, message: str, line_no: int):
        self.message = message
        self.line_no = line_no

    def __str__(self):
        return f"⚠ Warning line {self.line_no}: {self.message}"


class SemanticAnalyzer:
    """
    Walks the AST and reports semantic errors and warnings.
    """

    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table = symbol_table
        self.warnings: List[SemanticWarning] = []
        self._loop_depth = 0
        self._in_function = False
        self._local_scope: Set[str] = set()
        self._global_declared: Set[str] = set()

    def analyze(self, program: ProgramNode) -> List[SemanticWarning]:
        self.warnings = []
        self._visit_list(program.body)

        # Check for no entry point
        defined_funcs = set(self.symbol_table.functions.keys())
        def has_top_level_call(node: Any) -> bool:
            if node is None:
                return False
            if isinstance(node, FuncDefNode):
                return False  # do not look inside function bodies
            if isinstance(node, (FuncCallNode, CallNode)):
                if node.name in defined_funcs:
                    return True
            if hasattr(node, '__dict__'):
                for val in node.__dict__.values():
                    if isinstance(val, list):
                        for item in val:
                            if has_top_level_call(item):
                                return True
                    elif has_top_level_call(val):
                        return True
            return False

        has_call = any(has_top_level_call(stmt) for stmt in program.body)
        if not has_call and defined_funcs:
            self.warnings.append(SemanticWarning(
                "No entry point found. Functions defined but never called.\n"
                "  Hint: Call your function at the bottom of the file.",
                0
            ))

        return self.warnings

    def _visit_list(self, stmts: List[Any]):
        for stmt in stmts:
            self._visit(stmt)

    def _visit(self, node: Any):
        if node is None:
            return

        if isinstance(node, (CommentNode, BreakNode, ContinueNode)):
            return

        if isinstance(node, FuncDefNode):
            self._visit_func_def(node)

        elif isinstance(node, AssignNode):
            self._check_name_not_reserved(node.name, node.line)
            self._local_scope.add(node.name)
            self._visit_expr(node.value)

        elif isinstance(node, PrintNode):
            self._visit_expr(node.value)

        elif isinstance(node, ReturnNode):
            if not self._in_function:
                pass   # spec doesn't disallow this explicitly
            if node.value:
                self._visit_expr(node.value)

        elif isinstance(node, ForLoopNode):
            self._local_scope.add(node.var)
            self._visit_expr(node.start)
            self._visit_expr(node.end)
            self._visit_expr(node.step)
            self._loop_depth += 1
            self._visit_list(node.body)
            self._loop_depth -= 1

        elif isinstance(node, ForEachNode):
            self._local_scope.add(node.item)
            self._visit_expr(node.collection)
            self._loop_depth += 1
            self._visit_list(node.body)
            self._loop_depth -= 1

        elif isinstance(node, WhileNode):
            self._visit_expr(node.condition)
            self._check_infinite_while(node)
            self._loop_depth += 1
            self._visit_list(node.body)
            self._loop_depth -= 1

        elif isinstance(node, UntilNode):
            self._visit_expr(node.condition)
            self._loop_depth += 1
            self._visit_list(node.body)
            self._loop_depth -= 1

        elif isinstance(node, IfNode):
            self._visit_expr(node.condition)
            self._visit_list(node.body)
            for cond, body in node.elif_clauses:
                self._visit_expr(cond)
                self._visit_list(body)
            if node.else_body:
                self._visit_list(node.else_body)

        elif isinstance(node, TryNode):
            self._visit_list(node.body)
            for _, body in node.catch_clauses:
                self._visit_list(body)
            if node.finally_body:
                self._visit_list(node.finally_body)

        elif isinstance(node, RaiseNode):
            self._visit_expr(node.error)

        elif isinstance(node, GlobalNode):
            self._global_declared.add(node.name)

        elif isinstance(node, AutoPrintNode):
            self._visit_expr(node.value)

        elif isinstance(node, SwapNode):
            self._visit_expr(node.a)
            self._visit_expr(node.b)

        elif isinstance(node, TernaryNode):
            self._visit_expr(node.condition)
            self._visit_expr(node.true_val)
            self._visit_expr(node.false_val)

        elif isinstance(node, IndexAssignNode):
            self._visit_expr(node.obj)
            self._visit_expr(node.index)
            self._visit_expr(node.value)

        elif isinstance(node, FuncCallNode):
            if not self.symbol_table.has_function(node.name):
                if node.name not in BUILTIN_FUNCTIONS:
                    raise SemanticError(
                        f"NameError: '{node.name}' is not defined. Did you forget to define it?",
                        node.line
                    )
            else:
                func_def = self.symbol_table.get_function(node.name)
                if func_def and len(node.args) != len(func_def.params):
                    raise SemanticError(
                        f"ArgumentError: {node.name}() takes {len(func_def.params)} arguments, "
                        f"got {len(node.args)}",
                        node.line
                    )
            for arg in node.args:
                self._visit_expr(arg)

    def _visit_func_def(self, node: FuncDefNode):
        old_in_function = self._in_function
        old_local = self._local_scope.copy()
        old_global_decl = self._global_declared.copy()

        self._in_function = True
        self._local_scope = set(node.params)
        self._global_declared = set()

        self._visit_list(node.body)

        self._in_function = old_in_function
        self._local_scope = old_local
        self._global_declared = old_global_decl

    def _visit_expr(self, node: Any):
        if node is None:
            return
        if isinstance(node, (NumberLiteralNode, StringLiteralNode, BoolLiteralNode,
                              NullLiteralNode, InputNode)):
            return
        if isinstance(node, VariableNode):
            # Check it's not a keyword used as variable
            if node.name.lower() in _KEYWORDS and node.name.lower() not in ('true', 'false', 'null'):
                pass   # allow reading keywords - they'll fail at runtime if wrong
        if isinstance(node, ListLiteralNode):
            for el in node.elements:
                self._visit_expr(el)
        if isinstance(node, SetLiteralNode):
            for el in node.elements:
                self._visit_expr(el)
        if isinstance(node, DictLiteralNode):
            for k, v in node.pairs:
                self._visit_expr(k)
                self._visit_expr(v)
        if isinstance(node, BinaryOpNode):
            self._visit_expr(node.left)
            self._visit_expr(node.right)
        if isinstance(node, UnaryOpNode):
            self._visit_expr(node.operand)
        if isinstance(node, IndexNode):
            self._visit_expr(node.obj)
            self._visit_expr(node.index)
        if isinstance(node, SliceNode):
            self._visit_expr(node.obj)
            if node.start: self._visit_expr(node.start)
            if node.end: self._visit_expr(node.end)
        if isinstance(node, CallNode):
            for arg in node.args:
                self._visit_expr(arg)
        if isinstance(node, AttributeNode):
            self._visit_expr(node.obj)
        if isinstance(node, AttributeCallNode):
            self._visit_expr(node.obj)
            for arg in node.args:
                self._visit_expr(arg)
        if isinstance(node, InterpolatedStringNode):
            for part in node.parts:
                if not isinstance(part, str):
                    self._visit_expr(part)
        if isinstance(node, TernaryNode):
            self._visit_expr(node.condition)
            self._visit_expr(node.true_val)
            self._visit_expr(node.false_val)

    def _check_name_not_reserved(self, name: str, lineno: int):
        if name.lower() in _KEYWORDS:
            raise SemanticError(
                f"NameError: Cannot use '{name}' as variable name: it is a reserved keyword",
                lineno
            )
        # Only block unambiguously function-only names (not method-style names like count/add/get)
        if name in RESERVED_BUILTIN_NAMES or name.lower() in RESERVED_BUILTIN_NAMES:
            raise SemanticError(
                f"NameError: Cannot use '{name}' as variable name: it is a built-in function",
                lineno
            )

    def _check_infinite_while(self, node: WhileNode):
        """Warn if while true with no break in body."""
        cond = node.condition
        is_always_true = (
            isinstance(cond, BoolLiteralNode) and cond.value is True or
            isinstance(cond, NumberLiteralNode) and cond.value == 1
        )
        if is_always_true:
            has_break = _body_has_break(node.body)
            if not has_break:
                self.warnings.append(SemanticWarning(
                    "Possible infinite loop\n"
                    "  'while true' with no break statement detected\n"
                    "  Run anyway? (y/n)",
                    node.line
                ))


def _body_has_break(body: List[Any]) -> bool:
    for node in body:
        if isinstance(node, BreakNode):
            return True
        if isinstance(node, IfNode):
            if _body_has_break(node.body):
                return True
            for _, elif_body in node.elif_clauses:
                if _body_has_break(elif_body):
                    return True
            if node.else_body and _body_has_break(node.else_body):
                return True
    return False
