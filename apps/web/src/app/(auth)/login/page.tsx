"use client";

import { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/lib/api-client";
import { Button, Input, Card, CardHeader, CardContent, CardFooter, CardTitle, CardDescription } from "@vibecheck/ui";
import Link from "next/link";
import { Loader2 } from "lucide-react";

export default function LoginPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState("");
    const { login } = useAuth();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError("");

        try {
            const formData = new FormData();
            formData.append("username", email);
            formData.append("password", password);

            const response = await api.post("/login/access-token", formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });

            const { access_token } = response.data;
            login(access_token);
        } catch (err: any) {
            console.error(err);
            setError("Invalid email or password");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Card className="border-zinc-800 bg-zinc-950/50 backdrop-blur-xl">
            <CardHeader>
                <CardTitle className="text-2xl text-white">Welcome back</CardTitle>
                <CardDescription>Sign in to your account</CardDescription>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
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
                        {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : "Sign in"}
                    </Button>
                </form>
            </CardContent>
            <CardFooter className="flex justify-center">
                <p className="text-sm text-zinc-500">
                    Don't have an account?{" "}
                    <Link href="/signup" className="text-vibe-green hover:underline">
                        Sign up
                    </Link>
                </p>
            </CardFooter>
        </Card>
    );
}
