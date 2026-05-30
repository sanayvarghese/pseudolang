import type { Metadata } from "next";
import CodeBlock from "../components/CodeBlock";

export const metadata: Metadata = { title: "VS Code Extension" };

const FEATURE_CARDS = [
  {
    icon: "🎨",
    title: "Syntax Highlighting",
    desc: "Full token-level highlighting for .pseudo, .psu, .pmap, and pseudo.config files — driven dynamically by your active pmap.",
  },
  {
    icon: "✂️",
    title: "Smart Snippets",
    desc: "Every pattern in your pmap becomes a live snippet with tab stops. Custom patterns from pseudo.config appear first.",
  },
  {
    icon: "📖",
    title: "Hover Documentation",
    desc: "Hover any line to see which pmap pattern it matched, what it captures, and complexity metrics for functions.",
  },
  {
    icon: "🔍",
    title: "Inline Diagnostics",
    desc: "Errors and warnings appear inline as you type. No need to run the file to catch mistakes.",
  },
  {
    icon: "📊",
    title: "Complexity CodeLens",
    desc: "Time and space complexity overlays appear above every function definition. Click to see detailed reasoning.",
  },
  {
    icon: "⚡",
    title: "Run from Editor",
    desc: "Run the current file or run with complexity analysis directly from the editor title bar.",
  },
];

