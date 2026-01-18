"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api-client";
import { Card, CardHeader, CardTitle, CardContent, Button } from "@vibecheck/ui";
import Link from "next/link";
import { FileText, Loader2, PlayCircle } from "lucide-react";
// import { format } from "date-fns"; // Adding date-fns later if needed, use simple date for now

interface ProcessingJob {
    id: string; // UUID
    filename: string;
    status: "PENDING" | "COMPLETED" | "FAILED";
    created_at: string;
}

export default function DashboardPage() {
    const [jobs, setJobs] = useState<ProcessingJob[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchJobs = async () => {
            try {
                const { data } = await api.get("/jobs");
                setJobs(data);
            } catch (error) {
                console.error("Failed to fetch jobs", error);
            } finally {
                setLoading(false);
            }
        };

        fetchJobs();
    }, []);

    if (loading) {
        return <div className="flex items-center justify-center h-48"><Loader2 className="h-8 w-8 animate-spin text-vibe-green" /></div>;
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-3xl font-bold tracking-tight text-white">Dashboard</h2>
                <Link href="/upload">
                    <Button className="bg-vibe-green text-black hover:bg-vibe-green/90">
                        Upload New Interview
                    </Button>
                </Link>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {jobs.length === 0 ? (
                    <div className="col-span-full text-center py-10 text-zinc-500">
                        No interviews found. Upload one to get started.
                    </div>
                ) : (
                    jobs.map((job) => (
                        <Card key={job.id} className="bg-zinc-900 border-zinc-800 hover:border-vibe-green/50 transition-colors">
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium text-white truncate max-w-[200px]" title={job.filename}>
                                    {job.filename}
                                </CardTitle>
                                {job.status === "COMPLETED" ? (
                                    <FileText className="h-4 w-4 text-vibe-green" />
                                ) : (
                                    <Loader2 className="h-4 w-4 animate-spin text-yellow-500" />
                                )}
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold text-white mb-2">{job.status}</div>
                                <p className="text-xs text-zinc-500 mb-4">
                                    {new Date(job.created_at).toLocaleDateString()}
                                </p>
                                {job.status === "COMPLETED" && (
                                    <Link href={`/jobs/${job.id}`}>
                                        <Button variant="outline" size="sm" className="w-full border-zinc-700 text-white hover:bg-zinc-800">
                                            View Analysis
                                        </Button>
                                    </Link>
                                )}
                            </CardContent>
                        </Card>
                    ))
                )}
            </div>
        </div>
    );
}
