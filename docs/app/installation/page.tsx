import type { Metadata } from "next";
import CodeBlock from "../components/CodeBlock";

export const metadata: Metadata = { title: "Installation" };

export default function InstallationPage() {
  return (
    <>
      <div className="topbar">
        <span className="topbar-title">
          Getting Started › <span>Installation</span>
        </span>
        <span className="topbar-badge">v0.1</span>
      </div>
      <div className="page">
        <div className="page-hero">
          <span className="page-label">Getting Started</span>
          <h1 className="page-title">Installation</h1>
          <p className="page-desc">
            Pseudo ships as a <strong>standalone binary</strong> - no Python, no
            pip, no runtime required. One command and you're running.
          </p>
        </div>

        <div className="callout info">
          <span className="callout-icon">ℹ</span>
          <div className="callout-body">
            <strong>Standalone binary</strong> - the <code>pseudo</code>{" "}
            executable bundles everything it needs internally. Python does{" "}
            <em>not</em> need to be installed on your machine.
          </div>
        </div>

        {/* ── Windows ── */}
        <h2>🪟 Windows</h2>
        <p>
          Open <strong>PowerShell</strong> and run:
        </p>
        <CodeBlock
          lang="powershell"
          code={`iwr -useb https://pseudo.wiki/install.ps1 | iex`}
        />
        <p>
          This downloads <code>pseudo.exe</code> from GitHub Releases, places it
          in <code>%LOCALAPPDATA%\Programs\pseudo\</code>, and{" "}
          <strong>adds it to your PATH automatically</strong>. Open a new
          terminal and you're done.
        </p>

        <h3>Manual download</h3>
        <CodeBlock
          lang="powershell"
          code={`# Download install script and run it
curl -o install.ps1 https://pseudo.wiki/install.ps1
.\\install.ps1`}
        />

        <div className="callout tip">
          <span className="callout-icon">💡</span>
          <div className="callout-body">
            <strong>No admin required</strong> - the installer places the binary
            in your user folder and updates your <em>user</em> PATH only.
          </div>
        </div>

        {/* ── macOS ── */}
        <h2>🍎 macOS</h2>
        <CodeBlock
          lang="bash"
          code={`curl -fsSL https://pseudo.wiki/install.sh | bash`}
        />
        <p>
          Installs to <code>~/.local/bin/pseudo</code> and appends the PATH line
          to <code>~/.zshrc</code> (and <code>~/.bash_profile</code>). Supports
          both Intel and Apple Silicon.
        </p>

        <h3>Source the shell config (current session)</h3>
        <CodeBlock lang="bash" code={`source ~/.zshrc`} />

        {/* ── Linux ── */}
        <h2>🐧 Linux</h2>
        <CodeBlock
          lang="bash"
          code={`curl -fsSL https://pseudo.wiki/install.sh | bash`}
        />
        <p>
          Or with <code>wget</code>:
        </p>
        <CodeBlock
          lang="bash"
          code={`wget -qO- https://pseudo.wiki/install.sh | bash`}
        />
        <p>
          Installs to <code>~/.local/bin/pseudo</code> and updates{" "}
          <code>~/.bashrc</code>. Supports x86-64 and ARM64.
        </p>

        <h3>Source the shell config (current session)</h3>
        <CodeBlock lang="bash" code={`source ~/.bashrc`} />

        {/* ── Supported Platforms ── */}
        <h2>Supported Platforms</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Platform</th>
                <th>Binary</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>🪟 Windows x64</td>
                <td>
                  <code>pseudo-windows-x64.exe</code>
                </td>
                <td>Windows 10/11</td>
              </tr>
              <tr>
                <td>🍎 macOS x64</td>
                <td>
                  <code>pseudo-macos-x64</code>
                </td>
                <td>Intel Mac</td>
              </tr>
              <tr>
                <td>🍎 macOS ARM64</td>
                <td>
                  <code>pseudo-macos-arm64</code>
                </td>
                <td>Apple Silicon (M1/M2/M3)</td>
              </tr>
              <tr>
                <td>🐧 Linux x64</td>
                <td>
                  <code>pseudo-linux-x64</code>
                </td>
                <td>Ubuntu, Debian, Fedora, etc.</td>
              </tr>
              <tr>
                <td>🐧 Linux ARM64</td>
                <td>
                  <code>pseudo-linux-arm64</code>
                </td>
                <td>Raspberry Pi, ARM servers</td>
              </tr>
            </tbody>
          </table>
        </div>

        <p>
          All binaries are available on the{" "}
          <a
            href="https://github.com/sanayvarghese/pseudolang/releases"
            style={{ color: "var(--accent-warm)" }}
          >
            GitHub Releases page
          </a>
          .
        </p>

        {/* ── Verify ── */}
        <h2>Verify Installation</h2>
        <CodeBlock
          code="pseudo version"
          lang="bash"
          showOutput="pseudo 0.1.2"
        />

        {/* ── Install via pip (optional) ── */}
        <h2>
          Alternative - pip{" "}
          <span
            style={{ fontWeight: 400, fontSize: 14, color: "var(--fg-muted)" }}
          >
            (if Python 3.8+ is installed)
          </span>
        </h2>
        <CodeBlock code="pip install runpseudo" lang="bash" />
        <CodeBlock code="pip install --upgrade runpseudo" lang="bash" />

        {/* ── Init a Project ── */}
        <h2>Init a Project</h2>
        <p>
          Run inside any directory to create a local config and custom mapping
          file:
        </p>
        <CodeBlock code="pseudo init" lang="bash" />
        <p>This creates:</p>
        <ul>
          <li>
            <code>pseudo.config</code> - local project config (links to your
            pmap)
          </li>
          <li>
            A new or existing <code>.pmap</code> file at the path you specify
          </li>
        </ul>

        {/* ── What Gets Created ── */}
        <h2>What Gets Created on First Run</h2>
        <p>
          On first run, Pseudo creates a home directory at{" "}
          <code>~/.pseudo/</code>:
        </p>
        <CodeBlock
          lang="text"
          title="~/.pseudo/ structure"
          code={`~/.pseudo/
  config.json         ← global settings
  core/
    default.pmap      ← ships with pseudo (read-only)
  custom/
    custom.pmap       ← created by: pseudo init
  cache/
    default.pmap.cache
  packages/           ← future package manager`}
        />

        {/* ── File Extensions ── */}
        <h2>File Extensions</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Extension</th>
                <th>Use</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <code>.pseudo</code>
                </td>
                <td>Primary source file extension</td>
              </tr>
              <tr>
                <td>
                  <code>.psu</code>
                </td>
                <td>Short alias - identical behavior</td>
              </tr>
              <tr>
                <td>
                  <code>.pmap</code>
                </td>
                <td>Mapping file (not source code)</td>
              </tr>
              <tr>
                <td>
                  <code>.pseudo</code>
                </td>
                <td>❌ Error - common misspelling</td>
              </tr>
              <tr>
                <td>
                  <code>.py</code>
                </td>
                <td>❌ Error - that looks like a Python file</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
