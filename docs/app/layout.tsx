import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import Sidebar from "./components/Sidebar";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-jetbrains",
});

export const metadata: Metadata = {
  title: { default: "Pseudo - Documentation", template: "%s · Pseudo" },
  description:
    "Official documentation for Pseudo - run pseudocode as a real language.",
  metadataBase: new URL("https://pseudo.wiki"),
  icons: { icon: "/icon.png" },
  openGraph: {
    title: "Pseudo Language Documentation",
    description:
      "Write and run pseudocode. Install, configure, and extend Pseudo.",
    siteName: "pseudo.wiki",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${jetbrainsMono.variable}`}
      suppressHydrationWarning
    >
      <body>
        <div className="layout">
          <Sidebar />
          <main className="main-content">{children}</main>
        </div>
      </body>
    </html>
  );
}
