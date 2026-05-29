"""
AST Node types for the Pseudo language.
Mirrors the specification exactly from Section 22.2.
"""
from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple


# ──────────────────────────────────────────────────────────────
# Base
# ──────────────────────────────────────────────────────────────

class Node:
    """Base AST node."""
    line: int = 0


# ──────────────────────────────────────────────────────────────
# Expression Nodes
# ──────────────────────────────────────────────────────────────

@dataclass
class NumberLiteralNode(Node):
    value: Any          # int or float
    line: int = 0


@dataclass
class StringLiteralNode(Node):
    value: str
    line: int = 0


@dataclass
class BoolLiteralNode(Node):
    value: bool
    line: int = 0


@dataclass
class NullLiteralNode(Node):
    line: int = 0


@dataclass
class ListLiteralNode(Node):
    elements: List[Any] = field(default_factory=list)
    line: int = 0


@dataclass
class SetLiteralNode(Node):
    elements: List[Any] = field(default_factory=list)
    line: int = 0


@dataclass
class DictLiteralNode(Node):
    """dict/HashMap literal {key: value, ...}"""
    pairs: List[Tuple[Any, Any]] = field(default_factory=list)
    line: int = 0


@dataclass
class VariableNode(Node):
    name: str
    line: int = 0


@dataclass
class BinaryOpNode(Node):
    left: Any
    op: str
    right: Any
    line: int = 0


@dataclass
class UnaryOpNode(Node):
    op: str
    operand: Any
    line: int = 0


@dataclass
class IndexNode(Node):
    obj: Any
    index: Any
    line: int = 0


@dataclass
class SliceNode(Node):
    obj: Any
    start: Any
    end: Any
    line: int = 0


@dataclass
class CallNode(Node):
    name: str
    args: List[Any] = field(default_factory=list)
    line: int = 0


@dataclass
class AttributeNode(Node):
    obj: Any
    attr: str
    line: int = 0


@dataclass
class AttributeCallNode(Node):
    obj: Any
    attr: str
    args: List[Any] = field(default_factory=list)
    line: int = 0


@dataclass
class InterpolatedStringNode(Node):
    """String with {expr} interpolation."""
    parts: List[Any] = field(default_factory=list)   # alternating str and expr nodes
    line: int = 0


# ──────────────────────────────────────────────────────────────
# Statement Nodes
# ──────────────────────────────────────────────────────────────

@dataclass
class ProgramNode(Node):
    body: List[Any] = field(default_factory=list)
    line: int = 0


@dataclass
class FuncDefNode(Node):
    name: str
    params: List[str] = field(default_factory=list)
    body: List[Any] = field(default_factory=list)
    line: int = 0


@dataclass
class FuncCallNode(Node):
    name: str
    args: List[Any] = field(default_factory=list)
    line: int = 0


@dataclass
class AutoPrintNode(Node):
    value: Any
    line: int = 0


@dataclass
class ForLoopNode(Node):
    var: str
    start: Any
    end: Any
    step: Any                   # default 1
    body: List[Any] = field(default_factory=list)
    line: int = 0


@dataclass
class ForEachNode(Node):
    item: str
    collection: Any
    body: List[Any] = field(default_factory=list)
    line: int = 0


@dataclass
class WhileNode(Node):
    condition: Any
    body: List[Any] = field(default_factory=list)
    line: int = 0


@dataclass
class UntilNode(Node):
    condition: Any
    body: List[Any] = field(default_factory=list)
    line: int = 0


@dataclass
class IfNode(Node):
    condition: Any
    body: List[Any] = field(default_factory=list)
    elif_clauses: List[Tuple[Any, List[Any]]] = field(default_factory=list)
    else_body: Optional[List[Any]] = None
    line: int = 0


@dataclass
class ReturnNode(Node):
    value: Any = None           # None means bare return → null
    line: int = 0


@dataclass
class BreakNode(Node):
    line: int = 0


@dataclass
class ContinueNode(Node):
    line: int = 0


@dataclass
class AssignNode(Node):
    name: str
    value: Any
    line: int = 0


@dataclass
class IndexAssignNode(Node):
    """arr[i] = val"""
    obj: Any
    index: Any
    value: Any
    line: int = 0


@dataclass
class AttributeAssignNode(Node):
    """obj.attr = val (e.g. root.left = TreeNode(3))"""
    obj: Any
    attr: str
    value: Any
    line: int = 0


@dataclass
class PrintNode(Node):
    value: Any
    line: int = 0


@dataclass
class InputNode(Node):
    prompt: Optional[str] = None
    type_hint: Optional[str] = None
    line: int = 0


@dataclass
class TryNode(Node):
    body: List[Any] = field(default_factory=list)
    catch_clauses: List[Tuple[Optional[str], List[Any]]] = field(default_factory=list)
    finally_body: Optional[List[Any]] = None
    line: int = 0


@dataclass
class RaiseNode(Node):
    error: Any
    line: int = 0


@dataclass
class GlobalNode(Node):
    name: str
    line: int = 0


@dataclass
class CommentNode(Node):
    text: str
    line: int = 0


@dataclass
class SwapNode(Node):
    a: Any   # expr - could be arr[i] or simple var
    b: Any
    line: int = 0


@dataclass
class TernaryNode(Node):
    condition: Any
    true_val: Any
    false_val: Any
    line: int = 0
