import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import { Music, History } from "lucide-react";
import { Toaster } from "@/components/ui/sonner";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "MP3 Extractor - Convert MP4 to MP3",
  description: "Fast and easy MP4 to MP3 conversion with real-time progress tracking",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <div className="min-h-screen flex flex-col">
          {/* Navigation Header */}
          <header className="border-b">
            <div className="container mx-auto px-4 py-4">
              <nav className="flex items-center justify-between">
                <Link href="/" className="flex items-center gap-2 text-xl font-bold">
                  <Music className="w-6 h-6" />
                  <span>MP3 Extractor</span>
                </Link>
                <Link
                  href="/history"
                  className="flex items-center gap-2 text-sm font-medium hover:text-primary transition-colors"
                >
                  <History className="w-4 h-4" />
                  <span>History</span>
                </Link>
              </nav>
            </div>
          </header>

          {/* Main Content */}
          <main className="flex-1 container mx-auto px-4 py-8">
            {children}
          </main>

          {/* Footer */}
          <footer className="border-t py-6 text-center text-sm text-muted-foreground">
            <p>MP3 Extractor - Convert MP4 to MP3 with ease</p>
          </footer>
        </div>

        {/* Toast Notifications */}
        <Toaster />
      </body>
    </html>
  );
}
