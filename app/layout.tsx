import "./globals.css";

export const metadata = {
  title: "RepoPilot — AI Coding Agent",
  description: "Understand your GitHub repository before you change it."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
