"""Pseudo tree-walking interpreter (Section 22.3)."""

import math
import time
import sys
from collections import deque
from typing import Any, Dict, List, Optional
from ..parser.ast_nodes import *
from .builtins_ds import (Stack, Queue, HashMap, PseudoSet, MinHeap, MaxHeap,
                           TreeNode, ListNode, Graph, linkedList)


# ── Signals ──────────────────────────────────────────────────
class ReturnSignal(Exception):
    def __init__(self, value): self.value = value

class BreakSignal(Exception): pass
class ContinueSignal(Exception): pass

class PseudoError(Exception):
    def __init__(self, msg, line=0): super().__init__(msg); self.line = line

class LoopTimeoutError(PseudoError): pass
class RecursionLimitError(PseudoError): pass


# ── Scope ─────────────────────────────────────────────────────
class Scope:
    def __init__(self, parent=None):
        self._vars: Dict[str, Any] = {}
        self.parent = parent
        self._globals: set = set()

    def get(self, name: str) -> Any:
        if name in self._vars:
            return self._vars[name]
        if self.parent:
            return self.parent.get(name)
        return None

    def set(self, name: str, value: Any):
        if name in self._globals and self.parent:
            self._set_global(name, value)
        else:
            self._vars[name] = value

    def declare_global(self, name: str):
        self._globals.add(name)

    def _set_global(self, name: str, value: Any):
        scope = self
        while scope.parent:
            scope = scope.parent
        scope._vars[name] = value

    def get_global(self, name: str) -> Any:
        scope = self
        while scope.parent:
            scope = scope.parent
        return scope._vars.get(name, None)


