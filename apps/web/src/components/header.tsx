"use client";

import { UserButton } from "@clerk/nextjs";

export function Header() {
    return (
        <div className="flex items-center justify-end p-4 border-b border-zinc-800 bg-[#0a0a0a]">
            <UserButton
                appearance={{
                    elements: {
                        avatarBox: "h-8 w-8",
                    },
                }}
            />
        </div>
    );
}
