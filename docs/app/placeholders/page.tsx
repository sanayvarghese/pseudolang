import type { Metadata } from "next";
import CodeBlock from "../components/CodeBlock";

export const metadata: Metadata = { title: "Placeholder Types" };

export default function PlaceholdersPage() {
  return (
    <>
      <div className="topbar">
        <span className="topbar-title">
          PMAP System › <span>Placeholder Types</span>
        </span>
        <span className="topbar-badge">v0.1</span>
      </div>
      <div className="page">
        <div className="page-hero">
          <span className="page-label">The PMAP System</span>
          <h1 className="page-title">Placeholder Types</h1>
          <p className="page-desc">
            Every placeholder in a pattern must have a type. No generic untyped
            placeholders allowed.
          </p>
        </div>

        <div className="callout info">
          <span className="callout-icon">ℹ</span>
          <div className="callout-body">
            Syntax: <code>{"{name:type}"}</code> where <code>name</code> is the
            capture variable and <code>type</code> controls what tokens are
            accepted.
          </div>
        </div>

        {/* name */}
        <h2>
          <code>{"{var:name}"}</code> — Single Identifier
        </h2>
        <p>
          Matches a <strong>single word</strong> that is a valid identifier.
        </p>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Matches</th>
                <th>Rejects</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <code>x</code>, <code>arr</code>, <code>myVar</code>,{" "}
                  <code>counter</code>
                </td>
                <td>
                  <code>arr[i]</code>, <code>x+y</code>, <code>len(arr)</code>,{" "}
                  <code>5</code>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <h4>Usage in pattern</h4>
        <CodeBlock
          lang="text"
          code={`for {var:name} from {start:expr} to {end:expr}
#         ↑ must be a single identifier like: i, j, counter`}
        />
        <h4>Example</h4>
        <CodeBlock
          lang="pseudo"
          code={`for i from 0 to 10
#   ↑ captured as {var} = "i"`}
        />

        {/* expr */}
        <h2>
          <code>{"{value:expr}"}</code> — Full Expression
        </h2>
        <p>
          Greedy — collects tokens until a stop-token, keyword, end of line, or
          bracket closes.
        </p>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Matches</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <code>arr[i]+1</code>, <code>len(arr)-1</code>,{" "}
                  <code>x*y+z</code>, <code>5</code>, <code>"hello"</code>,{" "}
                  <code>true</code>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <h4>Example</h4>
        <CodeBlock
          lang="pseudo"
          code={`set result to arr[i] + arr[j] * 2
#           ↑ captured as {value} = "arr[i] + arr[j] * 2"

print len(arr) - 1
#     ↑ captured as {value} = "len(arr) - 1"`}
        />

        {/* number */}
        <h2>
          <code>{"{n:number}"}</code> — Numeric Literal Only
        </h2>
        <p>
          Accepts only a numeric literal. Rejects expressions, variables, and
          function calls.
        </p>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Matches</th>
                <th>Rejects</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <code>5</code>, <code>3.14</code>, <code>-1</code>,{" "}
                  <code>0</code>
                </td>
                <td>
                  <code>x</code>, <code>arr[i]</code>, <code>len(arr)</code>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <h4>Example pattern use</h4>
        <CodeBlock
          lang="text"
          code={`[FOR_LOOP]
for {var:name} from {start:expr} to {end:expr} step {step:expr}
# step here uses :expr to allow negative steps like -1`}
        />

        {/* condition */}
        <h2>
          <code>{"{condition:expr}"}</code> — Boolean Expression
        </h2>
        <p>
          Same as <code>:expr</code> but semantically signals a boolean context.
          Stops at a colon at the end of the line.
        </p>
        <CodeBlock
          lang="pseudo"
          code={`if x > 5 and y != 0
#  ↑ captured as {condition} = "x > 5 and y != 0"

while arr[i] == target
#     ↑ captured as {condition} = "arr[i] == target"`}
        />

        {/* type */}
        <h2>
          <code>{"{type:word}"}</code> — Single Type Keyword
        </h2>
        <p>
          Matches a single keyword indicating a type. Used with{" "}
          <code>$input</code>.
        </p>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Accepted values</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <code>number</code>, <code>string</code>, <code>list</code>,{" "}
                  <code>bool</code>, <code>int</code>, <code>float</code>,{" "}
                  <code>text</code>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <CodeBlock
          lang="pseudo"
          code={`$input as number
#          ↑ captured as {type} = "number"

$input("Enter age:") as int
#                      ↑ captured as {type} = "int"`}
        />

        {/* collection */}
        <h2>
          <code>{"{collection:expr}"}</code> — Iterable Expression
        </h2>
        <p>
          Anything that resolves to an iterable. Functionally identical to{" "}
          <code>:expr</code> but signals iteration context.
        </p>
        <CodeBlock
          lang="pseudo"
          code={`for each item in arr
#                 ↑ {collection} = "arr"

for each x in [1, 2, 3]
#             ↑ {collection} = "[1, 2, 3]"

loop through range(10) as i
#            ↑ {collection} = "range(10)"`}
        />

        {/* any */}
        <h2>
          <code>{"{text:any}"}</code> — Everything to End of Line
        </h2>
        <p>
          Matches <em>everything remaining</em> on the line as a raw string.
          Used for comments, prompts, and free-form text.
        </p>
        <CodeBlock
          lang="pseudo"
          code={`# this is a comment about the algorithm
# ↑ captured as {text} = "this is a comment about the algorithm"

$input("Enter your full name:")
#       ↑ captured as {prompt} = "Enter your full name:"`}
        />

        <h2>Summary Table</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Type</th>
                <th>What it matches</th>
                <th>Typical use</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <code>:name</code>
                </td>
                <td>Single valid identifier</td>
                <td>Variable names, loop vars, function names</td>
              </tr>
              <tr>
                <td>
                  <code>:expr</code>
                </td>
                <td>Full expression (greedy)</td>
                <td>Values, conditions, arithmetic</td>
              </tr>
              <tr>
                <td>
                  <code>:number</code>
                </td>
                <td>Numeric literal only</td>
                <td>Constants, exact counts</td>
              </tr>
              <tr>
                <td>
                  <code>:condition</code> (= <code>:expr</code>)
                </td>
                <td>Boolean expression</td>
                <td>if/while conditions</td>
              </tr>
              <tr>
                <td>
                  <code>:word</code>
                </td>
                <td>Single keyword token</td>
                <td>Type hints in $input</td>
              </tr>
              <tr>
                <td>
                  <code>:collection</code> (= <code>:expr</code>)
                </td>
                <td>Iterable expression</td>
                <td>for-each collections</td>
              </tr>
              <tr>
                <td>
                  <code>:any</code>
                </td>
                <td>Raw text to end of line</td>
                <td>Comments, prompts</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
