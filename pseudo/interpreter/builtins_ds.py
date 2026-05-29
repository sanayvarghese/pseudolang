"""
Built-in data structures for the Pseudo language (Section 15.7).

Implements:
  - Stack
  - Queue
  - HashMap
  - Set (PseudoSet)
  - MinHeap / MaxHeap
  - TreeNode
  - ListNode
  - Graph

Each class provides visual display methods (Section 16) for auto-print.
"""

import heapq
from collections import deque
from typing import Any, Optional, List


# ──────────────────────────────────────────────────────────────
# Stack
# ──────────────────────────────────────────────────────────────

class Stack:
    def __init__(self):
        self._data: list = []

    def push(self, item: Any):
        self._data.append(item)

    def pop(self) -> Any:
        if not self._data:
            raise IndexError("Stack is empty")
        return self._data.pop()

    def peek(self) -> Any:
        if not self._data:
            raise IndexError("Stack is empty")
        return self._data[-1]

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def size(self) -> int:
        return len(self._data)

    def __repr__(self):
        if not self._data:
            return "Stack (empty)"
        lines = ["Stack (top → bottom):"]
        for item in reversed(self._data):
            lines.append(f"  [ {_display(item)} ]")
        lines[1] += "  ← top"
        return '\n'.join(lines)

    def __bool__(self):
        return len(self._data) > 0


# ──────────────────────────────────────────────────────────────
# Queue
# ──────────────────────────────────────────────────────────────

class Queue:
    def __init__(self):
        self._data: deque = deque()

    def enqueue(self, item: Any):
        self._data.append(item)

    def dequeue(self) -> Any:
        if not self._data:
            raise IndexError("Queue is empty")
        return self._data.popleft()

    def peek(self) -> Any:
        if not self._data:
            raise IndexError("Queue is empty")
        return self._data[0]

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def size(self) -> int:
        return len(self._data)

    def __repr__(self):
        if not self._data:
            return "Queue (empty)"
        items = ' '.join(f'[ {_display(x)} ]' for x in self._data)
        return f"Queue (front → back):\n  front → {items} ← back"

    def __bool__(self):
        return len(self._data) > 0


# ──────────────────────────────────────────────────────────────
# HashMap
# ──────────────────────────────────────────────────────────────

class HashMap:
    def __init__(self):
        self._data: dict = {}

    def put(self, key: Any, value: Any = True):
        self._data[key] = value

    def get(self, key: Any) -> Any:
        if key not in self._data:
            return None
        return self._data[key]

    def has(self, key: Any) -> bool:
        return key in self._data

    def remove(self, key: Any):
        self._data.pop(key, None)

    def add(self, item: Any):
        self._data[item] = True

    def keys(self) -> list:
        return list(self._data.keys())

    def values(self) -> list:
        return list(self._data.values())

    def size(self) -> int:
        return len(self._data)

    def __getitem__(self, key: Any) -> Any:
        return self._data.get(key, None)

    def __setitem__(self, key: Any, value: Any):
        self._data[key] = value

    def __contains__(self, key: Any) -> bool:
        return key in self._data

    def __repr__(self):
        if not self._data:
            return "HashMap: {}"
        lines = ["HashMap:"]
        for k, v in self._data.items():
            lines.append(f"  {_display(k)} → {_display(v)}")
        return '\n'.join(lines)


# ──────────────────────────────────────────────────────────────
# Set
# ──────────────────────────────────────────────────────────────

class PseudoSet:
    def __init__(self, initial=None):
        if initial:
            self._data: set = set(initial)
        else:
            self._data: set = set()

    def add(self, item: Any):
        self._data.add(item)

    def has(self, item: Any) -> bool:
        return item in self._data

    def remove(self, item: Any):
        self._data.discard(item)

    def size(self) -> int:
        return len(self._data)

    def union(self, other: 'PseudoSet') -> 'PseudoSet':
        s = PseudoSet()
        s._data = self._data | other._data
        return s

    def intersection(self, other: 'PseudoSet') -> 'PseudoSet':
        s = PseudoSet()
        s._data = self._data & other._data
        return s

    def difference(self, other: 'PseudoSet') -> 'PseudoSet':
        s = PseudoSet()
        s._data = self._data - other._data
        return s

    def __repr__(self):
        return f"Set: {{{', '.join(_display(x) for x in sorted(self._data, key=str))}}}"

    def __contains__(self, item: Any) -> bool:
        return item in self._data


# ──────────────────────────────────────────────────────────────
# MinHeap / MaxHeap
# ──────────────────────────────────────────────────────────────

class MinHeap:
    def __init__(self):
        self._data: list = []

    def push(self, item: Any):
        heapq.heappush(self._data, item)

    def insert(self, item: Any):
        self.push(item)

    def pop(self) -> Any:
        if not self._data:
            raise IndexError("MinHeap is empty")
        return heapq.heappop(self._data)

    def peek(self) -> Any:
        if not self._data:
            raise IndexError("MinHeap is empty")
        return self._data[0]

    def size(self) -> int:
        return len(self._data)

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def __getitem__(self, idx: int) -> Any:
        return self._data[idx]

    def __repr__(self):
        return str(self._data)


