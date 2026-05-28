"use client";
import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { useState } from "react";
import {
  BookOpen,
  Download,
  Zap,
  Terminal,
  Eye,
  Layers,
  Braces,
  Ban,
  FileCode,
  Code,
  Scale,
  ArrowRightLeft,
  Settings,
  Cpu,
  Database,
  Sparkles,
  Activity,
  Menu as MenuIcon,
  X as XIcon,
  ExternalLink,
} from "lucide-react";

const NAV = [
  {
    section: "Getting Started",
    links: [
      { href: "/", label: "Introduction", icon: BookOpen },
      { href: "/installation", label: "Installation", icon: Download },
      { href: "/quickstart", label: "Quick Start", icon: Zap },
    ],
  },
  {
    section: "CLI Reference",
    links: [
      { href: "/cli", label: "Commands & Flags", icon: Terminal },
      { href: "/step-mode", label: "--step Mode", icon: Eye },
    ],
  },
  {
    section: "The PMAP System",
    links: [
      { href: "/pmap", label: "How PMAP Works", icon: Layers },
      { href: "/placeholders", label: "Placeholder Types", icon: Braces },
      { href: "/stop-tokens", label: "Stop Tokens", icon: Ban },
      { href: "/custom-pmap", label: "Custom PMAP", icon: FileCode },
    ],
  },
  {
    section: "Language Reference",
    links: [
      { href: "/canonicals", label: "Canonical Structures", icon: Code },
      { href: "/rules", label: "Language Rules", icon: Scale },
      { href: "/input", label: "$input System", icon: ArrowRightLeft },
      { href: "/config", label: "pseudo.config", icon: Settings },
    ],
  },
  {
    section: "Built-ins",
    links: [
      { href: "/builtins", label: "Built-in Functions", icon: Cpu },
      { href: "/datastructures", label: "Data Structures", icon: Database },
    ],
  },
  {
    section: "Examples",
    links: [{ href: "/examples", label: "Code Examples", icon: Sparkles }],
  },
  {
    section: "Internals",
    links: [{ href: "/architecture", label: "Architecture", icon: Activity }],
  },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  return (
    <>
      {/* mobile toggle */}
      <button
        className="menu-btn"
        onClick={() => setOpen(!open)}
        aria-label="Toggle Sidebar"
      >
        {open ? <XIcon size={18} /> : <MenuIcon size={18} />}
      </button>

      {open && (
        <div className="sidebar-overlay" onClick={() => setOpen(false)} />
      )}

      <aside className={`sidebar ${open ? "open" : ""}`}>
        <Link href="/" className="sidebar-logo" onClick={() => setOpen(false)}>
          <Image
            src="/icon.png"
            alt="Pseudo"
            width={28}
            height={28}
            style={{ objectFit: "contain" }}
          />
          <div>
            <div className="sidebar-logo-text">pseudo</div>
            <div className="sidebar-logo-sub">pseudo.wiki</div>
          </div>
        </Link>

        {NAV.map((group) => (
          <div key={group.section} className="sidebar-section">
            <div className="sidebar-section-label">{group.section}</div>
            {group.links.map((link) => {
              const Icon = link.icon;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`sidebar-link ${pathname === link.href ? "active" : ""}`}
                  onClick={() => setOpen(false)}
                >
                  <Icon size={15} />
                  {link.label}
                </Link>
              );
            })}
          </div>
        ))}

        <div
          style={{
            marginTop: "auto",
            padding: "20px",
            borderTop: "1px solid var(--bg-border)",
          }}
        >
          <a
            href="https://pypi.org/project/pseudo/"
            target="_blank"
            rel="noreferrer"
            style={{
              fontSize: 12,
              color: "var(--fg-muted)",
              display: "flex",
              alignItems: "center",
              gap: 6,
              textDecoration: "none",
            }}
          >
            <ExternalLink size={12} /> PyPI Package
          </a>
        </div>
      </aside>
    </>
  );
}
