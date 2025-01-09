import React from "react";
import Link from 'next/link';
import { Inter } from "next/font/google";
import { ThemeProvider } from "@/components/theme-provider";
import { AuthProvider } from '@/hooks/use-auth';
import { Toaster } from "@/components/ui/toaster";
import { Header } from "@/components/header";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
});

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <AuthProvider>
            <div className="min-h-screen bg-background">
              <Header />
              <main className="container mx-auto py-4 px-4">
                {children}
              </main>
            </div>
            <Toaster />
          </AuthProvider>
        </ThemeProvider>
        <footer className="flex justify-center space-x-4 mt-4">
          <Link href="/about">About</Link>
          <Link href="/about">Help</Link>
          <Link href="/about">Privacy</Link>
          <Link href="/about">Terms</Link>
        </footer>
        <div className="mt-4 text-center text-sm">    
            English © 2024 PhotoShare from The Byte Brigade
        </div>
      </body>
    </html>
  );
}
