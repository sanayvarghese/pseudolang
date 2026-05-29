import type { Metadata } from "next";
import CodeBlock from "../components/CodeBlock";

export const metadata: Metadata = { title: "CLI Reference" };

export default function CliPage() {
  return (
    <>
      <div className="topbar">
        <span className="topbar-title">
          CLI Reference › <span>Commands &amp; Flags</span>
        </span>
        <span className="topbar-badge">v0.1</span>
      </div>
      <div className="page">
        <div className="page-hero">
          <span className="page-label">CLI Reference</span>
          <h1 className="page-title">Commands &amp; Flags</h1>
          <p className="page-desc">
            Complete reference for the <code>pseudo</code> command-line
            interface.
          </p>
        </div>

        <h2>Commands</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Command</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <code>pseudo run &lt;file&gt;</code>
                </td>
                <td>
                  Run a <code>.pseudo</code> or <code>.psu</code> file
                </td>
              </tr>
              <tr>
                <td>
                  <code>pseudo validate &lt;file&gt;</code>
                </td>
                <td>
                  Validate a source or <code>.pmap</code> file without running
                </td>
              </tr>
              <tr>
                <td>
                  <code>pseudo explain &lt;line&gt;</code>
                </td>
                <td>Show what a line of pseudo maps to</td>
              </tr>
              <tr>
                <td>
                  <code>pseudo init</code>
                </td>
                <td>Create a custom.pmap and local pseudo.config</td>
              </tr>
              <tr>
                <td>
                  <code>pseudo version</code>
                </td>
                <td>Print the installed version</td>
              </tr>
            </tbody>
          </table>
        </div>

        <h2>pseudo run - Flags</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Flag</th>
                <th>Type</th>
                <th>Default</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              {[
                [
                  "--lang <file>",
                  "path",
                  "-",
                  "Use a specific .pmap file instead of auto-detected",
                ],
                [
                  "-i <input>",
                  "string/file",
                  "-",
                  "Inline input or input file (repeatable). Use \\n for multiple values",
                ],
                [
                  "--analyze",
                  "flag",
                  "off",
                  "Show Big-O complexity analysis after run",
                ],
                [
                  "--explain",
                  "flag",
                  "off",
                  "With --analyze: show reasoning for complexity",
                ],
                ["--summary", "flag", "off", "With --analyze: one-line output"],
                [
                  "--timeout <N>",
                  "float",
                  "5.0",
                  "Execution timeout in seconds (0 = unlimited)",
                ],
                [
                  "--max-iter <N>",
                  "int",
                  "10,000,000",
                  "Maximum loop iterations before halting",
                ],
                [
                  "--dry-run",
                  "flag",
                  "off",
                  "Show mapping resolution - do not execute",
                ],
                [
                  "--step",
                  "flag",
                  "off",
                  "Step through line-by-line (educational debugger)",
                ],
                [
                  "--no-auto-print",
                  "flag",
                  "off",
                  "Disable automatic printing of standalone expressions",
                ],
              ].map(([flag, type, def, desc]) => (
                <tr key={String(flag)}>
                  <td>
                    <span className="flag-name">{flag}</span>
                  </td>
                  <td>
                    <span className="badge blue">{type}</span>
                  </td>
                  <td>
                    <code>{def}</code>
                  </td>
                  <td style={{ color: "var(--fg-muted)" }}>{desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <h2>Examples</h2>
        <h3>Basic run</h3>
        <CodeBlock lang="bash" code="pseudo run algorithm.pseudo" />

        <h3>Pass input values</h3>
        <CodeBlock
          lang="bash"
          code={`pseudo run greet.pseudo -i "Alice"
pseudo run greet.pseudo -i "Alice\\n25"   # multiple inputs
pseudo run greet.pseudo -i inputs.txt    # from file`}
        />

        <h3>Use a custom pmap</h3>
        <CodeBlock
          lang="bash"
          code={`pseudo run algo.pseudo --lang custom.pmap
pseudo run algo.pseudo --lang ~/my_lang.pmap`}
        />

        <h3>Dry run - inspect mapping</h3>
        <CodeBlock
          lang="bash"
          code="pseudo run sort.pseudo --dry-run"
          showOutput={`  Line 1:  "func bubbleSort(arr)"
           → FUNC_DEF: name=bubbleSort, args=[arr]

  Line 2:  "    for i from 0 to len(arr)"
           → FOR_LOOP: var=i, start=0, end=len(arr)

No errors found. Safe to run.`}
        />

        <h3>Complexity analysis</h3>
        <CodeBlock
          lang="bash"
          code="pseudo run sort.pseudo --analyze"
          showOutput={`Time:  O(n²)
Space: O(1)`}
        />

        <h3>Explain a mapping</h3>
        <CodeBlock
          lang="bash"
          code={`pseudo explain "for i from 0 to n"
pseudo explain --list FOR_LOOP`}
          showOutput={`  Using: default.pmap

  Matched pattern : 'for {var:name} from {start:expr} to {end:expr}'
  Canonical form  : FOR_LOOP
  Captures        :
    {var} = 'i'
    {start} = '0'
    {end} = 'n'`}
        />

        <h3>Validate a pmap file</h3>
        <CodeBlock
          lang="bash"
          code="pseudo validate custom.pmap"
          showOutput={`Validating custom.pmap...
  ✓ 12 patterns loaded.
  No errors found.`}
        />

        <h2>pmap Resolution Order</h2>
        <p>
          When running a file, Pseudo picks the <code>.pmap</code> to use in
          this order:
        </p>
        <ol style={{ color: "var(--fg-muted)" }}>
          <li>
            <strong style={{ color: "var(--fg-light)" }}>--lang flag</strong> -
            explicitly specified pmap wins
          </li>
          <li>
            <strong style={{ color: "var(--fg-light)" }}>pseudo.config</strong>{" "}
            - local project config in current directory
          </li>
          <li>
            <strong style={{ color: "var(--fg-light)" }}>
              ~/.pseudo/custom/custom.pmap
            </strong>{" "}
            - your global custom pmap
          </li>
          <li>
            <strong style={{ color: "var(--fg-light)" }}>
              ~/.pseudo/core/default.pmap
            </strong>{" "}
            - the bundled default (English)
          </li>
        </ol>
      </div>
    </>
  );
}
