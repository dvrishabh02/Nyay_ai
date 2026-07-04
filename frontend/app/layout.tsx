import type { Metadata } from "next";
import { Newsreader, Hanken_Grotesk, Noto_Serif_Devanagari } from "next/font/google";
import "./globals.css";

const newsreader = Newsreader({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-newsreader",
  display: "swap",
});

const hanken = Hanken_Grotesk({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-hanken",
  display: "swap",
});

// Used only for the "न" brand-mark glyph in the logo tile/avatar — not for
// translated UI copy. The app remains English-only.
const notoDevanagari = Noto_Serif_Devanagari({
  subsets: ["devanagari"],
  weight: ["600"],
  variable: "--font-devanagari",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Nyay — Know your rights",
  description: "Ask about a legal problem in plain language and get a grounded, cited answer.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="en"
      className={`${newsreader.variable} ${hanken.variable} ${notoDevanagari.variable}`}
    >
      <body className="font-sans bg-canvas text-ink antialiased">{children}</body>
    </html>
  );
}
