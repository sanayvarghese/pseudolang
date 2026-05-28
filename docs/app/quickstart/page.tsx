import type { Metadata } from "next";
import CodeBlock from "../components/CodeBlock";

export const metadata: Metadata = { title: "Quick Start" };

const HELLO = `# hello.pseudo
name = "world"
print "Hello, {name}!"`;

const SORT = `func bubbleSort(arr)
    for i from 0 to len(arr)
        for j from 0 to len(arr) - i - 1
            if arr[j] > arr[j+1]
                swap arr[j] and arr[j+1]
    return arr

bubbleSort([5, 2, 9, 1])`;

const FIB = `recursive fibonacci(n)
    if n <= 1: return n
    return fibonacci(n-1) + fibonacci(n-2)

fibonacci(10)`;

export default function QuickstartPage() {
  return (
    <>
      <div className="topbar">
        <span className="topbar-title">
          Getting Started › <span>Quick Start</span>
        </span>
        <span className="topbar-badge">v0.1</span>
      </div>
      <div className="page">
        <div className="page-hero">
          <span className="page-label">Getting Started</span>
          <h1 className="page-title">Quick Start</h1>
          <p className="page-desc">
            Write and run your first Pseudo program in under 2 minutes.
          </p>
        </div>

        <ol className="steps">
          <li>
            <div className="step-num">1</div>
            <div className="step-body">
              <h4>Create a file</h4>
              <p>
                Create a file named <code>hello.pseudo</code>:
              </p>
              <CodeBlock
                code={HELLO}
                lang="pseudo"
                title="hello.pseudo"
                showOutput="Hello, world!"
              />
            </div>
          </li>
          <li>
            <div className="step-num">2</div>
            <div className="step-body">
              <h4>Run it</h4>
              <CodeBlock code="pseudo run hello.pseudo" lang="bash" />
            </div>
          </li>
          <li>
            <div className="step-num">3</div>
            <div className="step-body">
              <h4>Try an algorithm</h4>
              <CodeBlock
                code={SORT}
                lang="pseudo"
                title="sort.pseudo"
                showOutput="[1, 2, 5, 9]"
              />
            </div>
          </li>
          <li>
            <div className="step-num">4</div>
            <div className="step-body">
              <h4>Step through it (educational mode)</h4>
              <CodeBlock code="pseudo run sort.pseudo --step" lang="bash" />
              <p>
                The <code>--step</code> flag pauses at each line and shows
                variable state. Perfect for understanding how an algorithm
                progresses.
              </p>
            </div>
          </li>
          <li>
            <div className="step-num">5</div>
            <div className="step-body">
              <h4>Try recursion</h4>
              <CodeBlock
                code={FIB}
                lang="pseudo"
                title="fib.pseudo"
                showOutput="55"
              />
            </div>
          </li>
        </ol>

        <h2>Auto-print Behavior</h2>
        <p>
          A bare expression or function call at any level automatically prints
          its value — you don't need <code>print</code> everywhere:
        </p>
        <CodeBlock
          lang="pseudo"
          code={`x = 42
x          # → prints 42

arr = [1, 2, 3]
len(arr)   # → prints 3`}
          showOutput={`42\n3`}
        />

        <h2>Key Concepts</h2>
        <div className="card-grid">
          {[
            {
              title: "Indentation defines blocks",
              desc: "The only strict rule. Spaces or tabs — consistent within a file.",
            },
            {
              title: "Flexible keywords",
              desc: "if / when / check / given — all work. Defined by the .pmap file.",
            },
            {
              title: "Dynamic typing",
              desc: "No type declarations. Types change freely like Python.",
            },
            {
              title: "Auto-print",
              desc: "Bare values print automatically. No console.log spam needed.",
            },
          ].map((c) => (
            <div key={c.title} className="card">
              <div className="card-title">{c.title}</div>
              <p className="card-desc">{c.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
