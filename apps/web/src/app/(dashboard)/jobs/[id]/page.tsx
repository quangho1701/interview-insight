"use client";

import { useEffect, useState, useRef } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api-client";
import { Card, CardHeader, CardTitle, CardContent, Button } from "@vibecheck/ui";
import { Loader2, ArrowLeft, BarChart2, MessageSquare, Brain } from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";

interface ProcessingJob {
    id: string;
    status: "PENDING" | "COMPLETED" | "FAILED";
    created_at: string;
}

interface InterviewAnalysis {
    id: string;
    job_id: string;
    sentiment_score: number;
    word_count: number;
    technical_score: number;
    communication_score: number;
    executive_summary: string;
}

export default function JobDetailsPage() {
    const { id } = useParams();
    const [job, setJob] = useState<ProcessingJob | null>(null);
    const [analysis, setAnalysis] = useState<InterviewAnalysis | null>(null);
    const [loading, setLoading] = useState(true);
    const pollInterval = useRef<NodeJS.Timeout | null>(null);

    const fetchJob = async () => {
        if (!id) return;
        try {
            // Assuming GET /jobs/{id} exists or we use list and find?
            // Roadmap says: GET /api/v1/jobs (list). 
            // Does GET /api/v1/jobs/{id} exist?
            // Step 67 said: GET /api/v1/jobs/{id} is client poll target in plan.
            // Backend plan included it? 
            // "Step 128: Client polls job status via GET /api/v1/jobs/{job_id}" -> Yes.
            const { data } = await api.get(`/jobs/${id}`);
            setJob(data);

            if (data.status === "COMPLETED") {
                if (pollInterval.current) {
                    clearInterval(pollInterval.current);
                    pollInterval.current = null;
                }
                // Fetch analysis
                fetchAnalysis();
            }
        } catch (error) {
            console.error("Failed to fetch job", error);
        } finally {
            setLoading(false);
        }
    };

    const fetchAnalysis = async () => {
        try {
            const { data } = await api.get(`/analysis/${id}`);
            setAnalysis(data);
        } catch (error) {
            console.error("Failed to fetch analysis", error);
        }
    };

    useEffect(() => {
        fetchJob();

        // Start polling if not completed
        pollInterval.current = setInterval(() => {
            fetchJob();
        }, 5000);

        return () => {
            if (pollInterval.current) clearInterval(pollInterval.current);
        };
    }, [id]);

    if (loading && !job) {
        return <div className="flex justify-center p-10"><Loader2 className="h-8 w-8 animate-spin text-vibe-green" /></div>;
    }

    if (!job) {
        return <div className="text-white">Job not found.</div>;
    }

    return (
        <div className="space-y-6 max-w-4xl mx-auto">
            <Link href="/dashboard" className="flex items-center text-zinc-400 hover:text-white mb-4">
                <ArrowLeft className="mr-2 h-4 w-4" /> Back to Dashboard
            </Link>

            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-white">Interview Analysis</h1>
                <span className={cn(
                    "px-3 py-1 rounded-full text-xs font-medium",
                    job.status === "COMPLETED" ? "bg-vibe-green/20 text-vibe-green" : "bg-yellow-500/20 text-yellow-500"
                )}>
                    {job.status}
                </span>
            </div>

            {job.status === "PENDING" && (
                <Card className="bg-zinc-900 border-zinc-800 p-8 text-center animate-pulse">
                    <Loader2 className="h-12 w-12 animate-spin text-vibe-green mx-auto mb-4" />
                    <p className="text-zinc-400">Analysis in progress. This may take a few minutes...</p>
                </Card>
            )}

            {job.status === "COMPLETED" && analysis && (
                <div className="grid gap-6 md:grid-cols-2">
                    {/* Scores */}
                    <Card className="col-span-full bg-zinc-900 border-zinc-800">
                        <CardHeader><CardTitle className="text-white">Performance Metrics</CardTitle></CardHeader>
                        <CardContent className="grid grid-cols-3 gap-4 text-center">
                            <div className="p-4 bg-black rounded-lg border border-zinc-800">
                                <BarChart2 className="h-6 w-6 text-blue-500 mx-auto mb-2" />
                                <div className="text-2xl font-bold text-white">{analysis.technical_score}/10</div>
                                <div className="text-xs text-zinc-400">Technical</div>
                            </div>
                            <div className="p-4 bg-black rounded-lg border border-zinc-800">
                                <MessageSquare className="h-6 w-6 text-purple-500 mx-auto mb-2" />
                                <div className="text-2xl font-bold text-white">{analysis.communication_score}/10</div>
                                <div className="text-xs text-zinc-400">Communication</div>
                            </div>
                            <div className="p-4 bg-black rounded-lg border border-zinc-800">
                                <Brain className="h-6 w-6 text-vibe-green mx-auto mb-2" />
                                <div className="text-2xl font-bold text-white">{analysis.sentiment_score * 100}%</div>
                                <div className="text-xs text-zinc-400">Sentiment</div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Summary */}
                    <Card className="col-span-full bg-zinc-900 border-zinc-800">
                        <CardHeader><CardTitle className="text-white">Executive Summary</CardTitle></CardHeader>
                        <CardContent>
                            <p className="text-zinc-300 leading-relaxed">
                                {analysis.executive_summary}
                            </p>
                        </CardContent>
                    </Card>
                </div>
            )}
        </div>
    );
}
