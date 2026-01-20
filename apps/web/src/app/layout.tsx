import type { Metadata } from "next";
import { ClerkProvider } from "@clerk/nextjs";
import "./globals.css";
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
        <ClerkProvider
            appearance={{
                variables: {
                    colorPrimary: "#22c55e",
                    colorBackground: "#09090b",
                    colorInputBackground: "#18181b",
                    colorInputText: "#ffffff",
                    colorText: "#ffffff",
                    colorTextSecondary: "#a1a1aa",
                },
            }}
        >
            <html lang="en" className="dark">
                <body className={cn("min-h-screen bg-background font-sans antialiased", "bg-black text-white")}>
                    {children}
                </body>
            </html>
        </ClerkProvider>
    );
}