# ── Interpreter ───────────────────────────────────────────────
class Interpreter:
    MAX_ITER = 10_000_000
    TIMEOUT  = 5.0
    MAX_RECURSION = 1000

    def __init__(self, timeout=5.0, max_iter=10_000_000, inputs=None,
                 step_mode=False, dry_run=False, no_auto_print=False):
        self.timeout   = timeout
        self.max_iter  = max_iter
        self._inputs   = deque(inputs or [])
        self._input_count = 0
        self.step_mode = step_mode
        self.dry_run   = dry_run
        self.no_auto_print = no_auto_print
        self._iter_count = 0
        self._start_time = 0.0
        self._call_depth = 0
        self._global_scope = Scope()
        self._setup_builtins()
        self._step_count = 0
        self._source_lines = []

    def _setup_builtins(self):
        g = self._global_scope._vars
        g['pi'] = math.pi
        g['e']  = math.e

    def run(self, program: ProgramNode, source: str = ""):
        self._start_time = time.time()
        self._source_lines = source.splitlines()
        self._exec_list(program.body, self._global_scope)

    def _exec_list(self, stmts: List[Any], scope: Scope):
        for stmt in stmts:
            self._exec(stmt, scope)

    def _exec(self, node: Any, scope: Scope) -> Any:
        if node is None or isinstance(node, CommentNode):
            return None

        is_special = isinstance(node, (AssignNode, IndexAssignNode, AttributeAssignNode,
                                       WhileNode, UntilNode, ForLoopNode, ForEachNode,
                                       IfNode, SwapNode))
        if self.step_mode and not is_special:
            self._step(node, scope, 'default')

        if isinstance(node, AssignNode):
            val = self._eval(node.value, scope)
            scope.set(node.name, val)
            if self.step_mode:
                self._step(node, scope, 'assign')

        elif isinstance(node, IndexAssignNode):
            obj = self._eval(node.obj, scope)
            idx = self._eval(node.index, scope)
            val = self._eval(node.value, scope)
            if isinstance(obj, (list, dict, HashMap)):
                if isinstance(obj, HashMap):
                    obj.put(idx, val)
                else:
                    obj[idx] = val
            elif isinstance(obj, (TreeNode, ListNode)):
                setattr(obj, str(idx), val)
            if self.step_mode:
                self._step(node, scope, 'assign')

        elif isinstance(node, AttributeAssignNode):
            obj = self._eval(node.obj, scope)
            val = self._eval(node.value, scope)
            if obj is not None:
                setattr(obj, node.attr, val)
            if self.step_mode:
                self._step(node, scope, 'assign')

        elif isinstance(node, PrintNode):
            val = self._eval(node.value, scope)
            print(display_value(val))

        elif isinstance(node, AutoPrintNode):
            val = self._eval(node.value, scope)
            if not self.no_auto_print and val is not None:
                print(display_value(val))

        elif isinstance(node, FuncDefNode):
            scope.set(node.name, node)

        elif isinstance(node, (FuncCallNode, CallNode)):
            self._call_func(node.name, [self._eval(a, scope) for a in node.args], node.line, scope)

        elif isinstance(node, ReturnNode):
            val = self._eval(node.value, scope) if node.value else None
            raise ReturnSignal(val)

        elif isinstance(node, BreakNode):
            raise BreakSignal()

        elif isinstance(node, ContinueNode):
            raise ContinueSignal()

        elif isinstance(node, GlobalNode):
            scope.declare_global(node.name)

        elif isinstance(node, ForLoopNode):
            self._exec_for(node, scope)

        elif isinstance(node, ForEachNode):
            self._exec_foreach(node, scope)

        elif isinstance(node, WhileNode):
            self._exec_while(node, scope)

        elif isinstance(node, UntilNode):
            self._exec_until(node, scope)

        elif isinstance(node, IfNode):
            self._exec_if(node, scope)

        elif isinstance(node, TryNode):
            self._exec_try(node, scope)

        elif isinstance(node, RaiseNode):
            msg = self._eval(node.error, scope)
            raise PseudoError(str(msg), node.line)

        elif isinstance(node, SwapNode):
            if self.step_mode:
                arr_name = "?"
                arr_val = None
                if isinstance(node.a, IndexNode) and isinstance(node.a.obj, VariableNode):
                    arr_name = node.a.obj.name
                    arr_val = scope.get(arr_name)
                elif isinstance(node.a, VariableNode):
                    arr_name = node.a.name
                    arr_val = scope.get(arr_name)
                import copy
                before_val = copy.deepcopy(arr_val) if arr_val is not None else None
                
                self._exec_swap(node, scope)
                
                arr_val_after = scope.get(arr_name) if arr_name != "?" else None
                after_val = copy.deepcopy(arr_val_after) if arr_val_after is not None else None
                
                self._step(node, scope, 'swap', arr_name=arr_name, before=before_val, after=after_val)
            else:
                self._exec_swap(node, scope)

    def _exec_for(self, node: ForLoopNode, scope: Scope):
        start = self._eval(node.start, scope)
        end   = self._eval(node.end, scope)
        step  = self._eval(node.step, scope)
        if step is None: step = 1
        i = start
        while True:
            cond_val = (step > 0 and i < end) or (step < 0 and i > end)
            scope.set(node.var, i)
            if self.step_mode:
                from ..parser.ast_nodes import BinaryOpNode, VariableNode
                cond_op = '<' if step > 0 else '>'
                mock_cond = BinaryOpNode(left=VariableNode(node.var), op=cond_op, right=node.end)
                self._step(node, scope, 'loop', cond_node=mock_cond, cond_val=cond_val, loop_var=node.var)
            if not cond_val:
                break
            self._check_limits(node.line)
            try:
                self._exec_list(node.body, scope)
            except BreakSignal:
                return
            except ContinueSignal:
                pass
            i += step

    def _exec_foreach(self, node: ForEachNode, scope: Scope):
        coll = self._eval(node.collection, scope)
        if coll is None:
            return
        for item in _iter(coll):
            self._check_limits(node.line)
            scope.set(node.item, item)
            if self.step_mode:
                self._step(node, scope, 'loop', loop_var=node.item)
            try:
                self._exec_list(node.body, scope)
            except BreakSignal:
                return
            except ContinueSignal:
                pass

    def _exec_while(self, node: WhileNode, scope: Scope):
        while True:
            cond_val = self._truthy(self._eval(node.condition, scope))
            if self.step_mode:
                self._step(node, scope, 'loop', cond_node=node.condition, cond_val=cond_val)
            if not cond_val:
                break
            self._check_limits(node.line)
            try:
                self._exec_list(node.body, scope)
            except BreakSignal:
                return
            except ContinueSignal:
                pass

    def _exec_until(self, node: UntilNode, scope: Scope):
        while True:
            cond_val = self._truthy(self._eval(node.condition, scope))
            if self.step_mode:
                self._step(node, scope, 'loop', cond_node=node.condition, cond_val=cond_val)
            if cond_val:
                break
            self._check_limits(node.line)
            try:
                self._exec_list(node.body, scope)
            except BreakSignal:
                return
            except ContinueSignal:
                pass

    def _exec_if(self, node: IfNode, scope: Scope):
        cond_val = self._truthy(self._eval(node.condition, scope))
        if self.step_mode:
            self._step(node, scope, 'if', cond_node=node.condition, cond_val=cond_val)
        if cond_val:
            self._exec_list(node.body, scope)
            return
        for cond, body in node.elif_clauses:
            elif_val = self._truthy(self._eval(cond, scope))
            if self.step_mode:
                self._step(cond, scope, 'if', cond_node=cond, cond_val=elif_val)
            if elif_val:
                self._exec_list(body, scope)
                return
        if node.else_body is not None:
            self._exec_list(node.else_body, scope)

    def _exec_try(self, node: TryNode, scope: Scope):
        try:
            self._exec_list(node.body, scope)
        except (PseudoError, ZeroDivisionError, IndexError, TypeError,
                ValueError, KeyError, AttributeError) as e:
            err_type = type(e).__name__
            handled = False
            for error_name, catch_body in node.catch_clauses:
                if error_name is None or error_name == err_type:
                    self._exec_list(catch_body, scope)
                    handled = True
                    break
            if not handled and node.catch_clauses:
                self._exec_list(node.catch_clauses[-1][1], scope)
        finally:
            if node.finally_body:
                self._exec_list(node.finally_body, scope)

    def _exec_swap(self, node: SwapNode, scope: Scope):
        # Eval both sides
        a_val = self._eval(node.a, scope)
        b_val = self._eval(node.b, scope)
        # Write back
        self._assign_back(node.b, a_val, scope)
        self._assign_back(node.a, b_val, scope)

    def _assign_back(self, node: Any, val: Any, scope: Scope):
        if isinstance(node, VariableNode):
            scope.set(node.name, val)
        elif isinstance(node, IndexNode):
            obj = self._eval(node.obj, scope)
            idx = self._eval(node.index, scope)
            if isinstance(obj, list):
                obj[int(idx)] = val
            elif isinstance(obj, HashMap):
                obj.put(idx, val)

    # ── Evaluator ─────────────────────────────────────────────

    def _eval(self, node: Any, scope: Scope) -> Any:
        if node is None:
            return None

        if isinstance(node, NumberLiteralNode):
            return node.value
        if isinstance(node, StringLiteralNode):
            return node.value
        if isinstance(node, BoolLiteralNode):
            return node.value
        if isinstance(node, NullLiteralNode):
            return None
        if isinstance(node, ListLiteralNode):
            return [self._eval(e, scope) for e in node.elements]
        if isinstance(node, SetLiteralNode):
            s = PseudoSet()
            for e in node.elements:
                s.add(self._eval(e, scope))
            return s
        if isinstance(node, DictLiteralNode):
            m = HashMap()
            for k, v in node.pairs:
                m.put(self._eval(k, scope), self._eval(v, scope))
            return m

        if isinstance(node, VariableNode):
            return scope.get(node.name)

        if isinstance(node, InputNode):
            return self._get_input(node)

        if isinstance(node, InterpolatedStringNode):
            return ''.join(
                p if isinstance(p, str) else str(display_value(self._eval(p, scope)))
                for p in node.parts
            )

        if isinstance(node, BinaryOpNode):
            return self._eval_binop(node, scope)

        if isinstance(node, UnaryOpNode):
            operand = self._eval(node.operand, scope)
            if node.op == '-':
                return -operand
            if node.op == 'not':
                return not self._truthy(operand)
            return operand

        if isinstance(node, IndexNode):
            obj = self._eval(node.obj, scope)
            idx = self._eval(node.index, scope)
            if isinstance(obj, HashMap):
                return obj.get(idx)
            if isinstance(obj, (list, str)):
                return obj[int(idx)]
            if isinstance(obj, (TreeNode, ListNode)):
                return getattr(obj, str(idx), None)
            if hasattr(obj, '__getitem__'):
                try:
                    return obj[idx]
                except Exception:
                    pass
            return None

        if isinstance(node, SliceNode):
            obj = self._eval(node.obj, scope)
            start = self._eval(node.start, scope) if node.start else None
            end   = self._eval(node.end, scope) if node.end else None
            return obj[start:end]

        if isinstance(node, AttributeNode):
            if node.attr.startswith('_'):
                raise AttributeError(f"SecurityError: Access to private attribute {node.attr!r} is forbidden")
            obj = self._eval(node.obj, scope)
            return getattr(obj, node.attr, None)

        if isinstance(node, AttributeCallNode):
            if node.attr.startswith('_'):
                raise AttributeError(f"SecurityError: Call to private attribute {node.attr!r} is forbidden")
            obj = self._eval(node.obj, scope)
            args = [self._eval(a, scope) for a in node.args]
            attr = node.attr
            if isinstance(obj, list) and attr == 'push':
                attr = 'append'
            if isinstance(obj, list) and attr == 'insert' and len(args) == 1:
                attr = 'append'
            method = getattr(obj, attr, None)
            if callable(method):
                return method(*args)
            raise AttributeError(f"AttributeError: {type(obj).__name__} object has no attribute {node.attr!r}")

        if isinstance(node, CallNode):
            args = [self._eval(a, scope) for a in node.args]
            # _call_func checks user-defined functions first, then falls back to builtins
            return self._call_func(node.name, args, node.line, scope)

        if isinstance(node, FuncCallNode):
            args = [self._eval(a, scope) for a in node.args]
            return self._call_func(node.name, args, node.line, scope)

        if isinstance(node, AutoPrintNode):
            return self._eval(node.value, scope)

        if isinstance(node, TernaryNode):
            cond = self._eval(node.condition, scope)
            if self._truthy(cond):
                return self._eval(node.true_val, scope)
            else:
                return self._eval(node.false_val, scope)

        return None

    def _eval_binop(self, node: BinaryOpNode, scope: Scope) -> Any:
        op = node.op
        # Short-circuit
        if op == 'and':
            l = self._eval(node.left, scope)
            return self._eval(node.right, scope) if self._truthy(l) else l
        if op == 'or':
            l = self._eval(node.left, scope)
            return l if self._truthy(l) else self._eval(node.right, scope)

        left  = self._eval(node.left, scope)
        right = self._eval(node.right, scope)

        if op == '+':
            if isinstance(left, list) and isinstance(right, list):
                return left + right
            return left + right
        if op == '-':  return left - right
        if op == '*':  return left * right
        if op == '/':
            if right == 0: raise ZeroDivisionError("cannot divide by zero")
            return left / right
        if op == '//':
            if right == 0: raise ZeroDivisionError("cannot divide by zero")
            return left // right
        if op == '%':  return left % right
        if op == '**': return left ** right
        if op == '>':  return left > right
        if op == '<':  return left < right
        if op == '>=': return left >= right
        if op == '<=': return left <= right
        if op == '==': return left == right
        if op == '!=': return left != right
        if op == 'in':
            if right is None:
                return False
            try:
                return left in right
            except TypeError:
                return False
        if op == 'not in':
            if right is None:
                return True
            try:
                return left not in right
            except TypeError:
                return True
        return None

    # ── Function calls ────────────────────────────────────────

    def _call_func(self, name: str, args: List[Any], line: int, scope: Scope) -> Any:
        if self._call_depth >= self.MAX_RECURSION:
            raise RecursionLimitError(
                f"RecursionError: Maximum recursion depth exceeded (1000 calls)\n"
                f"  in {name}() → line {line}\n  Hint: Check your base case.", line)

        func_node = scope.get(name)
        if func_node is None or not isinstance(func_node, FuncDefNode):
            # try builtin
            return self._call_builtin(name, args, line, scope)

        if len(args) != len(func_node.params):
            raise PseudoError(
                f"ArgumentError: {name}() takes {len(func_node.params)} arguments, got {len(args)}",
                line)

        local = Scope(parent=self._global_scope)
        for param, val in zip(func_node.params, args):
            local.set(param, val)

        self._call_depth += 1
        try:
            self._exec_list(func_node.body, local)
            return None
        except ReturnSignal as r:
            return r.value
        finally:
            self._call_depth -= 1

    def _call_builtin(self, name: str, args: List[Any], line: int, scope: Scope) -> Any:
        n = name.lower()

        # Data structure constructors
        if n == 'stack':   return Stack()
        if n == 'queue':   return Queue()
        if n == 'hashmap': return HashMap()
        if n == 'set':     return PseudoSet(args[0] if args else None)
        if n == 'minheap': return MinHeap()
        if n == 'maxheap': return MaxHeap()
        if n == 'treenode': return TreeNode(*args)
        if n == 'listnode': return ListNode(*args)
        if n == 'graph':   return Graph()
        if n == 'linkedlist': return linkedList(args[0] if args else [])

        # Stack ops
        if n == 'push':
            obj = args[0]
            if isinstance(obj, Stack):   obj.push(args[1]); return None
            if isinstance(obj, MinHeap): obj.push(args[1]); return None
            if isinstance(obj, MaxHeap): obj.push(args[1]); return None
            if isinstance(obj, list):    obj.append(args[1]); return None
        if n == 'pop':
            obj = args[0]
            if isinstance(obj, Stack): return obj.pop()
            if isinstance(obj, (MinHeap, MaxHeap)): return obj.pop()
            if isinstance(obj, list):
                i = int(args[1]) if len(args) > 1 else -1
                return obj.pop(i)
        if n == 'peek':
            return args[0].peek()
        if n in ('isempty', 'is_empty'):
            obj = args[0]
            if hasattr(obj, 'is_empty'): return obj.is_empty()
            if isinstance(obj, list):    return len(obj) == 0
        if n == 'size':
            obj = args[0]
            if hasattr(obj, 'size'): return obj.size()
            return len(obj)
        if n == 'enqueue':
            args[0].enqueue(args[1]); return None
        if n == 'dequeue':
            return args[0].dequeue()

        # HashMap functional-style calls (alternative to method calls)
        if n == 'put':
            if hasattr(args[0], 'put'): args[0].put(args[1], args[2]); return None
        if n == 'get':
            if hasattr(args[0], 'get'): return args[0].get(args[1])
        if n == 'has':
            if hasattr(args[0], 'has'): return args[0].has(args[1])
        if n == 'keys':
            if hasattr(args[0], 'keys'): return args[0].keys()
        if n == 'values':
            if hasattr(args[0], 'values'): return args[0].values()
        if n == 'entries':
            if hasattr(args[0], 'entries'): return args[0].entries()

        # Set functional-style
        if n == 'add':
            if hasattr(args[0], 'add'): args[0].add(args[1]); return None
        if n == 'union':
            if hasattr(args[0], 'union'): return args[0].union(args[1])
        if n == 'intersection':
            if hasattr(args[0], 'intersection'): return args[0].intersection(args[1])
        if n == 'difference':
            if hasattr(args[0], 'difference'): return args[0].difference(args[1])

        # Graph functional-style
        if n == 'addvertex':
            if hasattr(args[0], 'addVertex'): args[0].addVertex(args[1]); return None
        if n == 'addedge':
            if hasattr(args[0], 'addEdge'):
                if len(args) >= 4: args[0].addEdge(args[1], args[2], args[3])
                else:              args[0].addEdge(args[1], args[2])
                return None
        if n == 'neighbors':
            if hasattr(args[0], 'neighbors'): return args[0].neighbors(args[1])
        if n == 'hasedge':
            if hasattr(args[0], 'hasEdge'): return args[0].hasEdge(args[1], args[2])
        if n == 'vertices':
            if hasattr(args[0], 'vertices'): return args[0].vertices()

        # List ops
        if n == 'len':
            obj = args[0]
            if hasattr(obj, 'size'): return obj.size()
            return len(obj) if obj is not None else 0
        if n == 'append':  args[0].append(args[1]); return None
        if n == 'prepend': args[0].insert(0, args[1]); return None
        if n == 'remove':
            if len(args) > 1: args[0].remove(args[1])
            return None
        if n == 'insert':
            if len(args) == 2:
                args[0].append(args[1])
            elif len(args) == 3:
                args[0].insert(int(args[1]), args[2])
            return None
        if n == 'sort':
            reverse = args[1] if len(args) > 1 else False
            args[0].sort(reverse=bool(reverse)); return None
        if n == 'sorted':
            reverse = args[1] if len(args) > 1 else False
            return sorted(args[0], reverse=bool(reverse))
        if n == 'reverse': args[0].reverse(); return None
        if n == 'reversed': return list(reversed(args[0]))
        if n == 'index':
            try: return args[0].index(args[1])
            except ValueError: return -1
        if n == 'find':   # alias
            try: return args[0].index(args[1])
            except ValueError: return -1
        if n == 'count':
            if len(args) > 1: return args[0].count(args[1])
            return len(args[0])
        if n == 'sum':
            if len(args) == 1: return sum(args[0])
            return sum(args[0])
        if n == 'min':
            if len(args) == 1: return min(args[0])
            return min(args)
        if n == 'max':
            if len(args) == 1: return max(args[0])
            return max(args)
        if n == 'range':
            if len(args) == 1: return list(range(int(args[0])))
            if len(args) == 2: return list(range(int(args[0]), int(args[1])))
            return list(range(int(args[0]), int(args[1]), int(args[2])))
        if n == 'copy':
            return list(args[0]) if isinstance(args[0], list) else args[0]
        if n == 'flatten':
            result = []
            def _flat(lst):
                for item in lst:
                    if isinstance(item, list): _flat(item)
                    else: result.append(item)
            _flat(args[0]); return result
        if n == 'zip':
            return [list(pair) for pair in zip(*args)]
        if n == 'enumerate':
            return [[i, v] for i, v in enumerate(args[0])]
        if n == 'filter':
            # filter(list, func_name) not supported; basic filter(list, value)
            return args[0]  # no-op for now, requires first-class functions
        if n == 'map':
            return args[0]  # no-op for now

        # String ops
        if n == 'upper': return str(args[0]).upper()
        if n == 'lower': return str(args[0]).lower()
        if n == 'strip': return str(args[0]).strip()
        if n == 'lstrip': return str(args[0]).lstrip()
        if n == 'rstrip': return str(args[0]).rstrip()
        if n == 'split':
            if len(args) == 1: return str(args[0]).split()
            return str(args[0]).split(str(args[1]))
        if n == 'join':
            if len(args) == 1: return ''.join(str(x) for x in args[0])
            delim = str(args[1]) if len(args) > 1 else ''
            return delim.join(str(x) for x in args[0])
        if n == 'replace':
            return str(args[0]).replace(str(args[1]), str(args[2]))
        if n == 'contains':
            return str(args[1]) in str(args[0])
        if n in ('startswith', 'starts_with'):
            return str(args[0]).startswith(str(args[1]))
        if n in ('endswith', 'ends_with'):
            return str(args[0]).endswith(str(args[1]))
        if n == 'substring':
            s = str(args[0])
            start = int(args[1]) if len(args) > 1 else 0
            end   = int(args[2]) if len(args) > 2 else len(s)
            return s[start:end]
        if n == 'char':   # char(str, i) → character at index
            return str(args[0])[int(args[1])]
        if n == 'ord':    return ord(str(args[0])[0]) if args else 0
        if n == 'chr':    return chr(int(args[0]))
        if n == 'format': return str(args[0]).format(*args[1:])
        if n == 'trim':   return str(args[0]).strip()
        if n == 'isdigit': return str(args[0]).isdigit()
        if n == 'isalpha': return str(args[0]).isalpha()
        if n == 'isalnum': return str(args[0]).isalnum()

        # Math
        if n == 'abs':   return abs(args[0])
        if n == 'round':
            if len(args) == 1: return round(args[0])
            return round(args[0], int(args[1]))
        if n == 'floor': return math.floor(args[0])
        if n == 'ceil':  return math.ceil(args[0])
        if n == 'sqrt':  return math.sqrt(args[0])
        if n in ('pow', 'power'):
            return args[0] ** args[1]
        if n == 'log':
            if len(args) == 1: return math.log(args[0])
            return math.log(args[0], args[1])
        if n == 'log2':  return math.log2(args[0])
        if n == 'log10': return math.log10(args[0])
        if n == 'exp':   return math.exp(args[0])
        if n == 'sin':   return math.sin(args[0])
        if n == 'cos':   return math.cos(args[0])
        if n == 'tan':   return math.tan(args[0])
        if n == 'asin':  return math.asin(args[0])
        if n == 'acos':  return math.acos(args[0])
        if n == 'atan':  return math.atan(args[0])
        if n == 'atan2': return math.atan2(args[0], args[1])
        if n == 'gcd':   return math.gcd(int(args[0]), int(args[1]))
        if n == 'lcm':
            a, b = int(args[0]), int(args[1])
            return abs(a * b) // math.gcd(a, b)
        if n == 'factorial':
            return math.factorial(int(args[0]))
        if n == 'inf':   return math.inf
        if n in ('infinity', 'max_int'): return math.inf

        # Type conversion
        if n == 'int':
            try: return int(float(args[0])) if args else 0
            except: return 0
        if n == 'float':
            try: return float(args[0]) if args else 0.0
            except: return 0.0
        if n == 'str':   return str(args[0]) if args else ''
        if n == 'list':
            if not args: return []
            if isinstance(args[0], range): return list(args[0])
            try: return list(args[0])
            except: return [args[0]]
        if n == 'bool':  return bool(args[0]) if args else False
        if n == 'char_to_int': return ord(str(args[0])[0])
        if n == 'int_to_char': return chr(int(args[0]))

        # Type checking
        if n == 'is_number': return isinstance(args[0], (int, float)) and not isinstance(args[0], bool)
        if n == 'is_string': return isinstance(args[0], str)
        if n == 'is_list':   return isinstance(args[0], list)
        if n == 'is_bool':   return isinstance(args[0], bool)
        if n == 'is_null':   return args[0] is None
        if n == 'type':
            v = args[0]
            if v is None: return 'null'
            if isinstance(v, bool): return 'bool'
            if isinstance(v, (int, float)): return 'number'
            if isinstance(v, str): return 'string'
            if isinstance(v, list): return 'list'
            return type(v).__name__

        # Utility
        if n == 'print':
            print(' '.join(display_value(a) for a in args))
            return None
        if n == 'input':
            prompt = str(args[0]) if args else None
            return self._get_input(InputNode(prompt=prompt, type_hint=None, line=line))
        if n == 'assert':
            if not self._truthy(args[0]):
                msg = str(args[1]) if len(args) > 1 else 'Assertion failed'
                raise PseudoError(f"AssertionError: {msg}", line)
            return None

        raise PseudoError(f"NameError: '{name}' is not defined", line)

    # ── Input ─────────────────────────────────────────────────

    def _get_input(self, node: InputNode) -> Any:
        self._input_count += 1
        if self._inputs:
            raw = str(self._inputs.popleft())
        else:
            if node.prompt:
                raw = input(f"? {node.prompt} → ")
            else:
                raw = input()

        type_hint = node.type_hint
        if type_hint in ('number', 'int', 'float'):
            try:
                return int(raw) if '.' not in raw else float(raw)
            except ValueError:
                raise PseudoError(f"ValueError: cannot convert {raw!r} to number", node.line)
        if type_hint == 'bool':
            return raw.lower() in ('true', 'yes', '1')
        if type_hint == 'list':
            import json
            try: return json.loads(raw)
            except Exception: return raw.split()
        if type_hint in ('string', 'text'):
            return raw
        # Auto-detect
        try:
            if '.' in raw: return float(raw)
            return int(raw)
        except ValueError:
            if raw.lower() == 'true': return True
            if raw.lower() == 'false': return False
            return raw

    # ── Helpers ───────────────────────────────────────────────

    def _truthy(self, val: Any) -> bool:
        if val is None: return False
        if isinstance(val, bool): return val
        if isinstance(val, (int, float)): return val != 0
        if isinstance(val, str): return len(val) > 0
        if isinstance(val, list): return len(val) > 0
        if isinstance(val, (Stack, Queue, HashMap, PseudoSet, MinHeap, MaxHeap)):
            return val.size() > 0
        return True

    def _check_limits(self, line: int):
        self._iter_count += 1
        if self._iter_count >= self.max_iter:
            raise LoopTimeoutError(
                f"LoopError: Infinite Loop Detected\n"
                f"  Ran for: {self.max_iter:,} iterations", line)
        if not self.step_mode and self.timeout > 0 and (time.time() - self._start_time) >= self.timeout:
            raise LoopTimeoutError(
                f"LoopError: Infinite Loop Detected\n"
                f"  Ran for: {self.timeout}s", line)

    def _find_variables_in_expr(self, expr_node: Any) -> List[str]:
        if expr_node is None:
            return []
        if isinstance(expr_node, VariableNode):
            return [expr_node.name]
        names = []
        for attr_name in dir(expr_node):
            if attr_name.startswith('_'):
                continue
            try:
                attr = getattr(expr_node, attr_name)
            except AttributeError:
                continue
            if isinstance(attr, Node):
                names.extend(self._find_variables_in_expr(attr))
            elif isinstance(attr, list):
                for item in attr:
                    if isinstance(item, Node):
                        names.extend(self._find_variables_in_expr(item))
        seen = set()
        res = []
        for n in names:
            if n not in seen:
                seen.add(n)
                res.append(n)
        return res

    def _eval_and_format_expr(self, expr_node: Any, scope: Scope) -> str:
        if isinstance(expr_node, VariableNode):
            val = scope.get(expr_node.name)
            return display_value(val)
        if isinstance(expr_node, NumberLiteralNode):
            return display_value(expr_node.value)
        if isinstance(expr_node, StringLiteralNode):
            return f'"{expr_node.value}"'
        if isinstance(expr_node, BoolLiteralNode):
            return 'true' if expr_node.value else 'false'
        if isinstance(expr_node, NullLiteralNode):
            return 'null'
        if isinstance(expr_node, BinaryOpNode):
            left_str = self._eval_and_format_expr(expr_node.left, scope)
            right_str = self._eval_and_format_expr(expr_node.right, scope)
            return f"{left_str} {expr_node.op} {right_str}"
        if isinstance(expr_node, UnaryOpNode):
            operand_str = self._eval_and_format_expr(expr_node.operand, scope)
            return f"{expr_node.op}{operand_str}"
        if isinstance(expr_node, CallNode):
            args_str = ", ".join(self._eval_and_format_expr(a, scope) for a in expr_node.args)
            return f"{expr_node.name}({args_str})"
        if isinstance(expr_node, IndexNode):
            obj_str = self._eval_and_format_expr(expr_node.obj, scope)
            idx_str = self._eval_and_format_expr(expr_node.index, scope)
            return f"{obj_str}[{idx_str}]"
        try:
            return display_value(self._eval(expr_node, scope))
        except Exception:
            return "?"

    def _get_variables_repr(self, scope: Scope) -> str:
        curr = scope
        all_vars = {}
        while curr:
            for k, v in curr._vars.items():
                if k not in all_vars and not isinstance(v, FuncDefNode) and k not in ('pi', 'e'):
                    all_vars[k] = v
            curr = curr.parent
        items_str = ", ".join(f"{k}: {display_value(v)}" for k, v in all_vars.items())
        return "{" + items_str + "}"

    def _step(self, node: Any, scope: Scope, step_type: str, **kwargs):
        if not self.step_mode:
            return
            
        self._step_count += 1
        line_no = getattr(node, 'line', None)
        line_text = ""
        if line_no and self._source_lines and 1 <= line_no <= len(self._source_lines):
            line_text = self._source_lines[line_no - 1]
            
        print(f"Step {self._step_count} │ {line_text}")
        
        if step_type == 'assign':
            vars_repr = self._get_variables_repr(scope)
            print(f"       │ Variables: {vars_repr}")
        elif step_type == 'loop':
            cond_node = kwargs.get('cond_node')
            cond_val = kwargs.get('cond_val')
            loop_var = kwargs.get('loop_var')
            
            parts = []
            if loop_var:
                var_val = scope.get(loop_var)
                parts.append(f"{loop_var} = {display_value(var_val)}")
            
            other_vars = []
            if cond_node:
                other_vars = self._find_variables_in_expr(cond_node)
                if loop_var in other_vars:
                    other_vars.remove(loop_var)
            
            for ov in other_vars:
                parts.append(f"{ov} = {display_value(scope.get(ov))}")
                
            if cond_node:
                cond_repr = self._eval_and_format_expr(cond_node, scope)
                cond_val_str = 'true' if cond_val else 'false'
                parts.append(f"condition: {cond_repr} = {cond_val_str}")
                
            print(f"       │ {', '.join(parts)}")
            
        elif step_type == 'if':
            cond_node = kwargs.get('cond_node')
            cond_val = kwargs.get('cond_val')
            
            parts = []
            other_vars = self._find_variables_in_expr(cond_node) if cond_node else []
            for ov in other_vars:
                parts.append(f"{ov} = {display_value(scope.get(ov))}")
            if cond_node:
                cond_repr = self._eval_and_format_expr(cond_node, scope)
                cond_val_str = 'true' if cond_val else 'false'
                parts.append(f"condition: {cond_repr} = {cond_val_str}")
                
            print(f"       │ {', '.join(parts)}")
            
        elif step_type == 'swap':
            arr_name = kwargs.get('arr_name')
            before_val = kwargs.get('before')
            after_val = kwargs.get('after')
            print(f"       │ {arr_name} before: {display_value(before_val)}")
            print(f"       │ {arr_name} after:  {display_value(after_val)}")
            
        else:
            vars_repr = self._get_variables_repr(scope)
            print(f"       │ Variables: {vars_repr}")
            
        try:
            input("       │ Press enter to continue...")
        except EOFError:
            pass
        print()


# ── Display helpers ───────────────────────────────────────────

def display_value(val: Any) -> str:
    if val is None:          return 'null'
    if isinstance(val, bool): return 'true' if val else 'false'
    if isinstance(val, float):
        if val == int(val) and abs(val) < 1e15:
            return str(int(val))
        return str(val)
    if isinstance(val, str): return val
    if isinstance(val, list):
        items = [display_value(x) for x in val]
        return '[' + ', '.join(items) + ']'
    return repr(val)


def _iter(obj: Any):
    if isinstance(obj, (list, tuple, str)):
        return obj
    if isinstance(obj, (Stack, Queue)):
        return list(obj._data)
    if isinstance(obj, HashMap):
        return obj.keys()
    if isinstance(obj, PseudoSet):
        return list(obj._data)
    return obj
