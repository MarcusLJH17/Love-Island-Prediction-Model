import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "IslandEdge",
  description: "Love Island USA sentiment forecasting MVP"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
