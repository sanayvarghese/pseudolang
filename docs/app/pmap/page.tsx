import type { Metadata } from "next";
import CodeBlock from "../components/CodeBlock";

export const metadata: Metadata = { title: "How PMAP Works" };

const PMAP_EXAMPLE = `@pmap-version 1.0
@pseudo-version >=1.0 <2.0
@language "English"
@author "Sanay"

[FOR_LOOP]
for {var:name} from {start:expr} to {end:expr} step {step:expr}
for {var:name} from {start:expr} to {end:expr}
loop {var:name} from {start:expr} to {end:expr}

[PRINT]
print {value:expr}
show {value:expr}
say {value:expr}`;

export default function PmapPage() {
  return (
    <>
      <div className="topbar">
        <span className="topbar-title">
          PMAP System › <span>How PMAP Works</span>
        </span>
        <span className="topbar-badge">v0.1</span>
      </div>
      <div className="page">
        <div className="page-hero">
          <span className="page-label">The PMAP System</span>
          <h1 className="page-title">How PMAP Works</h1>
          <p className="page-desc">
            The <code>.pmap</code> file is the bridge between any writing style
            and Pseudo's internal canonical structures.
          </p>
        </div>

        <div className="callout info">
          <span className="callout-icon">ℹ</span>
          <div className="callout-body">
            The <code>.pmap</code> is a <strong>data file</strong>, not code. It
            maps text patterns to canonical structure names. The compiler reads
            it, resolves each line, then processes the canonical AST.
          </div>
        </div>

        <h2>Canonical Internal Structures</h2>
        <p>
          These are fixed — they never change. They are the core of Pseudo,
          built into the compiler:
        </p>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Canonical</th>
                <th>Meaning</th>
              </tr>
            </thead>
            <tbody>
              {[
                ["FUNC_DEF", "Function definition"],
                ["FOR_LOOP", "Counted iteration with variable"],
                ["FOR_EACH", "Element iteration over collection"],
                ["WHILE_LOOP", "Condition-based loop"],
                ["UNTIL_LOOP", "Inverted while — loop until condition true"],
                ["IF", "Condition check"],
                ["ELSE_IF", "Chained condition"],
                ["ELSE", "Fallback block"],
                ["RETURN", "Exit function with value"],
                ["BREAK", "Exit loop"],
                ["CONTINUE", "Skip to next iteration"],
                ["ASSIGN", "Variable assignment"],
                ["PRINT", "Output to terminal"],
                ["INPUT", "Get value from user ($input)"],
                ["TRY / CATCH / FINALLY", "Error handling blocks"],
                ["RAISE", "Throw error"],
                ["GLOBAL", "Declare variable as global"],
                ["SWAP", "Exchange two values"],
              ].map(([c, d]) => (
                <tr key={String(c)}>
                  <td>
                    <code>{c}</code>
                  </td>
                  <td>{d}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <h2>Pattern Matching — No Regex</h2>
        <p>
          Pattern matching uses a custom token matcher, not regex. This prevents
          catastrophic backtracking entirely.
        </p>

        <h3>Algorithm</h3>
        <CodeBlock
          lang="text"
          title="pseudocode"
          code={`token_match(pattern_tokens, input_tokens):
  while pattern not exhausted and input not exhausted:
    if current pattern token is LITERAL:
      if it matches input token → advance both
      else → NO_MATCH (fail fast)
    if current pattern token is PLACEHOLDER:
      collect tokens until next literal or stop-token
      save to captures

  if all pattern tokens consumed → MATCH(captures)
  else → NO_MATCH`}
        />
        <p>
          Time: <strong>O(tokens in line)</strong>. No backtracking possible.
        </p>

        <h2>Pattern Specificity</h2>
        <p>
          More specific patterns (more literal tokens) are tried first
          automatically:
        </p>
        <CodeBlock
          lang="text"
          code={`# specificity = 4 (for, from, to, step) — tried first
for {var:name} from {start:expr} to {end:expr} step {step:expr}

# specificity = 3 (for, from, to) — tried second
for {var:name} from {start:expr} to {end:expr}`}
        />

        <h2>Resolution Order (per line)</h2>
        <ol style={{ color: "var(--fg-muted)" }}>
          {[
            "Is it a comment?  → COMMENT, done",
            "Is it a function DEF? → check name(args) + indented body below",
            "Is it a function CALL? → check symbol table from pass 1",
            "Is it a builtin call? → check builtin name list",
            "Run .pmap lookup → canonical structure match",
            "Is it an expression? → expression evaluator",
            "Nothing matched → error with suggestions",
          ].map((s, i) => (
            <li key={i} style={{ marginBottom: 6 }}>
              {s}
            </li>
          ))}
        </ol>

        <h2>A .pmap File</h2>
        <CodeBlock code={PMAP_EXAMPLE} lang="text" title="example.pmap" />

        <h2>Metadata Headers</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Header</th>
                <th>Required</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <code>@pmap-version 1.0</code>
                </td>
                <td>
                  <span className="badge green">yes</span>
                </td>
                <td>pmap format version</td>
              </tr>
              <tr>
                <td>
                  <code>@pseudo-version &gt;=1.0 &lt;2.0</code>
                </td>
                <td>
                  <span className="badge">optional</span>
                </td>
                <td>Compatible compiler version range</td>
              </tr>
              <tr>
                <td>
                  <code>@language "English"</code>
                </td>
                <td>
                  <span className="badge">optional</span>
                </td>
                <td>Human-readable label</td>
              </tr>
              <tr>
                <td>
                  <code>@author "name"</code>
                </td>
                <td>
                  <span className="badge">optional</span>
                </td>
                <td>Attribution</td>
              </tr>
              <tr>
                <td>
                  <code>@inherit default.pmap</code>
                </td>
                <td>
                  <span className="badge">optional</span>
                </td>
                <td>Inherit and extend another pmap</td>
              </tr>
              <tr>
                <td>
                  <code>@ignore-default</code>
                </td>
                <td>
                  <span className="badge">optional</span>
                </td>
                <td>Ignore all default.pmap mappings</td>
              </tr>
            </tbody>
          </table>
        </div>

        <h2>Fallback Chain</h2>
        <p>When no pattern matches, Pseudo falls through:</p>
        <ol style={{ color: "var(--fg-muted)" }}>
          <li>
            <strong style={{ color: "var(--fg-light)" }}>@inherit chain</strong>{" "}
            — custom.pmap → default.pmap → core
          </li>
          <li>
            <strong style={{ color: "var(--fg-light)" }}>
              Expression fallback
            </strong>{" "}
            — try expression evaluator if operators/calls found
          </li>
          <li>
            <strong style={{ color: "var(--fg-light)" }}>
              Name resolution
            </strong>{" "}
            — single identifier → look up → auto-print or NameError
          </li>
          <li>
            <strong style={{ color: "var(--fg-light)" }}>Helpful error</strong>{" "}
            — suggests matching patterns
          </li>
        </ol>

        <h2>Trie + Cache</h2>
        <p>
          For performance, Pseudo builds a prefix trie from the first literal
          token of each pattern. Only patterns starting with the same token as
          the input line are checked — <code>O(1)</code> trie lookup +{" "}
          <code>O(small subset)</code> pattern check.
        </p>
        <p>
          The compiled trie is cached as <code>.pmap.cache</code> and
          invalidated automatically when the <code>.pmap</code> SHA256 hash
          changes.
        </p>
      </div>
    </>
  );
}
