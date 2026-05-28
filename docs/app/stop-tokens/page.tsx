import type { Metadata } from "next";
import CodeBlock from "../components/CodeBlock";

export const metadata: Metadata = { title: "Stop Tokens" };

export default function StopTokensPage() {
  return (
    <>
      <div className="topbar">
        <span className="topbar-title">
          PMAP System › <span>Stop Tokens</span>
        </span>
        <span className="topbar-badge">v0.1</span>
      </div>
      <div className="page">
        <div className="page-hero">
          <span className="page-label">The PMAP System</span>
          <h1 className="page-title">Stop Tokens</h1>
          <p className="page-desc">
            How Pseudo knows where an expression ends and the next keyword
            begins.
          </p>
        </div>

        <h2>The Problem</h2>
        <p>In a pattern like:</p>
        <CodeBlock
          lang="text"
          code={`for {var:name} from {start:expr} to {end:expr}`}
        />
        <p>
          How does the matcher know where <code>{"{start:expr}"}</code> ends and{" "}
          <code>to</code> begins?
        </p>
        <p>
          Answer: <strong>stop tokens</strong>. The matcher collects expression
          tokens until it sees a token that is a known keyword (a stop token).
        </p>

        <h2>How Stop Tokens Are Built</h2>
        <ol style={{ color: "var(--fg-muted)" }}>
          <li>
            Pseudo extracts <strong>all literal words</strong> from all patterns
            in the loaded <code>.pmap</code>
          </li>
          <li>
            Builds a global <strong>stop-token set</strong> from those words
          </li>
          <li>
            When matching <code>:expr</code>, tokens are collected until a
            stop-token is seen, the line ends, or brackets close
          </li>
        </ol>

        <h2>Default Stop Tokens</h2>
        <p>
          These come from the literal tokens in <code>default.pmap</code>:
        </p>
        <div
          className="card"
          style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 13,
            lineHeight: 1.8,
          }}
        >
          {`for, from, to, step, in, each, every, while, until, if, when,
check, given, else, otherwise, return, give, back, and, or, not,
as, is, then, loop, repeat, function, func, define, def, procedure`}
        </div>

        <h2>An Expression Stops When</h2>
        <ul>
          <li>A stop-token is found (keyword boundary)</li>
          <li>End of line</li>
          <li>A colon (block opener)</li>
          <li>
            A matching closing bracket <code>)</code> <code>]</code>{" "}
            <code>{"}"}</code>
          </li>
        </ul>

        <h2>Examples</h2>
        <h3>Stop at keyword</h3>
        <CodeBlock
          lang="pseudo"
          code={`for i from 0 to n step 2
#         ↑──────↑ start:expr = "0" — stops at "to"
#                    ↑ end:expr = "n" — stops at "step"
#                           ↑ step:expr = "2"`}
        />

        <h3>Stop at end of line</h3>
        <CodeBlock
          lang="pseudo"
          code={`print arr[i] + arr[j] * 2
#     ↑────────────────────↑ value:expr = "arr[i] + arr[j] * 2"
#     no stop-token → collects to end of line`}
        />

        <h3>Stop at bracket close</h3>
        <CodeBlock
          lang="pseudo"
          code={`$input("Enter name:") as string
#             ↑─────↑ prompt:any = "Enter name:" — stops at )
#                        ↑ type:word = "string"`}
        />

        <h2>Custom PMAP Expands Stop Tokens</h2>
        <p>
          When you add new patterns to a custom <code>.pmap</code>, any new
          literal words you introduce automatically become stop tokens:
        </p>
        <CodeBlock
          lang="text"
          title="custom.pmap"
          code={`[FOR_LOOP]
count {var:name} from {start:expr} until {end:expr}
# "count" and "until" are now stop tokens`}
        />

        <div className="callout warn">
          <span className="callout-icon">⚠</span>
          <div className="callout-body">
            <strong>Be careful with common words</strong>
            If you add a common word like <code>the</code> or <code>of</code> as
            a literal token in a pattern, it becomes a stop token and will
            terminate expressions that contain those words.
          </div>
        </div>
      </div>
    </>
  );
}
