import { Sidebar } from "@/components/sidebar";
import { Header } from "@/components/header";

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    // Middleware handles route protection, no auth check needed here
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
