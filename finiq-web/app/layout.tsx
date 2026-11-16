import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FINIQ — AI-Powered Financial Intelligence",
  description: "Institutional-grade AI financial analysis platform with ML predictions, multi-agent debate, and transparent baseline comparisons. This project is a prototype and is not financial advice.",
  keywords: ["finance", "AI", "stocks", "machine learning", "investment analysis"],
  openGraph: {
    title: "FINIQ — AI-Powered Financial Intelligence",
    description: "Institutional-grade AI financial analysis. This project is a prototype and is not financial advice.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
