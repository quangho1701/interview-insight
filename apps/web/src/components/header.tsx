"use client";

import { useAuth } from "@/context/AuthContext";

export function Header() {
    const { user } = useAuth();

    return (
        <div className="flex items-center justify-end p-4 border-b border-zinc-800 bg-[#0a0a0a]">
            <div className="text-zinc-400 text-sm">
                {/* Welcome, {user?.full_name || "User"} */}
            </div>
        </div>
    );
}
