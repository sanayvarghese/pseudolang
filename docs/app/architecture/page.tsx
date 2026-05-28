import type { Metadata } from "next";
import CodeBlock from "../components/CodeBlock";

export const metadata: Metadata = { title: "Compiler Architecture" };

const PIPELINE = `Source (.pseudo)
      │
      ▼
1. Indentation Parser      → parse_indentation() / build_block_tree()
      │                       Handles tab/space, inline colon blocks
      ▼
2. Pass 1 — Registration   → run_registration_pass()
      │                       Scans for function/variable definitions
      │                       Builds symbol table before execution
      ▼
3. PMAP Loader             → PmapLoader.load()
      │                       Parses .pmap, builds prefix trie
      │                       Handles @inherit, @replace, @context
      │                       Cache: SHA256 hash invalidation
      ▼
4. Pass 2 — Resolver       → MappingResolver.resolve_blocks()
      │                       Matches each line against trie patterns
      │                       Parses expressions via recursive descent
      │                       Builds canonical AST (ProgramNode)
      ▼
5. Semantic Analyzer       → SemanticAnalyzer.analyze()
      │                       Validates undefined vars/functions
      │                       Checks argument counts
      │                       Generates warnings
      ▼
6. Interpreter             → Interpreter.run()
      │                       Tree-walking execution
      │                       Scope management (Scope chain)
      │                       Built-in resolution
      │                       Auto-print, step mode, timeout
      ▼
7. (optional) Complexity   → ComplexityEngine.analyze()
                              Static Big-O analysis
                              Walks AST for loop nesting, recursion`;

export default function ArchitecturePage() {
  return (
    <>
      <div className="topbar">
        <span className="topbar-title">
          Internals › <span>Architecture</span>
        </span>
        <span className="topbar-badge">v0.1 · Reference</span>
      </div>
      <div className="page">
        <div className="page-hero">
          <span className="page-label">Internals</span>
          <h1 className="page-title">Compiler Architecture</h1>
          <p className="page-desc">
            A reference overview of the Pseudo compilation pipeline. Useful for
            contributors and those building extensions.
          </p>
        </div>

        <div className="callout warn">
          <span className="callout-icon">⚠</span>
          <div className="callout-body">
            This is a reference section. You do not need to understand the
            internals to use Pseudo.
          </div>
        </div>

        <h2>Pipeline Overview</h2>
        <CodeBlock lang="text" title="pipeline" code={PIPELINE} />

        <h2>File Map</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>File</th>
                <th>Purpose</th>
                <th>~Lines</th>
              </tr>
            </thead>
            <tbody>
              {[
                ["pseudo/__init__.py", "Package entry, version export", "4"],
                [
                  "pseudo/parser/tokenizer.py",
                  "Lexer — character → tokens",
                  "266",
                ],
                [
                  "pseudo/parser/normalizer.py",
                  "Whitespace normalization",
                  "56",
                ],
                [
                  "pseudo/parser/indent_parser.py",
                  "Indentation + block tree",
                  "300",
                ],
                [
                  "pseudo/parser/ast_nodes.py",
                  "All AST dataclass definitions",
                  "293",
                ],
                [
                  "pseudo/parser/expr_parser.py",
                  "Recursive descent expression parser",
                  "577",
                ],
                [
                  "pseudo/data/default.pmap",
                  "Bundled default English mappings",
                  "163",
                ],
                [
                  "pseudo/resolver/pmap_loader.py",
                  ".pmap parser + prefix trie + cache",
                  "706",
                ],
                [
                  "pseudo/resolver/pass1_register.py",
                  "Function/variable registration",
                  "199",
                ],
                [
                  "pseudo/resolver/pass2_resolver.py",
                  "Pattern matching → AST",
                  "988",
                ],
                [
                  "pseudo/analyzer/semantic.py",
                  "Static validation + warnings",
                  "320",
                ],
                [
                  "pseudo/interpreter/interpreter.py",
                  "Tree-walking executor",
                  "1018",
                ],
                [
                  "pseudo/interpreter/builtins_ds.py",
                  "DS classes (Stack, Queue, etc.)",
                  "421",
                ],
                [
                  "pseudo/analyzer/complexity.py",
                  "Big-O static analysis",
                  "611",
                ],
                [
                  "pseudo/compiler.py",
                  "Pipeline glue + CLI integration",
                  "256",
                ],
                ["pseudo/cli.py", "argparse CLI entry point", "293"],
                ["pseudo/install.py", "~/.pseudo/ home setup", "88"],
              ].map(([f, p, l]) => (
                <tr key={String(f)}>
                  <td>
                    <code style={{ fontSize: 11 }}>{f}</code>
                  </td>
                  <td style={{ color: "var(--fg-muted)" }}>{p}</td>
                  <td style={{ color: "var(--fg-muted)", textAlign: "right" }}>
                    {l}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <h2>Two-Pass Parsing</h2>
        <p>
          Pseudo uses two passes to support mutual recursion and forward
          references:
        </p>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Pass</th>
                <th>What it does</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <strong>Pass 1</strong> — Registration
                </td>
                <td>
                  Scans the entire file. Registers all function names and global
                  variables into the symbol table. No execution occurs. No .pmap
                  matching occurs.
                </td>
              </tr>
              <tr>
                <td>
                  <strong>Pass 2</strong> — Resolver
                </td>
                <td>
                  With the full symbol table available, resolves every line via
                  .pmap pattern matching and builds the canonical AST.
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <h2>Prefix Trie (Pattern Matching)</h2>
        <p>
          All patterns are compiled into a prefix trie keyed by the first
          literal token. For a line starting with <code>for</code>, only
          patterns that start with <code>for</code> are tested —{" "}
          <strong>O(1)</strong> lookup, then <strong>O(small subset)</strong>{" "}
          pattern check.
        </p>

        <h2>Scope Chain</h2>
        <p>
          The interpreter maintains a chain of <code>Scope</code> objects:
        </p>
        <ul>
          <li>Global scope: top-level variables and functions</li>
          <li>
            Local scope: created per function call, parent is always global
          </li>
          <li>
            Reads walk up the chain; writes stay local unless{" "}
            <code>global</code> declared
          </li>
          <li>Recursion limit: 1000 call stack depth</li>
        </ul>

        <h2>Auto-print Signal</h2>
        <p>
          Bare expressions and function calls that are not assigned become{" "}
          <code>AutoPrintNode</code> in the AST. The interpreter evaluates them
          and prints the result if it is non-null (and{" "}
          <code>--no-auto-print</code> is not set).
        </p>
      </div>
    </>
  );
}
