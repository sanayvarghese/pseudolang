import type { Metadata } from "next";
import CodeBlock from "../components/CodeBlock";

export const metadata: Metadata = { title: "pseudo.config" };

const CONFIG_JSON = `{
    "pmap": "custom.pmap"
}`;

const CONFIG_ALT = `{
    "pmap": "/home/user/.pseudo/custom/my_lang.pmap"
}`;

export default function ConfigPage() {
  return (
    <>
      <div className="topbar">
        <span className="topbar-title">
          Language Reference › <span>pseudo.config</span>
        </span>
        <span className="topbar-badge">v0.1</span>
      </div>
      <div className="page">
        <div className="page-hero">
          <span className="page-label">Language Reference</span>
          <h1 className="page-title">pseudo.config</h1>
          <p className="page-desc">
            Configure which <code>.pmap</code> to use for a project directory.
          </p>
        </div>

        <h2>What is pseudo.config?</h2>
        <p>
          A <code>pseudo.config</code> file in your current working directory
          tells Pseudo which <code>.pmap</code> file to use automatically —
          without needing to pass <code>--lang</code> every time.
        </p>

        <h2>Format</h2>
        <p>
          JSON format with a single <code>pmap</code> key:
        </p>
        <CodeBlock code={CONFIG_JSON} lang="json" title="pseudo.config" />

        <h2>Path Resolution</h2>
        <p>
          The <code>pmap</code> value is resolved in this order:
        </p>
        <ol style={{ color: "var(--fg-muted)" }}>
          <li>Absolute path — used as-is</li>
          <li>Relative path — resolved from current working directory</li>
          <li>
            <code>~/.pseudo/custom/</code> — looked up by name
          </li>
        </ol>

        <CodeBlock
          code={CONFIG_ALT}
          lang="json"
          title="pseudo.config — absolute path"
        />

        <h2>Creating via pseudo init</h2>
        <CodeBlock lang="bash" code="pseudo init" />
        <p>
          This creates <code>pseudo.config</code> in the current directory and
          links it to the pmap file you specify.
        </p>

        <h2>Config Resolution Priority</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Priority</th>
                <th>Source</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>1st</td>
                <td>
                  <code>--lang</code> flag (explicit override)
                </td>
              </tr>
              <tr>
                <td>2nd</td>
                <td>
                  <code>pseudo.config</code> in current directory
                </td>
              </tr>
              <tr>
                <td>3rd</td>
                <td>
                  <code>.pseudorc</code> in current directory
                </td>
              </tr>
              <tr>
                <td>4th</td>
                <td>
                  <code>~/.pseudo/custom/custom.pmap</code> (if exists)
                </td>
              </tr>
              <tr>
                <td>5th</td>
                <td>
                  <code>~/.pseudo/core/default.pmap</code> (always available)
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="callout tip">
          <span className="callout-icon">💡</span>
          <div className="callout-body">
            <strong>Tip</strong>
            Use <code>pseudo.config</code> at the root of a project to lock in a
            specific language style for all <code>.pseudo</code> files in that
            directory — no flags needed.
          </div>
        </div>

        <h2>Alternative: .pseudorc</h2>
        <p>
          Pseudo also reads <code>.pseudorc</code> as an alternative to{" "}
          <code>pseudo.config</code>. Both formats are accepted — the first one
          found is used.
        </p>
      </div>
    </>
  );
}
