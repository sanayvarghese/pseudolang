import type { Metadata } from "next";
import CodeBlock from "../components/CodeBlock";

export const metadata: Metadata = { title: "Language Rules" };

export default function RulesPage() {
  return (
    <>
      <div className="topbar">
        <span className="topbar-title">
          Language Reference › <span>Language Rules</span>
        </span>
        <span className="topbar-badge">v0.1</span>
      </div>
      <div className="page">
        <div className="page-hero">
          <span className="page-label">Language Reference</span>
          <h1 className="page-title">Language Rules</h1>
          <p className="page-desc">
            Variables, types, scope, functions, operators — all the rules in one
            place.
          </p>
        </div>

        <h2>Variables</h2>
        <h3>Naming</h3>
        <ul>
          <li>Must start with a letter or underscore</li>
          <li>Can contain letters, numbers, underscores</li>
          <li>
            Case-sensitive: <code>myVar ≠ myvar ≠ MYVAR</code>
          </li>
          <li>Cannot be a keyword, builtin name, or defined function name</li>
        </ul>

        <h3>Assignment Operators</h3>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Syntax</th>
                <th>Example</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <code>x = 5</code>
                </td>
                <td>Standard equals</td>
              </tr>
              <tr>
                <td>
                  <code>x := 5</code>
                </td>
                <td>Walrus-style</td>
              </tr>
              <tr>
                <td>
                  <code>x {"<-"} 5</code>
                </td>
                <td>Arrow assignment</td>
              </tr>
              <tr>
                <td>
                  <code>set x to 5</code>
                </td>
                <td>English style</td>
              </tr>
              <tr>
                <td>
                  <code>let x be 5</code>
                </td>
                <td>English style</td>
              </tr>
              <tr>
                <td>
                  <code>store 5 in x</code>
                </td>
                <td>English style</td>
              </tr>
              <tr>
                <td>
                  <code>x is 5</code>
                </td>
                <td>Valid only at top level (not inside conditions)</td>
              </tr>
            </tbody>
          </table>
        </div>

        <h3>Types</h3>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Type</th>
                <th>Example</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <code>number</code>
                </td>
                <td>
                  <code>42</code>, <code>3.14</code>, <code>-1</code>
                </td>
                <td>Integers and floats — no distinction</td>
              </tr>
              <tr>
                <td>
                  <code>string</code>
                </td>
                <td>
                  <code>"hello"</code>, <code>'world'</code>
                </td>
                <td>Both quote styles accepted</td>
              </tr>
              <tr>
                <td>
                  <code>bool</code>
                </td>
                <td>
                  <code>true</code>, <code>false</code>
                </td>
                <td>Lowercase only</td>
              </tr>
              <tr>
                <td>
                  <code>null</code>
                </td>
                <td>
                  <code>null</code>
                </td>
                <td>Absence of value</td>
              </tr>
              <tr>
                <td>
                  <code>list</code>
                </td>
                <td>
                  <code>[1, 2, 3]</code>
                </td>
                <td>Ordered, mixed types ok</td>
              </tr>
            </tbody>
          </table>
        </div>

        <h2>Scope</h2>
        <CodeBlock
          lang="pseudo"
          code={`x = 10        # global

myFunc()
    print x   # ✓ reads global (fine)
    x = 20    # creates a NEW local x — does NOT touch global

myFunc()
x             # → still 10`}
        />

        <h3>Global keyword</h3>
        <CodeBlock
          lang="pseudo"
          code={`counter = 0

increment()
    global counter      # explicit declaration
    counter = counter + 1

increment()
increment()
counter               # → 2`}
        />

        <h2>Functions</h2>
        <h3>Definition</h3>
        <CodeBlock
          lang="pseudo"
          code={`# All equivalent function definitions:
bubbleSort(arr)
func bubbleSort(arr)
function bubbleSort(arr)
define bubbleSort(arr)
algorithm bubbleSort(arr)
recursive fibonacci(n)`}
        />

        <h3>Define vs Call</h3>
        <CodeBlock
          lang="pseudo"
          code={`sort(arr)           # CALL — if sort is in symbol table, no body follows
sort(arr)           # DEFINITION — if indented body follows below
sort([3,1,2])       # always CALL — literal argument`}
        />

        <h3>Two-pass parsing</h3>
        <p>
          Pass 1 scans all function names before execution. This enables mutual
          recursion — functions can call each other without forward
          declarations:
        </p>
        <CodeBlock
          lang="pseudo"
          code={`isEven(n)
    if n == 0: return true
    return isOdd(n - 1)

isOdd(n)
    if n == 0: return false
    return isEven(n - 1)

isEven(4)    # → true`}
        />

        <h2>Operators</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Category</th>
                <th>Operators</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Arithmetic</td>
                <td>
                  <code>+ - * / // % **</code> (also <code>^</code> and{" "}
                  <code>power</code>)
                </td>
              </tr>
              <tr>
                <td>Comparison</td>
                <td>
                  <code>
                    {">"} {"<"} {">="} {"<="} == !=
                  </code>{" "}
                  — also <code>greater than</code>, <code>equals</code>, etc.
                </td>
              </tr>
              <tr>
                <td>Logical</td>
                <td>
                  <code>and or not</code> — also <code>&& || !</code>
                </td>
              </tr>
              <tr>
                <td>Ternary</td>
                <td>
                  <code>cond ? true_val : false_val</code>
                </td>
              </tr>
              <tr>
                <td>String</td>
                <td>
                  <code>+</code> concat, <code>*</code> repeat,{" "}
                  <code>str[i]</code>, <code>str[a:b]</code>
                </td>
              </tr>
              <tr>
                <td>List</td>
                <td>
                  <code>+</code> concat, <code>arr[i]</code>,{" "}
                  <code>arr[-1]</code>, <code>arr[a:b]</code>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <h3>Ternary</h3>
        <CodeBlock
          lang="pseudo"
          code={`x = n > 10 ? "big" : "small"
print (n > 0 ? "positive" : "non-positive")`}
        />

        <h2>String Interpolation</h2>
        <CodeBlock
          lang="pseudo"
          code={`name = "Alice"
print "Hello, {name}!"              # → Hello, Alice!
print "Result: {score * 2}"        # → Result: 190
print "Pi: {round(pi, 2)}"         # → Pi: 3.14
# Escape: \\{ \\} → literal braces`}
        />

        <h2>Comments</h2>
        <CodeBlock
          lang="pseudo"
          code={`# single line comment
x = 5   # inline comment

# multi-line: just stack them
# line 1
# line 2`}
        />

        <h2>Indentation</h2>
        <ul>
          <li>
            Spaces <em>or</em> tabs — never mixed in the same file
          </li>
          <li>Any consistent size: 2, 4, or 8 spaces</li>
          <li>
            Mixed tabs/spaces → <code>IndentationError</code>
          </li>
        </ul>

        <h2>Auto-print</h2>
        <CodeBlock
          lang="pseudo"
          code={`x = 42
x              # → prints 42 (bare variable)

len([1,2,3])   # → prints 3 (bare function call)

# These are SILENT:
result = func()   # assignment
x = 5             # assignment`}
        />

        <h2>Error Handling</h2>
        <CodeBlock
          lang="pseudo"
          code={`try
    x = 1 / 0
catch ZeroDivisionError
    print "cannot divide by zero"
finally
    print "this always runs"`}
        />

        <h2>Built-in Error Types</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Error</th>
                <th>When</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <code>ZeroDivisionError</code>
                </td>
                <td>Dividing by zero</td>
              </tr>
              <tr>
                <td>
                  <code>IndexError</code>
                </td>
                <td>List index out of bounds</td>
              </tr>
              <tr>
                <td>
                  <code>TypeError</code>
                </td>
                <td>Wrong type for operation</td>
              </tr>
              <tr>
                <td>
                  <code>ValueError</code>
                </td>
                <td>Right type, wrong value</td>
              </tr>
              <tr>
                <td>
                  <code>NameError</code>
                </td>
                <td>Undefined variable or function</td>
              </tr>
              <tr>
                <td>
                  <code>RecursionError</code>
                </td>
                <td>Max recursion depth (1000) exceeded</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
