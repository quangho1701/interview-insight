import type { Metadata } from "next";
// import { Inter } from "next/font/google"; 
import "./globals.css";
import { AuthProvider } from "@/context/AuthContext";
import { cn } from "@/lib/utils";

export const metadata: Metadata = {
    title: "VibeCheck",
    description: "AI Interview Analyzer",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en" className="dark">
            <body className={cn("min-h-screen bg-background font-sans antialiased", "bg-black text-white")}>
                <AuthProvider>
                    {children}
                </AuthProvider>
            </body>
        </html>
    );
}
