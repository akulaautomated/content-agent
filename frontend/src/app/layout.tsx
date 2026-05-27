import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Content Agent — AI Marketing Platform",
  description: "AI-powered multi-channel content creation for digital marketing agencies",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
