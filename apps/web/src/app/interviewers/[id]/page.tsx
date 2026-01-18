"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api-client";
import { Card, CardHeader, CardTitle, CardContent } from "@vibecheck/ui";
import { Loader2, User, Trophy, Mic } from "lucide-react";

interface InterviewerProfile {
    id: string;
    name: string;
    total_interviews?: number;
    average_sentiment?: number;
    top_traits?: string[];
}

export default function InterviewerProfilePage() {
    const { id } = useParams();
    const [profile, setProfile] = useState<InterviewerProfile | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(false);

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const { data } = await api.get(`/interviewers/${id}`);
                setProfile(data);
            } catch (error) {
                console.error("Failed to fetch interviewer", error);
                setError(true);
            } finally {
                setLoading(false);
            }
        };
        fetchProfile();
    }, [id]);

    if (loading) {
        return <div className="flex justify-center h-screen items-center bg-black text-white"><Loader2 className="h-8 w-8 animate-spin text-vibe-green" /></div>;
    }

    if (error || !profile) {
        return (
            <div className="flex h-screen items-center justify-center bg-black text-white">
                <h1 className="text-2xl">Interviewer not found or profile is private.</h1>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-black p-8 text-white">
            <div className="max-w-4xl mx-auto space-y-8">
                {/* Header */}
                <div className="flex items-center space-x-4">
                    <div className="h-16 w-16 rounded-full bg-zinc-800 flex items-center justify-center border border-zinc-700">
                        <User className="h-8 w-8 text-vibe-green" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold">{profile.name}</h1>
                        <p className="text-zinc-400">Interviewer Profile</p>
                    </div>
                </div>

                <div className="grid gap-6 md:grid-cols-2">
                    <Card className="bg-zinc-900 border-zinc-800">
                        <CardHeader><CardTitle className="text-white flex items-center"><Mic className="mr-2 h-5 w-5 text-blue-500" /> Activity</CardTitle></CardHeader>
                        <CardContent>
                            <div className="text-4xl font-bold text-white mb-1">{profile.total_interviews || 0}</div>
                            <div className="text-sm text-zinc-500">Total Interviews Analyzed</div>
                        </CardContent>
                    </Card>

                    <Card className="bg-zinc-900 border-zinc-800">
                        <CardHeader><CardTitle className="text-white flex items-center"><Trophy className="mr-2 h-5 w-5 text-yellow-500" /> Vibe Score</CardTitle></CardHeader>
                        <CardContent>
                            <div className="text-4xl font-bold text-white mb-1">
                                {profile.average_sentiment ? Math.round(profile.average_sentiment * 100) : "N/A"}%
                            </div>
                            <div className="text-sm text-zinc-500">Average Positive Sentiment</div>
                        </CardContent>
                    </Card>
                </div>

                {/* Additional stats could go here if available */}
            </div>
        </div>
    );
}