class MaxHeap:
    def __init__(self):
        self._data: list = []   # stored negated for max behavior

    def push(self, item: Any):
        heapq.heappush(self._data, -item)

    def insert(self, item: Any):
        self.push(item)

    def pop(self) -> Any:
        if not self._data:
            raise IndexError("MaxHeap is empty")
        return -heapq.heappop(self._data)

    def peek(self) -> Any:
        if not self._data:
            raise IndexError("MaxHeap is empty")
        return -self._data[0]

    def size(self) -> int:
        return len(self._data)

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def __getitem__(self, idx: int) -> Any:
        return -self._data[idx]

    def __repr__(self):
        return str([-x for x in self._data])


# ──────────────────────────────────────────────────────────────
# TreeNode
# ──────────────────────────────────────────────────────────────

class TreeNode:
    def __init__(self, val: Any, left: Optional['TreeNode'] = None, right: Optional['TreeNode'] = None):
        self.val = val
        self.left = left
        self.right = right

    @property
    def value(self):
        return self.val

    @value.setter
    def value(self, v):
        self.val = v

    def __repr__(self):
        return _tree_display(self)


def _tree_display(root: Optional[TreeNode]) -> str:
    """Pretty-print a binary tree."""
    if root is None:
        return "null"

    lines = []
    _fill_tree(root, lines, 0, 0, _tree_width(root))

    # Remove trailing empty lines
    while lines and all(c == ' ' for c in lines[-1]):
        lines.pop()

    return '\n'.join(''.join(row).rstrip() for row in lines if any(c != ' ' for c in row))


def _tree_width(node: Optional[TreeNode]) -> int:
    if node is None:
        return 0
    lw = _tree_width(node.left)
    rw = _tree_width(node.right)
    return max(lw + rw + 2, len(str(node.val)) + 2)


def _fill_tree(node: Optional[TreeNode], lines: list, row: int, lo: int, hi: int):
    if node is None:
        return
    mid = (lo + hi) // 2
    val_str = str(node.val)
    while len(lines) <= row:
        lines.append([' '] * (hi + 5))
    for i, ch in enumerate(val_str):
        if mid + i < len(lines[row]):
            lines[row][mid + i] = ch
    _fill_tree(node.left, lines, row + 2, lo, mid - 1)
    _fill_tree(node.right, lines, row + 2, mid + len(val_str), hi)


# ──────────────────────────────────────────────────────────────
# ListNode
# ──────────────────────────────────────────────────────────────

class ListNode:
    def __init__(self, val: Any, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

    @property
    def value(self):
        return self.val

    @value.setter
    def value(self, v):
        self.val = v

    def __repr__(self):
        parts = []
        current = self
        visited = set()
        while current is not None:
            if id(current) in visited:
                parts.append("... (cycle)")
                break
            visited.add(id(current))
            parts.append(str(current.val))
            current = current.next
        return ' → '.join(parts) + ' → null'


def linkedList(values: list) -> Optional[ListNode]:
    """Build a linked list from a Python list, return head node."""
    if not values:
        return None
    head = ListNode(values[0])
    current = head
    for v in values[1:]:
        current.next = ListNode(v)
        current = current.next
    return head


# ──────────────────────────────────────────────────────────────
# Graph
# ──────────────────────────────────────────────────────────────

class Graph:
    def __init__(self):
        self._adj: dict = {}
        self._weights: dict = {}

    def addVertex(self, v: Any):
        if v not in self._adj:
            self._adj[v] = []

    def addEdge(self, u: Any, v: Any, weight: Any = None):
        self.addVertex(u)
        self.addVertex(v)
        if v not in self._adj[u]:
            self._adj[u].append(v)
        if u not in self._adj[v]:
            self._adj[v].append(u)
        if weight is not None:
            self._weights[(u, v)] = weight
            self._weights[(v, u)] = weight

    def neighbors(self, v: Any) -> list:
        return self._adj.get(v, [])

    def hasEdge(self, u: Any, v: Any) -> bool:
        return v in self._adj.get(u, [])

    def vertices(self) -> list:
        return list(self._adj.keys())

    def __repr__(self):
        lines = ["Graph:"]
        for v in self._adj:
            nbrs = self._adj[v]
            lines.append(f"  {v} → {nbrs}")
        return '\n'.join(lines)


# ──────────────────────────────────────────────────────────────
# Display helper
# ──────────────────────────────────────────────────────────────

def _display(value: Any) -> str:
    if isinstance(value, str):
        return f'"{value}"'
    if value is None:
        return 'null'
    if isinstance(value, bool):
        return 'true' if value else 'false'
    return str(value)
