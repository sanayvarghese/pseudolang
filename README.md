<div align="center">

<img src="https://raw.githubusercontent.com/sanayvarghese/pseudolang/main/images/logo.png" alt="Pseudo Logo" width="100" height="100" >

# Pseudo

**Write pseudocode. Actually run it.**

[![PyPI version](https://img.shields.io/badge/pypi-v0.1.1-orange?style=flat-square)](https://pypi.org/project/runpseudo/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue?style=flat-square)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)](#)

Pseudo is a programming language that sits between English prose and real code. It lets you write flexible, natural-language-style pseudocode and **actually execute it** — perfect for coding interviews, algorithm education, and rapid idea verification.

[📦 Installation](#-installation) · [⚡ Quick Start](#-quick-start) · [🗺 PMAP System](#-the-pmap-system) · [🛠 CLI Reference](#-cli-reference) · [📚 Examples](#-examples) · [🏗 Architecture](#-architecture)

</div>

---

## 🌟 What is Pseudo?

Pseudo is **not** a replacement for Python, Java, or any production language. It's a tool for:

- ✅ **Coding interviews** — write and verify your algorithm before whiteboarding
- ✅ **Algorithm education** — step through execution line-by-line
- ✅ **Teaching** — show how data structures work with built-in visualizations
- ✅ **Quick idea verification** — turn a mental model into runnable code fast

```
100% English prose ←——————— Pseudo ———————→ Real programming language
"Sort the array"                 ↑               for(int i=0; i<n; i++){...}
```

Pseudo leans toward programming syntax, not pure prose — but the exact keywords you use are **fully customizable** via `.pmap` mapping files.

---

## 📦 Installation

> 📦 **Pseudo ships as a standalone binary.** No Python, no pip, no runtime needed.
> The executable bundles everything inside — just download and run.

---

### 🪟 Windows

Open **PowerShell** and paste:

```powershell
iwr -useb https://pseudo.wiki/install.ps1 | iex
```

This downloads `pseudo.exe` from GitHub Releases, places it in `%LOCALAPPDATA%\Programs\pseudo\`, and **adds it to your PATH automatically**. Open a new terminal and you're done.

Or download the script manually:

```powershell
curl -o install.ps1 https://pseudo.wiki/install.ps1
.\install.ps1
```

---

### 🍎 macOS

```bash
curl -fsSL https://pseudo.wiki/install.sh | bash
```

Installs to `~/.local/bin/pseudo` and appends the PATH line to `~/.zshrc` and `~/.bash_profile`. Supports both **Intel** and **Apple Silicon**.

To use immediately in your current session:

```bash
source ~/.zshrc
```

---

### 🐧 Linux

```bash
curl -fsSL https://pseudo.wiki/install.sh | bash
```

Or with `wget`:

```bash
wget -qO- https://pseudo.wiki/install.sh | bash
```

Installs to `~/.local/bin/pseudo` and updates `~/.bashrc`. Supports **x86-64** and **ARM64**.

To use immediately:

```bash
source ~/.bashrc
```

---

### Supported Platforms

| Platform       | Binary                   | Notes                        |
| -------------- | ------------------------ | ---------------------------- |
| 🪟 Windows x64 | `pseudo-windows-x64.exe` | Windows 10/11                |
| 🍎 macOS x64   | `pseudo-macos-x64`       | Intel Mac                    |
| 🍎 macOS ARM64 | `pseudo-macos-arm64`     | Apple Silicon (M1/M2/M3)     |
| 🐧 Linux x64   | `pseudo-linux-x64`       | Ubuntu, Debian, Fedora, etc. |
| 🐧 Linux ARM64 | `pseudo-linux-arm64`     | Raspberry Pi, ARM servers    |

All binaries available on [GitHub Releases](https://github.com/sanayvarghese/pseudo/releases).

---

### Verify Installation

```bash
pseudo version
# pseudo 0.1.1
```

---

### Alternative — pip _(requires Python 3.8+)_

If you already have Python installed:

```bash
pip install runpseudo
pip install --upgrade runpseudo
```

---

### Init a Project

Run inside any directory to create a local config and custom mapping:

```bash
pseudo init
```

This creates:

- `pseudo.config` — local project config pointing to your `.pmap`
- A new `.pmap` file at the path you specify (with `@inherit default.pmap` scaffolded)

### What Gets Created on First Run

On first execution, Pseudo creates a home directory at `~/.pseudo/`:

```
~/.pseudo/
  config.json             ← global settings (timeout, max_iter)
  core/
    default.pmap          ← ships with pseudo (auto-updated)
  custom/
    custom.pmap           ← your custom syntax mappings
  cache/
    default.pmap.cache    ← SHA256-invalidated trie cache
  packages/               ← future package manager
```

### File Extensions

| Extension | Use                               |
| --------- | --------------------------------- |
| `.pseudo` | Primary source file               |
| `.psu`    | Short alias — identical behavior  |
| `.pmap`   | Mapping/language definition file  |
| `.pseudo` | ❌ Error — common misspelling     |
| `.py`     | ❌ Error — that looks like Python |

---

## ⚡ Quick Start

**1. Create `hello.pseudo`:**

```pseudo
name = "world"
print "Hello, {name}!"
```

**2. Run it:**

```bash
pseudo run hello.pseudo
# Hello, world!
```

**3. Try an algorithm:**

```pseudo
func bubbleSort(arr)
    for i from 0 to len(arr)
        for j from 0 to len(arr) - i - 1
            if arr[j] > arr[j+1]
                swap arr[j] and arr[j+1]
    return arr

bubbleSort([5, 3, 8, 1, 9, 2])
```

```bash
pseudo run sort.pseudo
# [1, 2, 3, 5, 8, 9]
```

**4. Step through it (educational debugger):**

```bash
pseudo run sort.pseudo --step
```

The `--step` flag pauses at each line and prints the full variable state. Perfect for understanding how an algorithm progresses.

### Auto-print Behavior

A bare expression or function call at any indent level **automatically prints** its value — no `print` required everywhere:

```pseudo
x = 42
x           # → prints 42

arr = [1, 2, 3]
len(arr)    # → prints 3
```

---

## 🛠 CLI Reference

### Commands

| Command                  | Description                                     |
| ------------------------ | ----------------------------------------------- |
| `pseudo run <file>`      | Run a `.pseudo` or `.psu` file                  |
| `pseudo validate <file>` | Validate source or `.pmap` file without running |
| `pseudo explain <line>`  | Show what a line of pseudo maps to internally   |
| `pseudo init`            | Create a `custom.pmap` and `pseudo.config`      |
| `pseudo version`         | Print the installed version                     |

---

### `pseudo run` — All Flags

| Flag              | Type        | Default    | Description                                                           |
| ----------------- | ----------- | ---------- | --------------------------------------------------------------------- |
| `--lang <file>`   | path        | —          | Use a specific `.pmap` instead of auto-detected                       |
| `-i <input>`      | string/file | —          | Inline input or input file (repeatable). Use `\n` for multiple values |
| `--analyze`       | flag        | off        | Show Big-O complexity analysis after run                              |
| `--explain`       | flag        | off        | With `--analyze`: show reasoning for complexity                       |
| `--summary`       | flag        | off        | With `--analyze`: one-line output                                     |
| `--timeout <N>`   | float       | 5.0        | Execution timeout in seconds (`0` = unlimited)                        |
| `--max-iter <N>`  | int         | 10,000,000 | Maximum loop iterations before halting                                |
| `--dry-run`       | flag        | off        | Show mapping resolution — do not execute                              |
| `--step`          | flag        | off        | Step through line-by-line (educational debugger)                      |
| `--no-auto-print` | flag        | off        | Disable automatic printing of standalone expressions                  |

---

### CLI Usage Examples

**Basic run:**

```bash
pseudo run algorithm.pseudo
```

**Pass input values:**

```bash
pseudo run greet.pseudo -i "Alice"
pseudo run greet.pseudo -i "Alice\n25"    # multiple inputs
pseudo run greet.pseudo -i inputs.txt     # from file
```

**Use a custom pmap language:**

```bash
pseudo run algo.pseudo --lang custom.pmap
pseudo run algo.pseudo --lang ~/my_lang.pmap
```

**Dry run — inspect pattern mapping:**

```bash
pseudo run sort.pseudo --dry-run
```

```
  Line 1:  "func bubbleSort(arr)"
           → FUNC_DEF: name=bubbleSort, args=[arr]

  Line 2:  "    for i from 0 to len(arr)"
           → FOR_LOOP: var=i, start=0, end=len(arr)

No errors found. Safe to run.
```

**Complexity analysis:**

```bash
pseudo run sort.pseudo --analyze
```

```
Time:  O(n²)
Space: O(1)
```

**Explain a mapping:**

```bash
pseudo explain "for i from 0 to n"
```

```
  Using: default.pmap

  Matched pattern : 'for {var:name} from {start:expr} to {end:expr}'
  Canonical form  : FOR_LOOP
  Captures        :
    {var} = 'i'
    {start} = '0'
    {end} = 'n'
```

**List all patterns for a canonical:**

```bash
pseudo explain --list FOR_LOOP
```

**Validate a `.pmap` file:**

```bash
pseudo validate custom.pmap
# Validating custom.pmap...
#   ✓ 12 patterns loaded.
#   No errors found.
```

---

### pmap Resolution Order

When running a file, Pseudo picks the `.pmap` to use in this order:

1. **`--lang` flag** — explicitly specified pmap wins
2. **`pseudo.config`** — local project config in the current directory
3. **`~/.pseudo/custom/custom.pmap`** — your global custom pmap
4. **`~/.pseudo/core/default.pmap`** — the bundled default (English)

---

## 🗺 The PMAP System

The `.pmap` file is the bridge between **any writing style** and Pseudo's internal canonical structures. It is a **data file**, not code — it maps text patterns to canonical structure names.

### How It Works

1. Source line tokens are looked up in a **prefix trie** keyed by the first literal word
2. Only patterns sharing that first token are tested — **O(1) lookup**
3. Each pattern is matched left-to-right: literals must match exactly, placeholders consume tokens greedily
4. Most specific patterns (most literal tokens) are tried first automatically
5. The compiled trie is **cached** (`SHA256` hash-invalidated) as `.pmap.cache`

### Placeholder Types

| Placeholder         | Matches                   |
| ------------------- | ------------------------- |
| `{name:name}`       | Single identifier word    |
| `{value:expr}`      | Full expression           |
| `{n:number}`        | Numeric literal only      |
| `{condition:expr}`  | Boolean expression        |
| `{type:word}`       | Single type keyword       |
| `{collection:expr}` | Iterable expression       |
| `{text:any}`        | Everything to end of line |

### Canonical Internal Structures

These are fixed — built into the compiler. The `.pmap` file maps your syntax to these:

| Canonical                   | Meaning                           |
| --------------------------- | --------------------------------- |
| `FUNC_DEF`                  | Function definition               |
| `FOR_LOOP`                  | Counted iteration with variable   |
| `FOR_EACH`                  | Element iteration over collection |
| `WHILE_LOOP`                | Condition-based loop              |
| `UNTIL_LOOP`                | Loop until condition is true      |
| `IF` / `ELSE_IF` / `ELSE`   | Conditional blocks                |
| `RETURN`                    | Exit function with value          |
| `BREAK` / `CONTINUE`        | Loop control                      |
| `ASSIGN`                    | Variable assignment               |
| `PRINT`                     | Output to terminal                |
| `INPUT`                     | Get value from user (`$input`)    |
| `TRY` / `CATCH` / `FINALLY` | Error handling                    |
| `RAISE`                     | Throw an error                    |
| `GLOBAL`                    | Declare variable as global        |
| `SWAP`                      | Exchange two values               |

### Sample `.pmap` File

```text
@pmap-version 1.0
@pseudo-version >=1.0 <2.0
@language "English"
@author "Your Name"
@inherit default.pmap

[FOR_LOOP]
for {var:name} from {start:expr} to {end:expr} step {step:expr}
for {var:name} from {start:expr} to {end:expr}
loop {var:name} from {start:expr} to {end:expr}

[PRINT]
print {value:expr}
show {value:expr}
say {value:expr}
```

### `.pmap` Metadata Headers

| Header                       | Required | Description                                     |
| ---------------------------- | -------- | ----------------------------------------------- |
| `@pmap-version 1.0`          | ✅ yes   | pmap format version                             |
| `@pseudo-version >=1.0 <2.0` | optional | Compatible compiler range                       |
| `@language "English"`        | optional | Human-readable label                            |
| `@author "name"`             | optional | Attribution                                     |
| `@inherit default.pmap`      | optional | Extend another pmap (your patterns tried first) |
| `@ignore-default`            | optional | Ignore all default.pmap mappings                |

### What the Default pmap Supports

The bundled `default.pmap` maps **English-style** patterns:

```pseudo
# All of these work for IF:
if x > 0
when x > 0
check x > 0
given x > 0

# All of these work for WHILE:
while n > 0
keep going while n > 0
as long as n > 0
loop while n > 0

# All of these work for RETURN:
return result
give back result
output result
send back result

# All of these work for ASSIGN:
x = 5
x := 5
x <- 5
set x to 5
let x be 5
store 5 in x
```

---

## 🧱 Built-in Data Structures

All data structures are available without any import:

| Constructor               | Description            |
| ------------------------- | ---------------------- |
| `Stack()`                 | LIFO stack             |
| `Queue()`                 | FIFO queue             |
| `HashMap()`               | Key-value map          |
| `Set(list)`               | Unordered unique set   |
| `MinHeap()` / `MaxHeap()` | Priority queues        |
| `TreeNode(val)`           | Binary tree node       |
| `ListNode(val)`           | Linked list node       |
| `Graph()`                 | Adjacency-list graph   |
| `linkedList(arr)`         | Linked list from array |

### Data Structure Operations

```pseudo
s = Stack()
push(s, 10)
push(s, 20)
top = peek(s)       # 20
val = pop(s)        # 20

q = Queue()
enqueue(q, "a")
enqueue(q, "b")
front = dequeue(q)  # "a"

m = HashMap()
m.put("key", 42)
m.get("key")        # 42
m.has("key")        # true
m.keys()            # ["key"]

g = Graph()
g.addEdge(1, 2)
g.addEdge(2, 3)
g.neighbors(1)      # [2]
```

---

## 📚 Built-in Functions

### List Operations

| Function                                         | Description                     |
| ------------------------------------------------ | ------------------------------- |
| `len(arr)`                                       | Length of list or string        |
| `append(arr, item)`                              | Add to end                      |
| `prepend(arr, item)`                             | Add to front                    |
| `remove(arr, item)`                              | Remove first occurrence         |
| `pop(arr)` / `pop(arr, i)`                       | Remove & return last / at index |
| `insert(arr, i, item)`                           | Insert at index                 |
| `sort(arr)`                                      | Sort in place                   |
| `sorted(arr)`                                    | New sorted list                 |
| `reverse(arr)` / `reversed(arr)`                 | In-place / new reversed         |
| `sum(arr)` / `min(arr)` / `max(arr)`             | Aggregates                      |
| `range(n)` / `range(s, e)` / `range(s, e, step)` | Integer ranges                  |
| `flatten(arr)`                                   | Flatten nested lists            |
| `zip(a, b)`                                      | Zip two lists                   |
| `enumerate(arr)`                                 | `[[i, val], ...]` pairs         |

### String Operations

| Function                                   | Description                   |
| ------------------------------------------ | ----------------------------- |
| `upper(s)` / `lower(s)`                    | Case conversion               |
| `strip(s)`                                 | Remove surrounding whitespace |
| `split(s)` / `split(s, delim)`             | Split to list                 |
| `join(arr, delim)`                         | Join list to string           |
| `replace(s, old, new)`                     | Substring replace             |
| `contains(s, sub)`                         | Substring check               |
| `startswith(s, p)` / `endswith(s, p)`      | Prefix/suffix check           |
| `substring(s, start, end)`                 | Slice by index                |
| `ord(c)` / `chr(n)`                        | ASCII conversion              |
| `isdigit(s)` / `isalpha(s)` / `isalnum(s)` | Character type check          |

### Math Functions

| Function                                       | Description            |
| ---------------------------------------------- | ---------------------- |
| `abs(x)` / `round(x)` / `floor(x)` / `ceil(x)` | Rounding               |
| `sqrt(x)` / `pow(x, n)`                        | Power/root             |
| `log(x)` / `log2(x)` / `log10(x)`              | Logarithms             |
| `sin(x)` / `cos(x)` / `tan(x)`                 | Trigonometry (radians) |
| `gcd(a, b)` / `lcm(a, b)`                      | Integer math           |
| `factorial(n)`                                 | `n!`                   |
| `pi` / `e`                                     | Constants              |

### Type Functions

| Function                                                      | Description                                                     |
| ------------------------------------------------------------- | --------------------------------------------------------------- |
| `int(x)` / `float(x)` / `str(x)` / `bool(x)`                  | Type conversion                                                 |
| `is_number(x)` / `is_string(x)` / `is_list(x)` / `is_null(x)` | Type checking                                                   |
| `type(x)`                                                     | Returns `"number"`, `"string"`, `"list"`, `"bool"`, or `"null"` |

---

## 📚 Examples

### Bubble Sort

```pseudo
func bubbleSort(arr)
    for i from 0 to len(arr)
        for j from 0 to len(arr) - i - 1
            if arr[j] > arr[j+1]
                swap arr[j] and arr[j+1]
    return arr

bubbleSort([5, 2, 9, 1, 7, 3])
# [1, 2, 3, 5, 7, 9]
```

### Binary Search

```pseudo
func binarySearch(arr, target)
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

binarySearch([1, 3, 5, 7, 9, 11, 13], 7)
# 3
```

### Fibonacci with Memoization (HashMap)

```pseudo
map = HashMap()

recursive fib(n)
    if n <= 1: return n
    if map.has(n): return map.get(n)
    result = fib(n-1) + fib(n-2)
    map.put(n, result)
    return result

fib(30)
# 832040
```

### BFS — Breadth-First Search

```pseudo
func bfs(graph, start)
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

bfs(g, 1)
# [1, 2, 3, 4]
```

### Two Sum (HashMap — O(n))

```pseudo
func twoSum(nums, target)
    seen = HashMap()
    for i from 0 to len(nums)
        complement = target - nums[i]
        if seen.has(complement)
            return [seen.get(complement), i]
        seen.put(nums[i], i)
    return []

twoSum([2, 7, 11, 15], 9)
# [0, 1]
```

### Merge Sort

```pseudo
func merge(left, right)
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

mergeSort([8, 3, 1, 5, 2, 9, 4, 7])
# [1, 2, 3, 4, 5, 7, 8, 9]
```

> 💡 Run any example with `--step` to see every assignment happen interactively.  
> Add `--analyze` to get automatic Big-O analysis: `pseudo run merge_sort.pseudo --analyze`

---

## 🏗 Architecture

Pseudo is a **7-stage compilation pipeline**:

```
Source (.pseudo)
      │
      ▼
1. Indentation Parser      → parse_indentation() / build_block_tree()
      │                       Handles tab/space, inline colon blocks (if x: print)
      ▼
2. Pass 1 — Registration   → run_registration_pass()
      │                       Scans entire file for function/variable definitions
      │                       Builds symbol table BEFORE any execution
      ▼
3. PMAP Loader             → PmapLoader.load()
      │                       Parses .pmap, builds prefix trie
      │                       Handles @inherit, @replace, @context
      │                       Cache: SHA256 hash invalidation
      ▼
4. Pass 2 — Resolver       → MappingResolver.resolve_blocks()
      │                       Matches each line against trie patterns
      │                       Parses expressions via recursive descent
      │                       Builds canonical AST (ProgramNode)
      ▼
5. Semantic Analyzer       → SemanticAnalyzer.analyze()
      │                       Validates undefined vars/functions
      │                       Checks argument counts, generates warnings
      ▼
6. Interpreter             → Interpreter.run()
      │                       Tree-walking execution
      │                       Scope management (Scope chain)
      │                       Built-in resolution, auto-print, step mode, timeout
      ▼
7. (optional) Complexity   → ComplexityEngine.analyze()
                              Static Big-O analysis
                              Walks AST for loop nesting, recursion, space
```

### Two-Pass Parsing

Pseudo uses two passes to support mutual recursion and forward references:

| Pass                      | What it does                                                                                                                       |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| **Pass 1** — Registration | Scans the entire file. Registers all function names and global variables into the symbol table. No execution, no `.pmap` matching. |
| **Pass 2** — Resolver     | With the full symbol table available, resolves every line via `.pmap` pattern matching and builds the canonical AST.               |

### Scope Chain

The interpreter maintains a chain of `Scope` objects:

- **Global scope** — top-level variables and functions
- **Local scope** — created per function call; parent is always global
- Reads walk up the chain; writes stay local unless `global` is declared
- Recursion limit: **1,000 call stack depth**

### Prefix Trie + Cache

All patterns are compiled into a prefix trie keyed by the first literal token. For a line starting with `for`, only patterns starting with `for` are tested — **O(1) trie lookup**, then **O(small subset)** linear pattern check. The compiled trie is cached as `.pmap.cache` and automatically invalidated when the `.pmap` SHA256 hash changes.

### File Map

| File                                | Purpose                              | ~Lines |
| ----------------------------------- | ------------------------------------ | ------ |
| `pseudo/__init__.py`                | Package entry, version export        | 4      |
| `pseudo/parser/tokenizer.py`        | Lexer — character → tokens           | 266    |
| `pseudo/parser/normalizer.py`       | Whitespace normalization             | 56     |
| `pseudo/parser/indent_parser.py`    | Indentation + block tree             | 300    |
| `pseudo/parser/ast_nodes.py`        | All AST dataclass definitions        | 293    |
| `pseudo/parser/expr_parser.py`      | Recursive descent expression parser  | 577    |
| `pseudo/data/default.pmap`          | Bundled default English mappings     | 163    |
| `pseudo/resolver/pmap_loader.py`    | `.pmap` parser + prefix trie + cache | 706    |
| `pseudo/resolver/pass1_register.py` | Function/variable registration       | 199    |
| `pseudo/resolver/pass2_resolver.py` | Pattern matching → AST               | 988    |
| `pseudo/analyzer/semantic.py`       | Static validation + warnings         | 320    |
| `pseudo/interpreter/interpreter.py` | Tree-walking executor                | 1,018  |
| `pseudo/interpreter/builtins_ds.py` | DS classes (Stack, Queue, etc.)      | 421    |
| `pseudo/analyzer/complexity.py`     | Big-O static analysis                | 611    |
| `pseudo/compiler.py`                | Pipeline glue + error handling       | 256    |
| `pseudo/cli.py`                     | argparse CLI entry point             | 293    |
| `pseudo/install.py`                 | `~/.pseudo/` home setup              | 88     |

---

## 🌐 Language Design

### The Only Strict Rule: Indentation

Indentation defines code blocks. Use spaces or tabs — but be **consistent within a file**. Inline colon syntax is also supported:

```pseudo
# Block form
if x > 0
    print "positive"

# Inline form (equivalent)
if x > 0: print "positive"
```

### Dynamic Typing

No type declarations. Types change freely:

```pseudo
x = 42
x = "now a string"
x = [1, 2, 3]
```

### String Interpolation

```pseudo
name = "Alice"
age = 30
print "Hello, {name}! You are {age} years old."
```

### Error Handling

```pseudo
try
    result = 10 / 0
catch ZeroDivisionError
    print "Cannot divide by zero"
finally
    print "Done"
```

### Ternary Expressions

```pseudo
label = "even" ? x % 2 == 0 : "odd"
```

### Input

```pseudo
name = $input                        # raw string
age  = $input as int                 # typed
city = $input("Enter your city:")    # with prompt
```

---

## 🔧 Custom Languages

Create a completely custom language by writing your own `.pmap`:

```bash
pseudo init
# Creates pseudo.config + custom.pmap in the current directory
```

**Example — adding a `go through` loop:**

```text
@pmap-version 1.0
@language "MyLang"
@inherit default.pmap

[FOR_LOOP]
go through {var:name} from {start:expr} to {end:expr}
count {var:name} from {start:expr} until {end:expr}

[PRINT] @replace
yell {value:expr}
scream {value:expr}
```

Now `go through i from 0 to 10` and `yell result` work in your project.

---

## 🚫 What Pseudo is NOT

- ❌ A language for building software applications
- ❌ A replacement for Python, Java, C++, etc.
- ❌ A language for file I/O, networking, async, or OOP
- ❌ A production language

---

## 🏭 Building & Releasing

Binaries for all platforms are built automatically by **GitHub Actions** when a version tag is pushed. There is no cross-compilation — each platform's runner builds its own native binary.

### How to release a new version

```bash
# 1. Bump the version in pseudo/__init__.py
#    __version__ = "1.0.1"

# 2. Commit and tag
git add .
git commit -m "chore: release v1.0.1"
git tag v1.0.1
git push && git push --tags
```

The workflow (`.github/workflows/release.yml`) then:

| Step            | What happens                                                                                      |
| --------------- | ------------------------------------------------------------------------------------------------- |
| **Build** (×4)  | Runs in parallel on `windows-latest`, `macos-13` (Intel), `macos-latest` (ARM64), `ubuntu-latest` |
| **PyInstaller** | Each runner builds a self-contained binary — Python runtime bundled inside                        |
| **Smoke test**  | Each binary runs `pseudo version` to confirm it works                                             |
| **Release**     | Creates a GitHub Release with all 4 binaries attached                                             |

### Output binaries

| Binary                   | Platform            |
| ------------------------ | ------------------- |
| `pseudo-windows-x64.exe` | Windows 10/11 x64   |
| `pseudo-macos-x64`       | macOS Intel         |
| `pseudo-macos-arm64`     | macOS Apple Silicon |
| `pseudo-linux-x64`       | Linux x86-64        |

> The install scripts at `pseudo.wiki/install.ps1` and `pseudo.wiki/install.sh` always download from the **latest** GitHub Release tag.

---

## 📄 License

MIT © [Sanay George Varghese](https://github.com/sanayvarghese)

---

<div align="center">

**Pseudo** · Write pseudocode. Actually run it.

</div>
