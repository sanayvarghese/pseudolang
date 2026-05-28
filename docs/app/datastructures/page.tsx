import type { Metadata } from "next";
import CodeBlock from "../components/CodeBlock";

export const metadata: Metadata = { title: "Data Structures" };

export default function DataStructuresPage() {
  return (
    <>
      <div className="topbar">
        <span className="topbar-title">
          Built-ins › <span>Data Structures</span>
        </span>
        <span className="topbar-badge">v0.1</span>
      </div>
      <div className="page">
        <div className="page-hero">
          <span className="page-label">Built-ins</span>
          <h1 className="page-title">Data Structures</h1>
          <p className="page-desc">
            Interview-ready data structures built into Pseudo. Auto-print shows
            a visual representation when you print them.
          </p>
        </div>

        {/* Stack */}
        <h2>Stack</h2>
        <CodeBlock
          lang="pseudo"
          code={`s = Stack()
push(s, 1)
push(s, 2)
push(s, 3)
s`}
          showOutput={`Stack (top → bottom):
  [ 3 ]  ← top
  [ 2 ]
  [ 1 ]`}
        />
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Method</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              {[
                ["push(stack, item)", "Add item to top"],
                ["pop(stack)", "Remove and return top item"],
                ["peek(stack)", "View top item without removing"],
                ["isEmpty(stack)", "True if empty"],
                ["size(stack)", "Number of elements"],
              ].map(([m, d]) => (
                <tr key={String(m)}>
                  <td>
                    <code>{m}</code>
                  </td>
                  <td style={{ color: "var(--fg-muted)" }}>{d}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Queue */}
        <h2>Queue</h2>
        <CodeBlock
          lang="pseudo"
          code={`q = Queue()
enqueue(q, "a")
enqueue(q, "b")
enqueue(q, "c")
q`}
          showOutput={`Queue (front → back):
  front → [ "a" ] [ "b" ] [ "c" ] ← back`}
        />
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Method</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              {[
                ["enqueue(queue, item)", "Add item to back"],
                ["dequeue(queue)", "Remove and return front item"],
                ["peek(queue)", "View front item without removing"],
                ["isEmpty(queue)", "True if empty"],
                ["size(queue)", "Number of elements"],
              ].map(([m, d]) => (
                <tr key={String(m)}>
                  <td>
                    <code>{m}</code>
                  </td>
                  <td style={{ color: "var(--fg-muted)" }}>{d}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* HashMap */}
        <h2>HashMap</h2>
        <CodeBlock
          lang="pseudo"
          code={`m = HashMap()
m.put("name", "Alice")
m.put("age", 25)
m`}
          showOutput={`HashMap:
  "name" → "Alice"
  "age" → 25`}
        />
        <CodeBlock
          lang="pseudo"
          code={`# Also works with dict-style:
m = {}
m["name"] = "Alice"
print m.get("name")   # → Alice
print m.has("age")    # → false
print m.keys()        # → ["name"]`}
        />
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Method</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              {[
                ["map.put(key, value)", "Insert or update key-value pair"],
                ["map.get(key)", "Get value by key (null if not found)"],
                ["map.has(key)", "True if key exists"],
                ["map.remove(key)", "Delete key-value pair"],
                ["map.keys()", "List of all keys"],
                ["map.values()", "List of all values"],
                ["map.size()", "Number of entries"],
              ].map(([m, d]) => (
                <tr key={String(m)}>
                  <td>
                    <code>{m}</code>
                  </td>
                  <td style={{ color: "var(--fg-muted)" }}>{d}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Set */}
        <h2>Set</h2>
        <CodeBlock
          lang="pseudo"
          code={`s = Set()
s.add(1)
s.add(2)
s.add(2)  # duplicate ignored
s`}
          showOutput={`Set: {1, 2}`}
        />
        <CodeBlock
          lang="pseudo"
          code={`a = Set([1,2,3])
b = Set([2,3,4])
a.union(b)         # → Set: {1, 2, 3, 4}
a.intersection(b)  # → Set: {2, 3}
a.difference(b)    # → Set: {1}`}
        />
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Method</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              {[
                ["s.add(item)", "Add item (duplicate ignored)"],
                ["s.has(item)", "True if item in set"],
                ["s.remove(item)", "Remove item"],
                ["s.size()", "Number of elements"],
                ["s.union(other)", "Return union of two sets"],
                ["s.intersection(other)", "Return intersection"],
                ["s.difference(other)", "Return difference"],
              ].map(([m, d]) => (
                <tr key={String(m)}>
                  <td>
                    <code>{m}</code>
                  </td>
                  <td style={{ color: "var(--fg-muted)" }}>{d}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* MinHeap / MaxHeap */}
        <h2>MinHeap / MaxHeap</h2>
        <CodeBlock
          lang="pseudo"
          code={`pq = MinHeap()
push(pq, 5)
push(pq, 1)
push(pq, 3)
peek(pq)    # → 1 (min on top)
pop(pq)     # → 1
pop(pq)     # → 3`}
        />
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Method</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              {[
                ["push(heap, item)", "Add item"],
                ["pop(heap)", "Remove and return min/max"],
                ["peek(heap)", "View min/max without removing"],
                ["size(heap)", "Number of elements"],
                ["isEmpty(heap)", "True if empty"],
              ].map(([m, d]) => (
                <tr key={String(m)}>
                  <td>
                    <code>{m}</code>
                  </td>
                  <td style={{ color: "var(--fg-muted)" }}>{d}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* TreeNode */}
        <h2>TreeNode</h2>
        <CodeBlock
          lang="pseudo"
          code={`root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(3)
root.left.left = TreeNode(4)
root`}
          showOutput={`    1
  2   3
4`}
        />
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Attribute</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              {[
                ["node.val", "The node value"],
                ["node.left", "Left child (null by default)"],
                ["node.right", "Right child (null by default)"],
              ].map(([a, d]) => (
                <tr key={String(a)}>
                  <td>
                    <code>{a}</code>
                  </td>
                  <td style={{ color: "var(--fg-muted)" }}>{d}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* ListNode */}
        <h2>ListNode (Linked List)</h2>
        <CodeBlock
          lang="pseudo"
          code={`head = linkedList([1, 2, 3, 4])
head`}
          showOutput={`1 → 2 → 3 → 4 → null`}
        />
        <CodeBlock
          lang="pseudo"
          code={`# Manual construction:
head = ListNode(1)
head.next = ListNode(2)
head.next.next = ListNode(3)`}
        />
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Attribute / Function</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              {[
                ["node.val", "The node value"],
                ["node.next", "Next node (null if end)"],
                [
                  "linkedList(list)",
                  "Build linked list from a list, returns head",
                ],
              ].map(([a, d]) => (
                <tr key={String(a)}>
                  <td>
                    <code>{a}</code>
                  </td>
                  <td style={{ color: "var(--fg-muted)" }}>{d}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Graph */}
        <h2>Graph</h2>
        <CodeBlock
          lang="pseudo"
          code={`g = Graph()
g.addEdge(1, 2)
g.addEdge(1, 3)
g.addEdge(2, 4)
g`}
          showOutput={`Graph:
  1 → [2, 3]
  2 → [1, 4]
  3 → [1]
  4 → [2]`}
        />
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Method</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              {[
                ["g.addVertex(v)", "Add vertex"],
                ["g.addEdge(u, v)", "Add undirected edge"],
                ["g.addEdge(u, v, weight)", "Add weighted edge"],
                ["g.neighbors(v)", "List of adjacent vertices"],
                ["g.hasEdge(u, v)", "True if edge exists"],
                ["g.vertices()", "List of all vertices"],
              ].map(([m, d]) => (
                <tr key={String(m)}>
                  <td>
                    <code>{m}</code>
                  </td>
                  <td style={{ color: "var(--fg-muted)" }}>{d}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
