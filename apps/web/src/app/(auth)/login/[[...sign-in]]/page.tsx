import { SignIn } from "@clerk/nextjs";

export default function LoginPage() {
    return (
        <div className="flex min-h-screen items-center justify-center">
            <SignIn
                appearance={{
                    elements: {
                        formButtonPrimary: "bg-vibe-green text-black hover:bg-vibe-green/90",
                        card: "bg-zinc-950/50 border-zinc-800 backdrop-blur-xl",
                        headerTitle: "text-white",
                        headerSubtitle: "text-zinc-400",
                        socialButtonsBlockButton: "bg-zinc-900 border-zinc-800 text-white hover:bg-zinc-800",
                        formFieldLabel: "text-zinc-400",
                        formFieldInput: "bg-zinc-900 border-zinc-800 text-white placeholder:text-zinc-500",
                        footerActionLink: "text-vibe-green hover:text-vibe-green/80",
                    },
                }}
            />
        </div>
    );
}
