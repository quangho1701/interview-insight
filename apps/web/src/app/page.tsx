import Link from "next/link";
import { Button } from "@vibecheck/ui";
import { ArrowRight, Mic, Sparkles, LineChart } from "lucide-react";

export default function Home() {
    return (
        <main className="flex min-h-screen flex-col bg-black text-white selection:bg-vibe-green selection:text-black">
            {/* Navigation */}
            <nav className="flex items-center justify-between p-6 px-8 border-b border-zinc-800">
                <div className="text-2xl font-bold bg-gradient-to-r from-vibe-green to-emerald-600 text-transparent bg-clip-text">
                    VibeCheck
                </div>
                <div className="flex gap-4">
                    <Link href="/login">
                        <Button variant="ghost" className="text-zinc-300 hover:text-white hover:bg-white/10">
                            Sign In
                        </Button>
                    </Link>
                    <Link href="/signup">
                        <Button className="bg-vibe-green text-black hover:bg-vibe-green/90">
                            Get Started
                        </Button>
                    </Link>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="flex flex-col items-center justify-center flex-1 text-center px-4 py-20 relative overflow-hidden">
                {/* Background Aura */}
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-vibe-green/20 rounded-full blur-[120px] -z-10 animate-pulse" />

                <div className="inline-flex items-center rounded-full border border-zinc-800 bg-zinc-900/50 px-3 py-1 text-sm text-zinc-400 mb-8 backdrop-blur-xl">
                    <Sparkles className="mr-2 h-4 w-4 text-vibe-green" />
                    <span>AI-Powered Interview Intelligence</span>
                </div>

                <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 max-w-4xl bg-gradient-to-b from-white to-zinc-400 text-transparent bg-clip-text">
                    Master the Art of the Vibe.
                </h1>

                <p className="text-xl text-zinc-400 max-w-2xl mb-10 leading-relaxed">
                    Analyze interviews, uncover hidden insights, and decode the subtle signals that make or break a hire.
                </p>

                <div className="flex flex-col sm:flex-row gap-4">
                    <Link href="/signup">
                        <Button size="lg" className="bg-vibe-green text-black hover:bg-vibe-green/90 h-12 px-8 text-lg">
                            Start Analyzing <ArrowRight className="ml-2 h-5 w-5" />
                        </Button>
                    </Link>
                    <Link href="/login">
                        <Button variant="outline" size="lg" className="border-zinc-700 text-white hover:bg-zinc-800 h-12 px-8 text-lg">
                            View Demo
                        </Button>
                    </Link>
                </div>
            </section>

            {/* Feature Grid */}
            <section className="grid md:grid-cols-3 gap-8 px-8 py-20 max-w-7xl mx-auto border-t border-zinc-900">
                <div className="p-6 rounded-2xl bg-zinc-950 border border-zinc-900 hover:border-vibe-green/30 transition-colors group">
                    <div className="h-12 w-12 rounded-lg bg-zinc-900 flex items-center justify-center mb-4 group-hover:bg-vibe-green/10 transition-colors">
                        <Mic className="h-6 w-6 text-vibe-green" />
                    </div>
                    <h3 className="text-xl font-bold mb-2 text-white">Audio Analysis</h3>
                    <p className="text-zinc-400">Upload interview recordings and get instant transcriptions and sentiment breakdowns.</p>
                </div>
                <div className="p-6 rounded-2xl bg-zinc-950 border border-zinc-900 hover:border-vibe-green/30 transition-colors group">
                    <div className="h-12 w-12 rounded-lg bg-zinc-900 flex items-center justify-center mb-4 group-hover:bg-purple-500/10 transition-colors">
                        <LineChart className="h-6 w-6 text-purple-500" />
                    </div>
                    <h3 className="text-xl font-bold mb-2 text-white">Performance Metrics</h3>
                    <p className="text-zinc-400">Track technical scores, communication clarity, and overall candidate vibe.</p>
                </div>
                <div className="p-6 rounded-2xl bg-zinc-950 border border-zinc-900 hover:border-vibe-green/30 transition-colors group">
                    <div className="h-12 w-12 rounded-lg bg-zinc-900 flex items-center justify-center mb-4 group-hover:bg-blue-500/10 transition-colors">
                        <Sparkles className="h-6 w-6 text-blue-500" />
                    </div>
                    <h3 className="text-xl font-bold mb-2 text-white">AI Summaries</h3>
                    <p className="text-zinc-400">Get executive summaries generated by advanced LLMs (Llama 3.3).</p>
                </div>
            </section>

            <footer className="border-t border-zinc-900 py-10 text-center text-zinc-500 text-sm">
                <p>© 2026 VibeCheck. Built for the future of hiring.</p>
            </footer>
        </main>
    );
}
