"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { LayoutDashboard, Upload, LogOut } from "lucide-react";
import { SignOutButton } from "@clerk/nextjs";
import { Button } from "@vibecheck/ui";

const routes = [
    {
        label: "Dashboard",
        icon: LayoutDashboard,
        href: "/dashboard",
        color: "text-sky-500",
    },
    {
        label: "Upload Interview",
        icon: Upload,
        href: "/upload",
        color: "text-violet-500",
    },
];

export function Sidebar() {
    const pathname = usePathname();

    return (
        <div className="space-y-4 py-4 flex flex-col h-full bg-[#111827] text-white">
            <div className="px-3 py-2 flex-1">
                <Link href="/dashboard" className="flex items-center pl-3 mb-14">
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-vibe-green to-emerald-600 text-transparent bg-clip-text">
                        VibeCheck
                    </h1>
                </Link>
                <div className="space-y-1">
                    {routes.map((route) => (
                        <Link
                            key={route.href}
                            href={route.href}
                            className={cn(
                                "text-sm group flex p-3 w-full justify-start font-medium cursor-pointer hover:text-white hover:bg-white/10 rounded-lg transition",
                                pathname === route.href ? "text-white bg-white/10" : "text-zinc-400"
                            )}
                        >
                            <div className="flex items-center flex-1">
                                <route.icon className={cn("h-5 w-5 mr-3", route.color)} />
                                {route.label}
                            </div>
                        </Link>
                    ))}
                </div>
            </div>
            <div className="px-3 py-2">
                <SignOutButton>
                    <Button variant="destructive" className="w-full justify-start pl-3 text-zinc-400 hover:text-white hover:bg-red-500/10">
                        <LogOut className="h-5 w-5 mr-3 text-red-500" />
                        Logout
                    </Button>
                </SignOutButton>
            </div>
        </div>
    );
}
