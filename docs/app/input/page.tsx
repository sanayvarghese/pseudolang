import type { Metadata } from "next";
import CodeBlock from "../components/CodeBlock";

export const metadata: Metadata = { title: "$input System" };

export default function InputPage() {
  return (
    <>
      <div className="topbar">
        <span className="topbar-title">
          Language Reference › <span>$input System</span>
        </span>
        <span className="topbar-badge">v0.1</span>
      </div>
      <div className="page">
        <div className="page-hero">
          <span className="page-label">Language Reference</span>
          <h1 className="page-title">$input System</h1>
          <p className="page-desc">
            Read user input interactively or via inline values and files.
          </p>
        </div>

        <h2>Syntax Forms</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Syntax</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <code>$input</code>
                </td>
                <td>Read a value, auto-detect type</td>
              </tr>
              <tr>
                <td>
                  <code>$input as number</code>
                </td>
                <td>Read and convert to number</td>
              </tr>
              <tr>
                <td>
                  <code>$input as string</code>
                </td>
                <td>Read as string</td>
              </tr>
              <tr>
                <td>
                  <code>$input as list</code>
                </td>
                <td>Read as list</td>
              </tr>
              <tr>
                <td>
                  <code>$input as bool</code>
                </td>
                <td>Read as boolean</td>
              </tr>
              <tr>
                <td>
                  <code>$input("prompt")</code>
                </td>
                <td>Show prompt, then read</td>
              </tr>
              <tr>
                <td>
                  <code>$input("prompt") as number</code>
                </td>
                <td>Show prompt with typed input</td>
              </tr>
            </tbody>
          </table>
        </div>

        <h3>Type keywords accepted</h3>
        <p>
          <code>number</code>, <code>string</code>, <code>list</code>,{" "}
          <code>bool</code>, <code>int</code>, <code>float</code>,{" "}
          <code>text</code>
        </p>

        <h2>Examples</h2>
        <CodeBlock
          lang="pseudo"
          code={`name = $input("Enter your name:")
age = $input("Enter age:") as number

print "Hello, {name}! You are {age} years old."`}
          showOutput={`? Enter your name: → Alice
? Enter age: → 25
Hello, Alice! You are 25 years old.`}
        />

        <h2>Auto Type Detection</h2>
        <p>
          When no type is specified, <code>$input</code> auto-detects:
        </p>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Input received</th>
                <th>Detected type</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <code>"42"</code>
                </td>
                <td>
                  number → <code>42</code>
                </td>
              </tr>
              <tr>
                <td>
                  <code>"true"</code>
                </td>
                <td>
                  bool → <code>true</code>
                </td>
              </tr>
              <tr>
                <td>
                  <code>"hello"</code>
                </td>
                <td>
                  string → <code>"hello"</code>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <h2>Inline Input (-i flag)</h2>
        <p>Pass inputs without interactive prompts:</p>
        <CodeBlock
          lang="bash"
          code={`# Single value
pseudo run greet.pseudo -i "Alice"

# Multiple values (\\n separates them)
pseudo run greet.pseudo -i "Alice\\n25\\nengineer"

# From a file
pseudo run greet.pseudo -i inputs.txt`}
        />
        <p>
          Each <code>$input</code> call consumes the next value in order.
        </p>

        <h3>inputs.txt example</h3>
        <CodeBlock
          lang="text"
          title="inputs.txt"
          code={`Alice
25
engineer`}
        />

        <h2>Repeatable -i</h2>
        <CodeBlock
          lang="bash"
          code={`pseudo run program.pseudo -i "Alice" -i "25" -i "engineer"`}
        />

        <h2>Input Exhaustion Error</h2>
        <p>
          If <code>$input</code> is called but no more inputs are available:
        </p>
        <CodeBlock
          lang="text"
          code={`✗ Runtime Error: Expected input #4 but no more inputs available.
     Line 12: score = $input`}
        />
      </div>
    </>
  );
}
