import type { Metadata } from "next";
import CodeBlock from "../components/CodeBlock";

export const metadata: Metadata = { title: "--step Mode" };

const STEP_OUT = `═══ Step 1 ═══════════════════════════════════
  Line: "i = 0"
  Type: ASSIGN
  State: { i: 0 }

═══ Step 2 ═══════════════════════════════════
  Line: "while i < len(arr)"
  Type: WHILE_LOOP  cond = (i < 5) = TRUE
  State: { i: 0 }

[Press Enter to continue, q to quit]`;

const STEP_SWAP = `═══ Step 7 ═══════════════════════════════════
  Line: "swap arr[j] and arr[j+1]"
  Type: SWAP
  Before: arr = [5, 3, 8]
  After:  arr = [3, 5, 8]
  State: { i: 0, j: 0 }

[Press Enter to continue, q to quit]`;

export default function StepModePage() {
  return (
    <>
      <div className="topbar">
        <span className="topbar-title">
          CLI Reference › <span>--step Mode</span>
        </span>
        <span className="topbar-badge">v0.1</span>
      </div>
      <div className="page">
        <div className="page-hero">
          <span className="page-label">CLI Reference</span>
          <h1 className="page-title">--step Mode</h1>
          <p className="page-desc">
            An interactive, educational debugger that walks through your
            algorithm one line at a time, showing live variable state at each
            step.
          </p>
        </div>

        <h2>Usage</h2>
        <CodeBlock lang="bash" code="pseudo run sort.pseudo --step" />

        <h2>How It Works</h2>
        <p>
          When <code>--step</code> is active, the interpreter pauses{" "}
          <strong>before executing each statement</strong> and prints:
        </p>
        <ul>
          <li>
            The <strong>current source line</strong>
          </li>
          <li>
            The <strong>canonical type</strong> (ASSIGN, WHILE_LOOP, SWAP, etc.)
          </li>
          <li>
            The <strong>condition value</strong> for loops and if statements
          </li>
          <li>
            The <strong>full variable state</strong> at that moment
          </li>
          <li>
            For <strong>swaps</strong>: the before and after state of the
            affected array
          </li>
        </ul>

        <h2>Step Output Examples</h2>
        <h3>Assignment and loop</h3>
        <CodeBlock lang="text" title="step output" code={STEP_OUT} />

        <h3>Swap operation</h3>
        <CodeBlock lang="text" title="step output - swap" code={STEP_SWAP} />

        <h2>Controls</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Key</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <code>Enter</code>
                </td>
                <td>Advance to next step</td>
              </tr>
              <tr>
                <td>
                  <code>q</code> + Enter
                </td>
                <td>Quit step mode, stop execution</td>
              </tr>
            </tbody>
          </table>
        </div>

        <h2>Teaching Example</h2>
        <p>
          Step mode is ideal for teaching algorithms. Run a bubble sort step by
          step to watch every comparison and swap:
        </p>
        <CodeBlock
          lang="pseudo"
          title="sort.pseudo"
          code={`func bubbleSort(arr)
    for i from 0 to len(arr)
        for j from 0 to len(arr) - i - 1
            if arr[j] > arr[j+1]
                swap arr[j] and arr[j+1]
    return arr

bubbleSort([5, 2, 9, 1])`}
        />
        <CodeBlock lang="bash" code="pseudo run sort.pseudo --step" />

        <div className="callout info">
          <span className="callout-icon">ℹ</span>
          <div className="callout-body">
            <strong>Special statements</strong>
            Assignments, swaps, and loops get special step output. All other
            statements use a default step view.
          </div>
        </div>

        <h2>Combine with --analyze</h2>
        <p>
          After stepping through, add <code>--analyze</code> to also see the
          Big-O complexity:
        </p>
        <CodeBlock lang="bash" code="pseudo run sort.pseudo --step --analyze" />
      </div>
    </>
  );
}
