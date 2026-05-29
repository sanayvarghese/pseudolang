"""Complexity analysis engine - Section 18.

Supports:
  O(1), O(log n), O(n), O(n log n), O(n²), O(n³), O(nᵏ), O(2ⁿ), O(n!)

Detection rules (from spec §18.3):
  Loop nesting → O(nᵏ) for k-deep loops over input
  Binary search while-loop pattern → O(log n)
  Linear recursion f(n-1) → O(n)
  Double/exponential recursion f(n-1)+f(n-2) → O(2ⁿ)
  Halving recursion f(n/2) → O(log n)
  Halving recursion + O(n) loop inside → O(n log n)
  Space: fixed vars → O(1), new array → O(n), linear rec stack → O(n),
         halving rec stack → O(log n), matrix → O(n²)
"""

from typing import Any, Dict, List, Optional, Tuple, Set
from ..parser.ast_nodes import *


# ── Complexity representation ──────────────────────────────────

class Complexity:
    def __init__(self, time_: str = 'O(1)', space: str = 'O(1)',
                 time_reason: str = '', space_reason: str = ''):
        self.time = time_
        self.space = space
        self.time_reason = time_reason
        self.space_reason = space_reason


ORDERS = [
    'O(1)', 'O(log n)', 'O(n)', 'O(n log n)',
    'O(n²)', 'O(n³)', 'O(2ⁿ)', 'O(n!)'
]

def _rank(c: str) -> int:
    try:
        return ORDERS.index(c)
    except ValueError:
        return 2  # default to O(n) for unknown

def _worse(a: str, b: str) -> str:
    return a if _rank(a) >= _rank(b) else b

def _combine_loop(outer: str, inner: str) -> str:
    """Multiply two complexities for nested loops."""
    if inner == 'O(1)':
        return outer
    rank_map = {c: i for i, c in enumerate(ORDERS)}
    o = rank_map.get(outer, 2)
    i = rank_map.get(inner, 0)
    # Combine: O(n)*O(n)=O(n²), O(n)*O(n²)=O(n³), O(n)*O(log n)=O(n log n)
    combos = {
        ('O(n)',     'O(n)'):      'O(n²)',
        ('O(n)',     'O(n²)'):     'O(n³)',
        ('O(n)',     'O(log n)'): 'O(n log n)',
        ('O(n)',     'O(n log n)'): 'O(n²)',   # conservative
        ('O(n²)',    'O(n)'):      'O(n³)',
        ('O(log n)', 'O(n)'):     'O(n log n)',
        ('O(log n)', 'O(log n)'): 'O(log n)',
    }
    result = combos.get((outer, inner))
    if result:
        return result
    # Fallback: pick worse
    return ORDERS[min(o + i, len(ORDERS) - 1)]


# ── Recursion pattern detection ────────────────────────────────

def _expr_subtracts_one(node: Any, param: str) -> bool:
    """True if node looks like param - 1 (linear recursion step)."""
    if isinstance(node, BinaryOpNode) and node.op == '-':
        if isinstance(node.left, VariableNode) and node.left.name == param:
            if isinstance(node.right, NumberLiteralNode) and node.right.value in (1, 2):
                return True
    return False

def _expr_halves(node: Any, param: str) -> bool:
    """True if node looks like param // 2 or (a + b) // 2 or param / 2."""
    if isinstance(node, BinaryOpNode) and node.op in ('//', '/'):
        if isinstance(node.right, NumberLiteralNode) and node.right.value == 2:
            return True  # something // 2
    return False

def _count_recursive_calls(body: List[Any], func_name: str) -> int:
    """Count how many times func_name is directly called in body (shallow)."""
    count = 0
    for stmt in body:
        count += _count_calls_in_node(stmt, func_name)
    return count

