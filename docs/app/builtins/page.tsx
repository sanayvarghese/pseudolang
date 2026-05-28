import type { Metadata } from "next";
import CodeBlock from "../components/CodeBlock";

export const metadata: Metadata = { title: "Built-in Functions" };

export default function BuiltinsPage() {
  return (
    <>
      <div className="topbar">
        <span className="topbar-title">
          Built-ins › <span>Built-in Functions</span>
        </span>
        <span className="topbar-badge">v0.1</span>
      </div>
      <div className="page">
        <div className="page-hero">
          <span className="page-label">Built-ins</span>
          <h1 className="page-title">Built-in Functions</h1>
          <p className="page-desc">
            All built-in functions available without import. Call them directly
            in any <code>.pseudo</code> file.
          </p>
        </div>

        {/* List Operations */}
        <h2>List Operations</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Function</th>
                <th>Description</th>
                <th>Example</th>
              </tr>
            </thead>
            <tbody>
              {[
                ["len(arr)", "Length of list", "len([1,2,3]) → 3"],
                ["append(arr, item)", "Add item to end", "append(arr, 5)"],
                ["prepend(arr, item)", "Add item to front", "prepend(arr, 0)"],
                [
                  "remove(arr, item)",
                  "Remove first occurrence",
                  "remove(arr, 3)",
                ],
                ["pop(arr)", "Remove & return last", "pop([1,2,3]) → 3"],
                [
                  "pop(arr, i)",
                  "Remove & return at index i",
                  "pop(arr, 0) → first",
                ],
                [
                  "insert(arr, i, item)",
                  "Insert item at index i",
                  "insert(arr, 1, 99)",
                ],
                ["sort(arr)", "Sort in place", "sort(arr)"],
                [
                  "sorted(arr)",
                  "New sorted list (original unchanged)",
                  "sorted([3,1,2]) → [1,2,3]",
                ],
                ["reverse(arr)", "Reverse in place", "reverse(arr)"],
                [
                  "reversed(arr)",
                  "New reversed list",
                  "reversed([1,2,3]) → [3,2,1]",
                ],
                [
                  "index(arr, item)",
                  "Index of first occurrence (-1 if not found)",
                  "index(arr, 5)",
                ],
                ["count(arr, item)", "Count occurrences", "count(arr, 3)"],
                ["sum(arr)", "Sum all elements", "sum([1,2,3]) → 6"],
                ["min(arr)", "Minimum value", "min([3,1,2]) → 1"],
                ["max(arr)", "Maximum value", "max([3,1,2]) → 3"],
                ["min(a, b)", "Minimum of two values", "min(3, 5) → 3"],
                ["max(a, b)", "Maximum of two values", "max(3, 5) → 5"],
                ["range(n)", "List 0 to n-1", "range(5) → [0,1,2,3,4]"],
                [
                  "range(start, end)",
                  "List start to end-1",
                  "range(2, 5) → [2,3,4]",
                ],
                [
                  "range(start, end, step)",
                  "List with step",
                  "range(0,10,2) → [0,2,4,6,8]",
                ],
                [
                  "flatten(arr)",
                  "Flatten nested list",
                  "flatten([[1,2],[3]]) → [1,2,3]",
                ],
                [
                  "zip(a, b)",
                  "Zip two lists",
                  "zip([1,2],[3,4]) → [[1,3],[2,4]]",
                ],
                [
                  "enumerate(arr)",
                  "List of [i, val] pairs",
                  'enumerate(["a","b"]) → [[0,"a"],[1,"b"]]',
                ],
                ["copy(arr)", "Shallow copy of list", "copy(arr)"],
              ].map(([fn, desc, ex]) => (
                <tr key={String(fn)}>
                  <td>
                    <code>{fn}</code>
                  </td>
                  <td style={{ color: "var(--fg-muted)" }}>{desc}</td>
                  <td
                    style={{
                      color: "var(--fg-muted)",
                      fontSize: 12,
                      fontFamily: "monospace",
                    }}
                  >
                    {ex}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <h3>Example</h3>
        <CodeBlock
          lang="pseudo"
          code={`arr = [5, 2, 8, 1, 9]
sort(arr)
print arr               # → [1, 2, 5, 8, 9]

top3 = sorted(arr, true)[0:3]   # descending, first 3
print top3              # → [9, 8, 5]

print sum(arr)          # → 25
print min(arr)          # → 1
print max(arr)          # → 9`}
        />

        {/* String Operations */}
        <h2>String Operations</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Function</th>
                <th>Description</th>
                <th>Example</th>
              </tr>
            </thead>
            <tbody>
              {[
                ["len(str)", "Length of string", 'len("hello") → 5'],
                ["upper(str)", "Convert to uppercase", 'upper("hi") → "HI"'],
                ["lower(str)", "Convert to lowercase", 'lower("HI") → "hi"'],
                [
                  "strip(str)",
                  "Remove leading/trailing whitespace",
                  'strip("  hi  ") → "hi"',
                ],
                [
                  "split(str)",
                  "Split by whitespace → list",
                  'split("a b c") → ["a","b","c"]',
                ],
                [
                  "split(str, delim)",
                  "Split by delimiter",
                  'split("a,b", ",") → ["a","b"]',
                ],
                [
                  "join(arr, delim)",
                  "Join list into string",
                  'join(["a","b"], ",") → "a,b"',
                ],
                [
                  "replace(str, old, new)",
                  "Replace substring",
                  'replace("hello","l","r") → "herro"',
                ],
                [
                  "contains(str, sub)",
                  "True if substring found",
                  'contains("hello","ell") → true',
                ],
                [
                  "startswith(str, prefix)",
                  "True if starts with prefix",
                  'startswith("hello","he") → true',
                ],
                [
                  "endswith(str, suffix)",
                  "True if ends with suffix",
                  'endswith("hello","lo") → true',
                ],
                [
                  "substring(str, start, end)",
                  "Substring by index range",
                  'substring("hello",1,4) → "ell"',
                ],
                ["ord(str)", "ASCII code of first character", 'ord("A") → 65'],
                ["chr(n)", "Character from ASCII code", 'chr(65) → "A"'],
                ["isdigit(str)", "True if all digits", 'isdigit("123") → true'],
                [
                  "isalpha(str)",
                  "True if all letters",
                  'isalpha("abc") → true',
                ],
              ].map(([fn, desc, ex]) => (
                <tr key={String(fn)}>
                  <td>
                    <code>{fn}</code>
                  </td>
                  <td style={{ color: "var(--fg-muted)" }}>{desc}</td>
                  <td
                    style={{
                      color: "var(--fg-muted)",
                      fontSize: 12,
                      fontFamily: "monospace",
                    }}
                  >
                    {ex}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <h3>Example</h3>
        <CodeBlock
          lang="pseudo"
          code={`s = "Hello, World!"
print upper(s)            # → HELLO, WORLD!
print lower(s)            # → hello, world!
parts = split(s, ", ")
print parts               # → ["Hello", "World!"]
print join(parts, " — ") # → Hello — World!`}
        />

        {/* Math */}
        <h2>Math Functions</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Function / Constant</th>
                <th>Description</th>
                <th>Example</th>
              </tr>
            </thead>
            <tbody>
              {[
                ["abs(x)", "Absolute value", "abs(-5) → 5"],
                ["round(x)", "Round to nearest integer", "round(3.7) → 4"],
                [
                  "round(x, n)",
                  "Round to n decimal places",
                  "round(3.14159, 2) → 3.14",
                ],
                ["floor(x)", "Round down", "floor(3.9) → 3"],
                ["ceil(x)", "Round up", "ceil(3.1) → 4"],
                ["sqrt(x)", "Square root", "sqrt(16) → 4.0"],
                ["pow(x, n)", "x to the power n", "pow(2, 10) → 1024"],
                ["log(x)", "Natural logarithm", "log(e) → 1.0"],
                ["log(x, base)", "Log with given base", "log(8, 2) → 3.0"],
                ["log2(x)", "Base-2 logarithm", "log2(8) → 3.0"],
                ["log10(x)", "Base-10 logarithm", "log10(100) → 2.0"],
                [
                  "sin(x) / cos(x) / tan(x)",
                  "Trigonometric (radians)",
                  "sin(pi/2) → 1.0",
                ],
                ["gcd(a, b)", "Greatest common divisor", "gcd(12, 8) → 4"],
                ["lcm(a, b)", "Least common multiple", "lcm(4, 6) → 12"],
                ["factorial(n)", "n!", "factorial(5) → 120"],
                ["pi", "Constant π = 3.14159...", "—"],
                ["e", "Constant e = 2.71828...", "—"],
              ].map(([fn, desc, ex]) => (
                <tr key={String(fn)}>
                  <td>
                    <code>{fn}</code>
                  </td>
                  <td style={{ color: "var(--fg-muted)" }}>{desc}</td>
                  <td
                    style={{
                      color: "var(--fg-muted)",
                      fontSize: 12,
                      fontFamily: "monospace",
                    }}
                  >
                    {ex}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Type conversion */}
        <h2>Type Conversion</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Function</th>
                <th>Description</th>
                <th>Example</th>
              </tr>
            </thead>
            <tbody>
              {[
                ["int(x)", "Convert to integer", 'int("42") → 42'],
                ["float(x)", "Convert to float", 'float("3.14") → 3.14'],
                ["str(x)", "Convert to string", 'str(42) → "42"'],
                ["list(x)", "Convert to list", "list(range(3)) → [0,1,2]"],
                ["bool(x)", "Convert to boolean", "bool(0) → false"],
              ].map(([fn, desc, ex]) => (
                <tr key={String(fn)}>
                  <td>
                    <code>{fn}</code>
                  </td>
                  <td style={{ color: "var(--fg-muted)" }}>{desc}</td>
                  <td
                    style={{
                      color: "var(--fg-muted)",
                      fontSize: 12,
                      fontFamily: "monospace",
                    }}
                  >
                    {ex}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Type checking */}
        <h2>Type Checking</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Function</th>
                <th>Returns</th>
              </tr>
            </thead>
            <tbody>
              {[
                ["is_number(x)", "true if x is a number"],
                ["is_string(x)", "true if x is a string"],
                ["is_list(x)", "true if x is a list"],
                ["is_bool(x)", "true if x is boolean"],
                ["is_null(x)", "true if x is null"],
                [
                  "type(x)",
                  '"number", "string", "list", "bool", "null", or class name',
                ],
              ].map(([fn, desc]) => (
                <tr key={String(fn)}>
                  <td>
                    <code>{fn}</code>
                  </td>
                  <td style={{ color: "var(--fg-muted)" }}>{desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <h3>Example</h3>
        <CodeBlock
          lang="pseudo"
          code={`x = 42
print type(x)         # → number
print is_number(x)    # → true
print is_string(x)    # → false

y = "hello"
print type(y)         # → string`}
        />

        {/* Utility */}
        <h2>Utility</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Function</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <code>print(x)</code>
                </td>
                <td>Explicit print (also auto-print works)</td>
              </tr>
              <tr>
                <td>
                  <code>assert(cond, msg)</code>
                </td>
                <td>Throw AssertionError if condition is false</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
