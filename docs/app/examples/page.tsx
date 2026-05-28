import type { Metadata } from "next";
import CodeBlock from "../components/CodeBlock";

export const metadata: Metadata = { title: "Code Examples" };

const BUBBLE_SORT = `func bubbleSort(arr)
    for i from 0 to len(arr)
        for j from 0 to len(arr) - i - 1
            if arr[j] > arr[j+1]
                swap arr[j] and arr[j+1]
    return arr

bubbleSort([5, 2, 9, 1, 7, 3])`;

const BINARY_SEARCH = `func binarySearch(arr, target)
    left = 0
    right = len(arr) - 1
    while left <= right
        mid = (left + right) // 2
        if arr[mid] == target
            return mid
        else if arr[mid] < target
            left = mid + 1
        else
            right = mid - 1
    return -1

arr = [1, 3, 5, 7, 9, 11, 13]
binarySearch(arr, 7)`;

const FIB_MEMO = `map = HashMap()

recursive fib(n)
    if n <= 1: return n
    if map.has(n): return map.get(n)
    result = fib(n-1) + fib(n-2)
    map.put(n, result)
    return result

fib(30)`;

const STACK_BALANCED = `func isBalanced(s)
    stack = Stack()
    for each ch in s
        if ch == "(" or ch == "[" or ch == "{"
            push(stack, ch)
        else if ch == ")" or ch == "]" or ch == "}"
            if isEmpty(stack): return false
            top = pop(stack)
            if ch == ")" and top != "(": return false
            if ch == "]" and top != "[": return false
            if ch == "}" and top != "{": return false
    return isEmpty(stack)

isBalanced("({[]})")`;

const BFS = `func bfs(graph, start)
    visited = Set()
    q = Queue()
    enqueue(q, start)
    visited.add(start)
    order = []

    while not isEmpty(q)
        node = dequeue(q)
        append(order, node)
        for each neighbor in graph.neighbors(node)
            if not visited.has(neighbor)
                visited.add(neighbor)
                enqueue(q, neighbor)
    return order

g = Graph()
g.addEdge(1, 2)
g.addEdge(1, 3)
g.addEdge(2, 4)
g.addEdge(3, 4)

bfs(g, 1)`;

const TWO_SUM = `func twoSum(nums, target)
    seen = HashMap()
    for i from 0 to len(nums)
        complement = target - nums[i]
        if seen.has(complement)
            return [seen.get(complement), i]
        seen.put(nums[i], i)
    return []

twoSum([2, 7, 11, 15], 9)`;

const TREE_TRAVERSAL = `func inorder(node)
    if node == null: return
    inorder(node.left)
    print node.val
    inorder(node.right)

root = TreeNode(4)
root.left = TreeNode(2)
root.right = TreeNode(6)
root.left.left = TreeNode(1)
root.left.right = TreeNode(3)
root.right.left = TreeNode(5)
root.right.right = TreeNode(7)

inorder(root)`;

const MERGE_SORT = `func merge(left, right)
    result = []
    i = 0
    j = 0
    while i < len(left) and j < len(right)
        if left[i] <= right[j]
            append(result, left[i])
            i = i + 1
        else
            append(result, right[j])
            j = j + 1
    while i < len(left)
        append(result, left[i])
        i = i + 1
    while j < len(right)
        append(result, right[j])
        j = j + 1
    return result

recursive mergeSort(arr)
    if len(arr) <= 1: return arr
    mid = len(arr) // 2
    left = mergeSort(arr[0:mid])
    right = mergeSort(arr[mid:len(arr)])
    return merge(left, right)

mergeSort([8, 3, 1, 5, 2, 9, 4, 7])`;

export default function ExamplesPage() {
  return (
    <>
      <div className="topbar">
        <span className="topbar-title">
          Examples › <span>Code Examples</span>
        </span>
        <span className="topbar-badge">v0.1</span>
      </div>
      <div className="page">
        <div className="page-hero">
          <span className="page-label">Examples</span>
          <h1 className="page-title">Code Examples</h1>
          <p className="page-desc">
            Real algorithms written in Pseudo — from sorting to graph traversal.
          </p>
        </div>

        <h2>Bubble Sort</h2>
        <CodeBlock
          code={BUBBLE_SORT}
          lang="pseudo"
          title="bubble_sort.pseudo"
          showOutput="[1, 2, 3, 5, 7, 9]"
        />

        <h2>Binary Search</h2>
        <CodeBlock
          code={BINARY_SEARCH}
          lang="pseudo"
          title="binary_search.pseudo"
          showOutput="3"
        />
        <p>
          Result <code>3</code> is the index of <code>7</code> in the array.
        </p>

        <h2>Fibonacci with Memoization</h2>
        <CodeBlock
          code={FIB_MEMO}
          lang="pseudo"
          title="fib_memo.pseudo"
          showOutput="832040"
        />

        <h2>Balanced Brackets (Stack)</h2>
        <CodeBlock
          code={STACK_BALANCED}
          lang="pseudo"
          title="balanced.pseudo"
          showOutput="true"
        />

        <h2>BFS — Breadth-First Search</h2>
        <CodeBlock
          code={BFS}
          lang="pseudo"
          title="bfs.pseudo"
          showOutput="[1, 2, 3, 4]"
        />

        <h2>Two Sum (HashMap)</h2>
        <CodeBlock
          code={TWO_SUM}
          lang="pseudo"
          title="two_sum.pseudo"
          showOutput="[0, 1]"
        />
        <p>
          Indices 0 and 1 (<code>2 + 7 = 9</code>) — O(n) solution using a
          HashMap.
        </p>

        <h2>Binary Tree — In-order Traversal</h2>
        <CodeBlock
          code={TREE_TRAVERSAL}
          lang="pseudo"
          title="inorder.pseudo"
          showOutput={`1\n2\n3\n4\n5\n6\n7`}
        />

        <h2>Merge Sort</h2>
        <CodeBlock
          code={MERGE_SORT}
          lang="pseudo"
          title="merge_sort.pseudo"
          showOutput="[1, 2, 3, 4, 5, 7, 8, 9]"
        />

        <div className="callout tip">
          <span className="callout-icon">💡</span>
          <div className="callout-body">
            <strong>Run any example with --step</strong>
            Try <code>pseudo run bubble_sort.pseudo --step</code> to watch every
            swap happen interactively.
          </div>
        </div>

        <div className="callout info">
          <span className="callout-icon">ℹ</span>
          <div className="callout-body">
            <strong>Analyze complexity</strong>
            Add <code>--analyze</code> to see the Big-O analysis:{" "}
            <code>pseudo run merge_sort.pseudo --analyze</code>
          </div>
        </div>
      </div>
    </>
  );
}
