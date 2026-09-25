import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Sales Pulse",
  description: "Automated sales analytics — validated, tested and deployed by CI/CD.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