export default function VscodeExtensionPage() {
  return (
    <>
      <div className="topbar">
        <span className="topbar-title">
          Getting Started › <span>VS Code Extension</span>
        </span>
        <span className="topbar-badge">v1.1</span>
      </div>
      <div className="page">
        <div className="page-hero">
          <span className="page-label">Editor Support</span>
          <h1 className="page-title">VS Code Extension</h1>
          <p className="page-desc">
            First-class VS Code support for Pseudo — syntax highlighting,
            pmap-driven snippets, inline diagnostics, and complexity analysis,
            all in one extension.
          </p>
        </div>

        {/* Install banner */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 16,
            background: "rgba(184, 152, 112, 0.06)",
            border: "1px solid rgba(184, 152, 112, 0.2)",
            borderRadius: 12,
            padding: "18px 24px",
            marginBottom: 40,
          }}
        >
          <span style={{ fontSize: 28 }}>🧩</span>
          <div style={{ flex: 1 }}>
            <div
              style={{
                fontSize: 14,
                fontWeight: 600,
                color: "var(--fg-light)",
                marginBottom: 4,
              }}
            >
              Pseudo Language Support
            </div>
            <div style={{ fontSize: 13, color: "var(--fg-muted)" }}>
              Publisher:{" "}
              <code style={{ fontSize: 12 }}>sanayvarghese</code> · Extension
              ID:{" "}
              <code style={{ fontSize: 12 }}>
                sanayvarghese.pseudo-syntax
              </code>
            </div>
          </div>
          <a
            href="https://marketplace.visualstudio.com/items?itemName=sanayvarghese.pseudo-syntax"
            target="_blank"
            rel="noreferrer"
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 6,
              background: "var(--accent-warm)",
              color: "#0e0c10",
              fontWeight: 700,
              fontSize: 13,
              padding: "8px 18px",
              borderRadius: 8,
              textDecoration: "none",
              whiteSpace: "nowrap",
              flexShrink: 0,
            }}
          >
            Open in Marketplace ↗
          </a>
        </div>

        {/* Features */}
        <h2>Features</h2>
        <div className="card-grid">
          {FEATURE_CARDS.map((f) => (
            <div className="card" key={f.title}>
              <div className="card-icon">{f.icon}</div>
              <div className="card-title">{f.title}</div>
              <p className="card-desc">{f.desc}</p>
            </div>
          ))}
        </div>

        {/* Install */}
        <h2>Installation</h2>
        <h3>From VS Code</h3>
        <ol className="steps">
          <li>
            <div className="step-num">1</div>
            <div className="step-body">
              <h4>Open the Extensions panel</h4>
              <p>
                Press <code>Ctrl+Shift+X</code> (Windows/Linux) or{" "}
                <code>Cmd+Shift+X</code> (macOS).
              </p>
            </div>
          </li>
          <li>
            <div className="step-num">2</div>
            <div className="step-body">
              <h4>Search for Pseudo</h4>
              <p>
                Type <code>pseudo language support</code> in the search box and
                select the extension published by{" "}
                <strong>sanayvarghese</strong>.
              </p>
            </div>
          </li>
          <li>
            <div className="step-num">3</div>
            <div className="step-body">
              <h4>Click Install</h4>
              <p>The extension activates immediately — no reload required.</p>
            </div>
          </li>
        </ol>

        <h3>From the Command Line</h3>
        <CodeBlock
          lang="bash"
          code={`code --install-extension sanayvarghese.pseudo-syntax`}
        />

        <h3>Manual Install (.vsix)</h3>
        <p>
          Download the <code>.vsix</code> file from the{" "}
          <a
            href="https://github.com/sanayvarghese/pseudolang/releases"
            target="_blank"
            rel="noreferrer"
          >
            GitHub Releases page
          </a>{" "}
          and install via:
        </p>
        <CodeBlock
          lang="bash"
          code={`code --install-extension pseudo-syntax-1.1.0.vsix`}
        />

        {/* File support */}
        <h2>Supported File Types</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>File / Extension</th>
                <th>Language ID</th>
                <th>Support</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <code>.pseudo</code>, <code>.psu</code>
                </td>
                <td>
                  <code>pseudo</code>
                </td>
                <td>
                  Highlighting · Snippets · Hover · Diagnostics · CodeLens ·
                  Run buttons
                </td>
              </tr>
              <tr>
                <td>
                  <code>.pmap</code>
                </td>
                <td>
                  <code>pmap</code>
                </td>
                <td>
                  Highlighting (sections, placeholders, directives, strings)
                </td>
              </tr>
              <tr>
                <td>
                  <code>pseudo.config</code>, <code>.pseudorc</code>
                </td>
                <td>
                  <code>pseudo-config</code>
                </td>
                <td>Highlighting (keys, paths, JSON structure)</td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Dynamic highlighting */}
        <h2>Dynamic Highlighting</h2>
        <p>
          Unlike most language extensions, highlighting in Pseudo is{" "}
          <strong>not hardcoded</strong>. The extension reads your active{" "}
          <code>.pmap</code> file and extracts every keyword from every pattern
          — these become the highlighted tokens in your <code>.pseudo</code>{" "}
          file. If you add a new keyword to your custom pmap, it lights up
          instantly.
        </p>

        <div className="callout info">
          <span className="callout-icon">ℹ</span>
          <div className="callout-body">
            <strong>Live reload</strong> — changing, creating, or deleting any{" "}
            <code>.pmap</code> file, <code>pseudo.config</code>, or{" "}
            <code>.pseudorc</code> automatically re-indexes highlighting and
            snippets without restarting VS Code.
          </div>
        </div>

        {/* Snippets */}
        <h2>pmap-Driven Snippets</h2>
        <p>
          Every pattern line in your active pmap is converted into a VS Code
          snippet. Placeholders like <code>{"{var:name}"}</code> become tab
          stops you can jump between with <kbd>Tab</kbd>.
        </p>
        <CodeBlock
          lang="pmap"
          title="custom.pmap"
          code={`[FOR_LOOP]
for {var:name} from {start:expr} to {end:expr} step {step:expr}
for {var:name} from {start:expr} to {end:expr}`}
        />
        <p>
          When you type <code>for</code> in a <code>.pseudo</code> file, both
          patterns appear as snippet completions — with the cursor pre-placed on{" "}
          <code>var</code>, then <code>start</code>, then <code>end</code> as
          you press <kbd>Tab</kbd>.
        </p>

        <div className="callout tip">
          <span className="callout-icon">💡</span>
          <div className="callout-body">
            <strong>Custom patterns first</strong> — if you have a{" "}
            <code>pseudo.config</code> pointing to a custom pmap, those patterns
            are listed before the defaults in the completion list.
          </div>
        </div>

        {/* Config integration */}
        <h2>pseudo.config Integration</h2>
        <p>
          The extension reads <code>pseudo.config</code> (or{" "}
          <code>.pseudorc</code>) from your workspace root to discover which
          custom <code>.pmap</code> you&apos;re using — the same file the
          runtime reads.
        </p>
        <CodeBlock
          lang="json"
          title="pseudo.config"
          code={`{
  "pmap": "custom.pmap"
}`}
        />
        <p>
          With this in place, the extension merges <strong>custom.pmap</strong>{" "}
          and <strong>default.pmap</strong> — custom keywords and snippets take
          priority.
        </p>

        {/* Hover & CodeLens */}
        <h2>Hover &amp; CodeLens</h2>
        <h3>Function hover</h3>
        <p>
          Hovering a user-defined function name shows its signature and — if
          you&apos;ve run the file — time and space complexity:
        </p>
        <CodeBlock
          lang="text"
          code={`function bubbleSort(arr)
──────────────────────────────
Complexity Analysis:
  Time Complexity  : O(n²)
  Space Complexity : O(1)`}
        />

        <h3>Pattern hover</h3>
        <p>
          Hovering any other line shows which pmap pattern it matched and what
          values were captured:
        </p>
        <CodeBlock
          lang="text"
          code={`Pseudo Mapping Explanation
──────────────────────────────
Matched: for {var:name} from {start:expr} to {end:expr}
Captures:
  {var}   = "i"
  {start} = "0"
  {end}   = "n"`}
        />

        <h3>Complexity CodeLens</h3>
        <p>
          A one-line complexity summary appears above every function definition
          after running the file. Click it to see the full reasoning in an
          output panel.
        </p>

        {/* Run buttons */}
        <h2>Run Buttons</h2>
        <p>
          Two buttons appear in the editor title bar when a{" "}
          <code>.pseudo</code> file is open:
        </p>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Button</th>
                <th>Command</th>
                <th>What it runs</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>▶ (play)</td>
                <td>
                  <code>Pseudo: Run File</code>
                </td>
                <td>
                  <code>pseudo run &lt;file&gt;</code>
                </td>
              </tr>
              <tr>
                <td>📈 (graph)</td>
                <td>
                  <code>Pseudo: Run with Complexity Analysis</code>
                </td>
                <td>
                  <code>pseudo run &lt;file&gt; --analyze --explain</code>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Requirements */}
        <h2>Requirements</h2>
        <div className="callout warn">
          <span className="callout-icon">⚠️</span>
          <div className="callout-body">
            <strong>Python required for runtime features</strong> — hover
            explanations, diagnostics, CodeLens, and the run buttons all invoke{" "}
            <code>pseudo</code> under the hood. The extension automatically
            detects the Python interpreter from the{" "}
            <strong>ms-python.python</strong> extension if installed, otherwise
            falls back to <code>python</code> on your PATH.
          </div>
        </div>
        <p>
          Syntax highlighting and snippet completions work{" "}
          <strong>without Python</strong> — only the runtime features require
          it.
        </p>

        {/* Links */}
        <h2>Links</h2>
        <div className="card-grid">
          {[
            {
              icon: "🛒",
              title: "VS Code Marketplace",
              desc: "Install directly from the official marketplace.",
              href: "https://marketplace.visualstudio.com/items?itemName=sanayvarghese.pseudo-syntax",
            },
            {
              icon: "📦",
              title: "GitHub Repository",
              desc: "Source code, issues, and pull requests.",
              href: "https://github.com/sanayvarghese/pseudolang",
            },
          ].map((l) => (
            <a
              key={l.title}
              href={l.href}
              target="_blank"
              rel="noreferrer"
              className="card"
              style={{ textDecoration: "none", display: "block" }}
            >
              <div className="card-icon">{l.icon}</div>
              <div className="card-title">{l.title}</div>
              <p className="card-desc">{l.desc}</p>
            </a>
          ))}
        </div>
      </div>
    </>
  );
}
