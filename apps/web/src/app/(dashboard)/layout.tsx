"use client";

import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { Sidebar } from "@/components/sidebar";
import { Header } from "@/components/header";
import { Loader2 } from "lucide-react";

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const { isAuthenticated, isLoading } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!isLoading && !isAuthenticated) {
            router.push("/login");
        }
    }, [isLoading, isAuthenticated, router]);

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-screen bg-black text-white">
                <Loader2 className="h-8 w-8 animate-spin text-vibe-green" />
            </div>
        );
    }

    if (!isAuthenticated) {
        return null; // Will redirect
    }

    return (
        <div className="h-full relative">
            <div className="hidden h-full md:flex md:w-72 md:flex-col md:fixed md:inset-y-0 z-[80] bg-gray-900">
                <Sidebar />
            </div>
            <main className="md:pl-72 h-full bg-[#0a0a0a]">
                <Header />
                <div className="p-8">
                    {children}
                </div>
            </main>
        </div>
    );
}