def _count_calls_in_node(node: Any, func_name: str) -> int:
    if node is None:
        return 0
    total = 0
    if isinstance(node, (FuncCallNode, CallNode)) and node.name == func_name:
        total += 1
        for a in node.args:
            total += _count_calls_in_node(a, func_name)
        return total  # count this call + recursive in args
    if isinstance(node, AssignNode):
        total += _count_calls_in_node(node.value, func_name)
    elif isinstance(node, ReturnNode) and node.value:
        total += _count_calls_in_node(node.value, func_name)
    elif isinstance(node, PrintNode):
        total += _count_calls_in_node(node.value, func_name)
    elif isinstance(node, IfNode):
        for s in node.body: total += _count_calls_in_node(s, func_name)
        for _, b in node.elif_clauses:
            for s in b: total += _count_calls_in_node(s, func_name)
        if node.else_body:
            for s in node.else_body: total += _count_calls_in_node(s, func_name)
    elif isinstance(node, (ForLoopNode, ForEachNode, WhileNode, UntilNode)):
        for s in node.body: total += _count_calls_in_node(s, func_name)
    elif isinstance(node, BinaryOpNode):
        total += _count_calls_in_node(node.left, func_name)
        total += _count_calls_in_node(node.right, func_name)
    elif isinstance(node, (FuncCallNode, CallNode)):
        for a in node.args: total += _count_calls_in_node(a, func_name)
    elif isinstance(node, AutoPrintNode):
        total += _count_calls_in_node(node.value, func_name)
    elif isinstance(node, TernaryNode):
        total += _count_calls_in_node(node.condition, func_name)
        total += _count_calls_in_node(node.true_val, func_name)
        total += _count_calls_in_node(node.false_val, func_name)
    return total

def _call_args_halve(node: Any, func_name: str, param: str) -> bool:
    """Check if a recursive call to func_name uses param // 2 or similar."""
    if isinstance(node, (FuncCallNode, CallNode)) and node.name == func_name:
        return any(_expr_halves(a, param) for a in node.args)
    if isinstance(node, BinaryOpNode):
        return _call_args_halve(node.left, func_name, param) or \
               _call_args_halve(node.right, func_name, param)
    if isinstance(node, ReturnNode) and node.value:
        return _call_args_halve(node.value, func_name, param)
    if isinstance(node, AssignNode):
        return _call_args_halve(node.value, func_name, param)
    if isinstance(node, IfNode):
        return any(_call_args_halve(s, func_name, param) for s in node.body)
    if isinstance(node, TernaryNode):
        return (_call_args_halve(node.condition, func_name, param) or
                _call_args_halve(node.true_val, func_name, param) or
                _call_args_halve(node.false_val, func_name, param))
    return False

def _has_halving_call(body: List[Any], func_name: str, params: List[str]) -> bool:
    """Does the function body contain a call to itself with n/2 argument?"""
    for param in params:
        for stmt in body:
            if _call_args_halve(stmt, func_name, param):
                return True
    return False

def _body_has_on_loop(body: List[Any]) -> bool:
    """Does the body contain a for/foreach loop that is O(n)?"""
    for stmt in body:
        if isinstance(stmt, (ForLoopNode, ForEachNode)):
            end = getattr(stmt, 'end', None)
            if not isinstance(end, NumberLiteralNode):
                return True  # non-fixed bound = O(n)
        if isinstance(stmt, IfNode):
            if _body_has_on_loop(stmt.body):
                return True
    return False


def _expr_divides_var(expr: Any, var_name: str) -> bool:
    if expr is None:
        return False
    if isinstance(expr, BinaryOpNode) and expr.op in ('/', '//', '>>'):
        if isinstance(expr.left, VariableNode) and expr.left.name == var_name:
            if isinstance(expr.right, NumberLiteralNode):
                limit = 1 if expr.op == '>>' else 1
                if expr.right.value > limit:
                    return True
    if isinstance(expr, (CallNode, FuncCallNode)) and expr.name in ('floor', 'int', 'round', 'ceil'):
        if expr.args and _expr_divides_var(expr.args[0], var_name):
            return True
    return False


# ── Main analyzer ──────────────────────────────────────────────

