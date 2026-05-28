import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import CodeBlock from "./components/CodeBlock";

export const metadata: Metadata = {
  title: "Pseudo — Run Pseudocode as a Real Language",
  description:
    "Pseudo is a programming language for writing and running pseudocode. Ideal for coding interviews, algorithm education, and quick idea verification.",
};

const EXAMPLE = `# Bubble Sort in pseudo
func bubbleSort(arr)
    for i from 0 to len(arr)
        for j from 0 to len(arr) - i - 1
            if arr[j] > arr[j+1]
                swap arr[j] and arr[j+1]
    return arr

result = bubbleSort([5, 3, 8, 1, 9, 2])
print result`;

const OUTPUT = `[1, 2, 3, 5, 8, 9]`;

export default function Home() {
  return (
    <>
      {/* Hero */}
      <div className="hero-section">
        <div className="hero-inner">
          <Image
            src="/logo.png"
            alt="Pseudo"
            width={120}
            height={48}
            style={{ objectFit: "contain", marginBottom: 28 }}
          />
          <h1 className="hero-title">
            Write pseudocode.
            <br />
            <span style={{ color: "var(--accent-warm)" }}>
              Actually run it.
            </span>
          </h1>
          <p
            style={{
              fontSize: 17,
              color: "var(--fg-muted)",
              maxWidth: 560,
              lineHeight: 1.7,
              marginBottom: 32,
            }}
          >
            Pseudo is a language that sits between English prose and real code.
            Flexible syntax via <code>.pmap</code> mappings — any style, any
            language.
          </p>
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            <Link
              href="/installation"
              style={{
                background: "var(--accent-warm)",
                color: "#0e0c10",
                padding: "10px 22px",
                borderRadius: 8,
                fontWeight: 700,
                fontSize: 14,
                textDecoration: "none",
                display: "inline-block",
                transition: "opacity 0.15s",
              }}
            >
              Get Started →
            </Link>
            <Link
              href="/quickstart"
              style={{
                background: "rgba(50,45,56,0.6)",
                color: "var(--fg-light)",
                border: "1px solid var(--bg-border)",
                padding: "10px 22px",
                borderRadius: 8,
                fontWeight: 600,
                fontSize: 14,
                textDecoration: "none",
                display: "inline-block",
              }}
            >
              Quick Start
            </Link>
          </div>
        </div>
      </div>

      <div className="page">
        {/* Feature cards */}
        <div className="card-grid" style={{ marginTop: 0 }}>
          {[
            {
              icon: "🗺",
              title: "PMAP Mappings",
              desc: "Write in any style — English, Python-like, or your own language. Just define a .pmap file.",
            },
            {
              icon: "🧩",
              title: "No Rigid Syntax",
              desc: "Indentation is the only strict rule. Everything else is flexible via pattern matching.",
            },
            {
              icon: "🔍",
              title: "--step Mode",
              desc: "Step through your algorithm line-by-line with full variable state visible at each step.",
            },
            {
              icon: "📦",
              title: "DS Built-in",
              desc: "Stack, Queue, HashMap, MinHeap, Graph — all built in with visual auto-print display.",
            },
          ].map((f) => (
            <div key={f.title} className="card">
              <div className="card-icon">{f.icon}</div>
              <div className="card-title">{f.title}</div>
              <p className="card-desc">{f.desc}</p>
            </div>
          ))}
        </div>

        <h2>A Quick Look</h2>
        <CodeBlock
          code={EXAMPLE}
          lang="pseudo"
          title=".pseudo"
          showOutput={OUTPUT}
        />

        <h2>Position on the Spectrum</h2>
        <div
          className="card"
          style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 13 }}
        >
          <div style={{ color: "var(--fg-muted)", marginBottom: 8 }}>
            100% English prose ←—— Pseudo ——→ Real programming language
          </div>
          <div style={{ color: "var(--fg-muted)" }}>
            "Sort the
            array"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↑&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for(int
            i=0; i&lt;n; i++) {"{"}...{"}"}
          </div>
          <div style={{ color: "var(--accent-warm)", marginTop: 8 }}>
            Pseudo leans toward programming language syntax, not prose.
          </div>
        </div>

        <h2>What Pseudo is NOT</h2>
        <ul>
          <li>A language for building software applications</li>
          <li>A replacement for Python, Java, C++ etc.</li>
          <li>A language for file I/O, networking, async, or OOP</li>
          <li>A production language</li>
        </ul>

        <div className="callout tip">
          <span className="callout-icon">💡</span>
          <div className="callout-body">
            <strong>Target use cases</strong>
            Coding interviews, algorithm verification, teaching algorithms
            step-by-step, and quickly stating ideas in runnable form.
          </div>
        </div>

        <h2>Next Steps</h2>
        <div className="card-grid">
          {[
            {
              href: "/installation",
              title: "Installation",
              desc: "Install via pip and set up your environment.",
            },
            {
              href: "/quickstart",
              title: "Quick Start",
              desc: "Write and run your first .pseudo file.",
            },
            {
              href: "/pmap",
              title: "PMAP System",
              desc: "Understand the core mapping mechanism.",
            },
            {
              href: "/examples",
              title: "Examples",
              desc: "See real algorithms written in pseudo.",
            },
          ].map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className="card"
              style={{ display: "block", textDecoration: "none" }}
            >
              <div className="card-title">{l.title} →</div>
              <p className="card-desc">{l.desc}</p>
            </Link>
          ))}
        </div>
      </div>
    </>
  );
}
