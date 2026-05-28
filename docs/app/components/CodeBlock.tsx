"use client";
import { Check, Copy } from "lucide-react";
import { useState, useCallback } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";

// Custom dark theme using pseudo palette
const pseudoTheme = {
  'code[class*="language-"]': {
    color: "#e8dec8",
    background: "none",
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: "13.5px",
  },
  'pre[class*="language-"]': { color: "#e8dec8", background: "none" },
  comment: { color: "#6a6070", fontStyle: "italic" },
  keyword: { color: "#d4b88c", fontWeight: "600" },
  string: { color: "#a8d8a8" },
  number: { color: "#89cff0" },
  function: { color: "#e8dec8" },
  operator: { color: "#b89870" },
  punctuation: { color: "#6a6070" },
  boolean: { color: "#89cff0" },
  variable: { color: "#e8dec8" },
  builtin: { color: "#d4b88c" },
  "class-name": { color: "#d4b88c" },
  parameter: { color: "#e8dec8" },
};

type CodeBlockProps = {
  code: string;
  lang?: string;
  title?: string;
  showOutput?: string;
};

export default function CodeBlock({
  code,
  lang = "text",
  title,
  showOutput,
}: CodeBlockProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }, [code]);

  return (
    <div>
      <div className="code-block">
        <div className="code-block-header">
          <span className="code-block-lang">{title || lang}</span>
          <button
            className="code-block-copy flex items-center gap-2"
            onClick={handleCopy}
          >
            {copied ? (
              <>
                <Check size={14} />
                Copied
              </>
            ) : (
              <>
                <Copy size={14} />
                Copy
              </>
            )}
          </button>
        </div>
        <SyntaxHighlighter
          language={lang === "pseudo" ? "python" : lang}
          style={pseudoTheme as Record<string, React.CSSProperties>}
          customStyle={{
            margin: 0,
            padding: "20px",
            background: "transparent",
            fontSize: "13.5px",
          }}
        >
          {code}
        </SyntaxHighlighter>
      </div>
      {showOutput !== undefined && (
        <div>
          <div
            className="output-label"
            style={{ paddingLeft: 16, marginTop: 8 }}
          >
            Output
          </div>
          <div className="output-block">{showOutput}</div>
        </div>
      )}
    </div>
  );
}