class ComplexityEngine:
    def analyze(self, program: ProgramNode) -> Dict[str, Complexity]:
        """Returns {func_name: Complexity} plus 'Overall'."""
        results = {}
        for node in program.body:
            if isinstance(node, FuncDefNode):
                results[node.name] = self._analyze_func(node)

        if results:
            overall_time  = max(
                (c.time  for c in results.values()),
                key=lambda t: _rank(t)
            )
            overall_space = max(
                (c.space for c in results.values()),
                key=lambda s: _rank(s)
            )
            results['Overall'] = Complexity(overall_time, overall_space)

        return results

    def _analyze_func(self, node: FuncDefNode) -> Complexity:
        time_c, time_r   = self._analyze_body_time(node.body, depth=0,
                                                     func_name=node.name,
                                                     params=node.params)
        space_c, space_r = self._analyze_space(node)
        return Complexity(time_c, space_c, time_r, space_r)

    # ── Time complexity ────────────────────────────────────────

    def _analyze_body_time(self, body: List[Any], depth: int,
                           func_name: str = '', params: List[str] = None
                           ) -> Tuple[str, str]:
        best = 'O(1)'
        reasons = []
        params = params or []

        for node in body:
            t, r = self._analyze_stmt_time(node, depth, func_name, params)
            best = _worse(best, t)
            if r:
                reasons.append(r)

        return best, '\n'.join(reasons)

    def _analyze_stmt_time(self, node: Any, depth: int,
                           func_name: str, params: List[str]
                           ) -> Tuple[str, str]:
        indent = '  ' * depth

        if isinstance(node, ForLoopNode):
            return self._analyze_for_loop(node, depth, func_name, params)

        if isinstance(node, ForEachNode):
            inner_t, inner_r = self._analyze_body_time(node.body, depth + 1, func_name, params)
            combined = _combine_loop('O(n)', inner_t)
            reason = f"{indent}for each {node.item} → O(n) × {inner_t} = {combined}"
            return combined, reason

        if isinstance(node, WhileNode):
            return self._analyze_while(node, depth, func_name, params)

        if isinstance(node, UntilNode):
            if self._is_binary_search_pattern(node.body) or self._is_logarithmic_loop(node, params):
                combined = 'O(log n)'
                inner_t = 'O(1)'
            else:
                inner_t, _ = self._analyze_body_time(node.body, depth + 1, func_name, params)
                combined = _combine_loop('O(n)', inner_t)
            reason = f"{indent}until loop → {combined}"
            return combined, reason

        if isinstance(node, IfNode):
            t, r = self._analyze_body_time(node.body, depth, func_name, params)
            for _, body in node.elif_clauses:
                t2, r2 = self._analyze_body_time(body, depth, func_name, params)
                t = _worse(t, t2)
            if node.else_body:
                t2, _ = self._analyze_body_time(node.else_body, depth, func_name, params)
                t = _worse(t, t2)
            return t, r

        if isinstance(node, TryNode):
            t, r = self._analyze_body_time(node.body, depth, func_name, params)
            return t, r

        if isinstance(node, ReturnNode) and node.value:
            return self._analyze_expr_time(node.value, func_name, params, depth)

        if isinstance(node, AssignNode):
            return self._analyze_expr_time(node.value, func_name, params, depth)

        if isinstance(node, AutoPrintNode):
            return self._analyze_expr_time(node.value, func_name, params, depth)

        if isinstance(node, PrintNode):
            return self._analyze_expr_time(node.value, func_name, params, depth)

        return 'O(1)', ''

    def _analyze_expr_time(self, node: Any, func_name: str, params: List[str],
                           depth: int) -> Tuple[str, str]:
        """Detect recursion patterns inside expressions."""
        if node is None:
            return 'O(1)', ''

        # Direct recursive call
        if isinstance(node, (FuncCallNode, CallNode)) and node.name == func_name:
            return self._classify_recursive_call(node, func_name, params, depth)

        # BinaryOp containing recursive calls (e.g. f(n-1) + f(n-2))
        if isinstance(node, BinaryOpNode):
            left_calls  = _count_calls_in_node(node.left, func_name)
            right_calls = _count_calls_in_node(node.right, func_name)
            total_calls = left_calls + right_calls
            if total_calls >= 2:
                # Double recursion: O(2ⁿ)
                return 'O(2ⁿ)', f"{'  '*depth}double recursion {func_name}() → O(2ⁿ)"
            if total_calls == 1:
                t1, r1 = self._analyze_expr_time(node.left, func_name, params, depth)
                t2, r2 = self._analyze_expr_time(node.right, func_name, params, depth)
                return _worse(t1, t2), r1 or r2

        return 'O(1)', ''

    def _classify_recursive_call(self, node: Any, func_name: str,
                                  params: List[str], depth: int) -> Tuple[str, str]:
        """Determine recursion complexity from call arguments."""
        indent = '  ' * depth
        for arg in node.args:
            if _expr_halves(arg, params[0] if params else ''):
                return 'O(log n)', f"{indent}halving recursion {func_name}() → O(log n)"
            if _expr_subtracts_one(arg, params[0] if params else ''):
                return 'O(n)', f"{indent}linear recursion {func_name}() → O(n)"
        return 'O(n)', f"{indent}recursion {func_name}() → O(n)"

    def _analyze_for_loop(self, node: ForLoopNode, depth: int,
                          func_name: str, params: List[str]) -> Tuple[str, str]:
        indent = '  ' * depth
        end = node.end
        if isinstance(end, NumberLiteralNode):
            bound = 'O(1)'
            bound_str = f'fixed bound {end.value}'
        elif self._is_binary_search_pattern(node.body):
            bound = 'O(log n)'
            bound_str = 'binary search inner'
        else:
            bound = 'O(n)'
            bound_str = 'input-dependent bound'

        inner_t, inner_r = self._analyze_body_time(node.body, depth + 1, func_name, params)
        combined = _combine_loop(bound, inner_t)
        reason = (f"{indent}for {node.var} from ... to ... → {bound}\n"
                  f"{indent}  └─ {inner_r}" if inner_r else
                  f"{indent}for {node.var} → {bound} → combined {combined}")
        return combined, reason

    def _analyze_while(self, node: WhileNode, depth: int,
                       func_name: str, params: List[str]) -> Tuple[str, str]:
        indent = '  ' * depth
        if self._is_binary_search_pattern(node.body) or self._is_logarithmic_loop(node, params):
            combined = 'O(log n)'
            inner_t = 'O(1)'
        else:
            inner_t, _ = self._analyze_body_time(node.body, depth + 1, func_name, params)
            combined = _combine_loop('O(n)', inner_t)
        reason = f"{indent}while loop → {combined}"
        return combined, reason

    # ── Space complexity ───────────────────────────────────────

    def _analyze_space(self, node: FuncDefNode) -> Tuple[str, str]:
        """Analyze space: array allocs + recursion call stack + collections."""
        space = 'O(1)'
        reasons = []

        # Recursive call stack space
        rec_space, rec_reason = self._recursion_space(node)
        if rec_reason:
            space = _worse(space, rec_space)
            reasons.append(rec_reason)

        # Array allocations
        arr_space, arr_reasons = self._allocation_space(node.body, node.params)
        space = _worse(space, arr_space)
        reasons.extend(arr_reasons)

        # Collection growth heuristics
        coll_space, coll_reasons = self._analyze_collection_space(node.body, node.name, node.params)
        space = _worse(space, coll_space)
        reasons.extend(coll_reasons)

        return space, '\n'.join(reasons)

    def _recursion_space(self, node: FuncDefNode) -> Tuple[str, str]:
        """Determine call-stack space from recursion type."""
        func_name = node.name
        params = node.params

        total_calls = _count_recursive_calls(node.body, func_name)
        if total_calls == 0:
            return 'O(1)', ''

        # Halving recursion → O(log n) stack
        if _has_halving_call(node.body, func_name, params):
            return 'O(log n)', f"halving recursion → O(log n) call stack"

        # Double recursion → O(2ⁿ) space (or O(n) stack depth)
        # Actually double recursion like fibonacci: stack depth is O(n)
        # because we go n levels deep before branching
        for stmt in node.body:
            direct_calls = _count_calls_in_node(stmt, func_name)
            if direct_calls >= 2:
                return 'O(n)', f"double recursion → O(n) call stack (max depth)"

        # Linear recursion → O(n) stack
        return 'O(n)', f"linear recursion → O(n) call stack"

    def _allocation_space(self, body: List[Any], params: List[str],
                          ) -> Tuple[str, List[str]]:
        """Count array allocations."""
        space = 'O(1)'
        reasons = []
        for stmt in body:
            if isinstance(stmt, AssignNode):
                v = stmt.value
                # [0] * n or [[0]*n]*n → O(n) or O(n²)
                if isinstance(v, ListLiteralNode):
                    if v.elements:
                        space = _worse(space, 'O(n)')
                        reasons.append(f'array allocated: {stmt.name}')
                if isinstance(v, (FuncCallNode, CallNode)) and v.name == 'range':
                    space = _worse(space, 'O(n)')
                    reasons.append(f'range array: {stmt.name}')
            elif isinstance(stmt, IfNode):
                s2, r2 = self._allocation_space(stmt.body, params)
                space = _worse(space, s2); reasons.extend(r2)
                for _, b in stmt.elif_clauses:
                    s2, r2 = self._allocation_space(b, params)
                    space = _worse(space, s2); reasons.extend(r2)
                if stmt.else_body:
                    s2, r2 = self._allocation_space(stmt.else_body, params)
                    space = _worse(space, s2); reasons.extend(r2)
        return space, reasons

    def _analyze_collection_space(self, body: List[Any], func_name: str, params: List[str]) -> Tuple[str, List[str]]:
        """Identify collections and trace if they grow in loops."""
        space = 'O(1)'
        reasons = []
        collections = {}

        def collect_collections(nodes):
            for stmt in nodes:
                if isinstance(stmt, AssignNode):
                    v = stmt.value
                    if isinstance(v, ListLiteralNode):
                        collections[stmt.name] = 'O(n)' if v.elements else 'O(1)'
                    elif isinstance(v, SetLiteralNode) or isinstance(v, DictLiteralNode):
                        collections[stmt.name] = 'O(1)'
                    elif isinstance(v, (FuncCallNode, CallNode)):
                        if v.name.lower() in ('range', 'hashmap', 'minheap', 'maxheap', 'queue', 'stack', 'set', 'listnode', 'treenode'):
                            collections[stmt.name] = 'O(1)'
                elif isinstance(stmt, IfNode):
                    collect_collections(stmt.body)
                    for _, b in stmt.elif_clauses:
                        collect_collections(b)
                    if stmt.else_body:
                        collect_collections(stmt.else_body)
                elif isinstance(stmt, TryNode):
                    collect_collections(stmt.body)
                elif isinstance(stmt, (ForLoopNode, ForEachNode, WhileNode, UntilNode)):
                    collect_collections(stmt.body)

        collect_collections(body)

        def check_mutations(nodes, loop_complexity=None):
            for stmt in nodes:
                if isinstance(stmt, (ForLoopNode, ForEachNode, WhileNode, UntilNode)):
                    # Get complexity of loop
                    loop_t, _ = self._analyze_stmt_time(stmt, depth=0, func_name=func_name, params=params)
                    # Use the worse loop complexity if nested
                    current_complexity = _worse(loop_complexity or 'O(1)', loop_t)
                    check_mutations(stmt.body, current_complexity)
                elif isinstance(stmt, IfNode):
                    check_mutations(stmt.body, loop_complexity)
                    for _, b in stmt.elif_clauses:
                        check_mutations(b, loop_complexity)
                    if stmt.else_body:
                        check_mutations(stmt.else_body, loop_complexity)
                elif isinstance(stmt, TryNode):
                    check_mutations(stmt.body, loop_complexity)
                elif loop_complexity is not None:
                    mutated_var = None
                    expr = stmt
                    if isinstance(expr, AutoPrintNode):
                        expr = expr.value
                    
                    if isinstance(expr, AttributeCallNode):
                        if isinstance(expr.obj, VariableNode):
                            mutated_var = expr.obj.name
                    elif isinstance(expr, CallNode) and len(expr.args) > 0:
                        if isinstance(expr.args[0], VariableNode):
                            mutated_var = expr.args[0].name
                    elif isinstance(expr, IndexAssignNode):
                        if isinstance(expr.obj, VariableNode):
                            mutated_var = expr.obj.name
                    elif isinstance(expr, AssignNode):
                        if isinstance(expr.value, AttributeCallNode) and isinstance(expr.value.obj, VariableNode):
                            mutated_var = expr.value.obj.name

                    if mutated_var and mutated_var in collections:
                        collections[mutated_var] = _worse(collections[mutated_var], loop_complexity)

        check_mutations(body)

        for name, comp in collections.items():
            if comp != 'O(1)':
                space = _worse(space, comp)
                reasons.append(f"collection '{name}' grows to {comp}")

        return space, reasons

    def _is_binary_search_pattern(self, body: List[Any]) -> bool:
        """Detect low/high/mid variable assignments (binary search)."""
        vars_seen: Set[str] = set()

        def _collect(nodes):
            for stmt in nodes:
                if isinstance(stmt, AssignNode):
                    vars_seen.add(stmt.name.lower())
                elif isinstance(stmt, IfNode):
                    _collect(stmt.body)
                    for _, elif_body in stmt.elif_clauses:
                        _collect(elif_body)
                    if stmt.else_body:
                        _collect(stmt.else_body)
                elif isinstance(stmt, TryNode):
                    _collect(stmt.body)

        _collect(body)
        return ({'low', 'high', 'mid'} <= vars_seen or
                {'lo', 'hi', 'mid'} <= vars_seen)

    def _is_logarithmic_loop(self, node: Any, params: List[str]) -> bool:
        """Detect if the loop modifies a variable from the condition by division/halving."""
        cond_vars = self._collect_variables(node.condition)
        if not cond_vars:
            return False
        return self._has_division_assignment(node.body, cond_vars)

    def _collect_variables(self, node: Any) -> Set[str]:
        if node is None:
            return set()
        if isinstance(node, VariableNode):
            return {node.name}
        if isinstance(node, BinaryOpNode):
            return self._collect_variables(node.left) | self._collect_variables(node.right)
        if isinstance(node, UnaryOpNode):
            return self._collect_variables(node.operand)
        if isinstance(node, IndexNode):
            return self._collect_variables(node.obj) | self._collect_variables(node.index)
        if isinstance(node, (FuncCallNode, CallNode)):
            res = set()
            for a in node.args:
                res |= self._collect_variables(a)
            return res
        if isinstance(node, TernaryNode):
            return (self._collect_variables(node.condition) |
                    self._collect_variables(node.true_val) |
                    self._collect_variables(node.false_val))
        return set()

    def _has_division_assignment(self, body: List[Any], vars_to_check: Set[str]) -> bool:
        for stmt in body:
            if isinstance(stmt, AssignNode):
                if stmt.name in vars_to_check:
                    if _expr_divides_var(stmt.value, stmt.name):
                        return True
            elif isinstance(stmt, IfNode):
                if self._has_division_assignment(stmt.body, vars_to_check):
                    return True
                for _, elif_body in stmt.elif_clauses:
                    if self._has_division_assignment(elif_body, vars_to_check):
                        return True
                if stmt.else_body:
                    if self._has_division_assignment(stmt.else_body, vars_to_check):
                        return True
            elif isinstance(stmt, TryNode):
                if self._has_division_assignment(stmt.body, vars_to_check):
                    return True
        return False



# ── Output formatter ───────────────────────────────────────────

def format_complexity(results: Dict[str, Complexity], explain: bool = False,
                      summary: bool = False) -> str:
    if not results:
        return "No functions analyzed."

    if summary:
        overall = results.get('Overall')
        if overall:
            return f"Time: {overall.time}  │  Space: {overall.space}"
        return ""

    lines = ["Complexity Analysis", "─" * 40]
    for name, c in results.items():
        lines.append(f"  {name}")
        lines.append(f"    Time  : {c.time}")
        lines.append(f"    Space : {c.space}")
        if explain and (c.time_reason or c.space_reason):
            if c.time_reason:
                for ln in c.time_reason.splitlines():
                    lines.append(f"      └─ {ln}")
            if c.space_reason:
                for ln in c.space_reason.splitlines():
                    lines.append(f"      └─ [space] {ln}")
        lines.append("")
    lines.append("─" * 40)
    lines.append("Disclaimer: Complexity estimation is heuristic-based and statically analyzed.")
    lines.append("  Specialized variables (e.g. tree height 'h', graph elements 'V', 'E') are")
    lines.append("  represented in terms of main input size 'n'.")
    return '\n'.join(lines)
