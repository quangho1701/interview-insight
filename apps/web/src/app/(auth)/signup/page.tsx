"use client";

import { useState } from "react";
// import { useAuth } from "@/context/AuthContext"; // Use if auto-login after signup
import { api } from "@/lib/api-client";
import { Button, Input, Card, CardHeader, CardContent, CardFooter, CardTitle, CardDescription } from "@vibecheck/ui";
import Link from "next/link";
import { Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";

export default function SignupPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [fullName, setFullName] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState("");
    const router = useRouter();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError("");

        try {
            // Assuming /users/ signup endpoint accepts json
            await api.post("/users/", {
                email,
                password,
                full_name: fullName,
            });

            // Redirect to login
            router.push("/login?registered=true");
        } catch (err: any) {
            console.error(err);
            if (err.response?.status === 409) {
                setError("An account with this email already exists.");
            } else if (err.response?.status === 422) {
                setError("Please check your input. Password must be at least 8 characters.");
            } else {
                setError("Failed to create account. Please try again.");
            }
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Card className="border-zinc-800 bg-zinc-950/50 backdrop-blur-xl">
            <CardHeader>
                <CardTitle className="text-2xl text-white">Create an account</CardTitle>
                <CardDescription>Get started with VibeCheck</CardDescription>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="space-y-2">
                        <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 text-zinc-400">
                            Full Name
                        </label>
                        <Input
                            type="text"
                            placeholder="John Doe"
                            value={fullName}
                            onChange={(e) => setFullName(e.target.value)}
                            className="bg-zinc-900 border-zinc-800 text-white placeholder:text-zinc-500"
                            required
                        />
                    </div>
                    <div className="space-y-2">
                        <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 text-zinc-400">
                            Email
                        </label>
                        <Input
                            type="email"
                            placeholder="name@example.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="bg-zinc-900 border-zinc-800 text-white placeholder:text-zinc-500"
                            required
                        />
                    </div>
                    <div className="space-y-2">
                        <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 text-zinc-400">
                            Password
                        </label>
                        <Input
                            type="password"
                            placeholder="••••••••"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="bg-zinc-900 border-zinc-800 text-white placeholder:text-zinc-500"
                            required
                        />
                    </div>
                    {error && <p className="text-sm text-red-500">{error}</p>}
                    <Button type="submit" className="w-full bg-vibe-green text-black hover:bg-vibe-green/90" disabled={isLoading}>
                        {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : "Sign up"}
                    </Button>
                </form>
            </CardContent>
            <CardFooter className="flex justify-center">
                <p className="text-sm text-zinc-500">
                    Already have an account?{" "}
                    <Link href="/login" className="text-vibe-green hover:underline">
                        Sign in
                    </Link>
                </p>
            </CardFooter>
        </Card>
    );
}
