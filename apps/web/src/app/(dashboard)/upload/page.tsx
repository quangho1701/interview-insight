"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api-client";
import { Button, Input, Card, CardHeader, CardTitle, CardContent, CardFooter } from "@vibecheck/ui";
import { UploadCloud, CheckCircle, Loader2, User } from "lucide-react";
import axios from "axios";

interface Interviewer {
    id: string; // UUID
    name: string;
}

export default function UploadPage() {
    const [file, setFile] = useState<File | null>(null);
    const [interviewers, setInterviewers] = useState<Interviewer[]>([]);
    const [selectedInterviewer, setSelectedInterviewer] = useState<string>("");
    const [newInterviewerName, setNewInterviewerName] = useState("");
    const [isCreatingInterviewer, setIsCreatingInterviewer] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const router = useRouter();

    // Fetch interviewers on mount
    useEffect(() => {
        const fetchInterviewers = async () => {
            try {
                const { data } = await api.get("/interviewers");
                setInterviewers(data.items);
            } catch (error) {
                console.error("Failed to fetch interviewers", error);
            }
        };
        fetchInterviewers();
    }, []);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    const createInterviewer = async () => {
        if (!newInterviewerName) return;
        try {
            const { data } = await api.post("/interviewers", { name: newInterviewerName });
            setInterviewers([...interviewers, data]);
            setSelectedInterviewer(data.id);
            setIsCreatingInterviewer(false);
            setNewInterviewerName("");
        } catch (error) {
            console.error("Failed to create interviewer", error);
            alert("Failed to create interviewer");
        }
    };

    const handleUpload = async () => {
        if (!file || !selectedInterviewer) return;
        setIsUploading(true);
        setUploadProgress(0);

        try {
            // 1. Get Presigned URL
            const { data: presignedData } = await api.post("/uploads/presigned-url", {
                filename: file.name,
                content_type: file.type,
            });

            const { url, fields, job_id } = presignedData;

            // 2. Upload to S3
            // We need to construct FormData based on 'fields' if it's a POST, or just put if it's a PUT.
            // Usually presigned URL for POST has fields. PUT is direct.
            // Assuming Request returns 'url' and optionally 'fields'.
            // If 'fields' exists, it's a POST.

            if (fields) {
                const formData = new FormData();
                Object.entries(fields).forEach(([key, value]) => {
                    formData.append(key, value as string);
                });
                formData.append("file", file); // File must be last

                await axios.post(url, formData, {
                    headers: {
                        "Content-Type": "multipart/form-data",
                    },
                    onUploadProgress: (progressEvent) => {
                        const percent = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 100));
                        setUploadProgress(percent);
                    }
                });
            } else {
                // PUT request
                await axios.put(url, file, {
                    headers: {
                        "Content-Type": file.type
                    },
                    onUploadProgress: (progressEvent) => {
                        const percent = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 100));
                        setUploadProgress(percent);
                    }
                })
            }

            // 3. Confirm Upload
            await api.post(`/uploads/${job_id}/confirm`, {
                interviewer_id: selectedInterviewer,
            });

            router.push("/dashboard");

        } catch (error) {
            console.error("Upload failed", error);
            alert("Upload failed. Please try again.");
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <div className="max-w-3xl mx-auto space-y-8">
            <h1 className="text-3xl font-bold text-white">Upload Interview</h1>

            <div className="grid gap-6 md:grid-cols-2">
                {/* File Selection */}
                <Card className="bg-zinc-900 border-zinc-800">
                    <CardHeader>
                        <CardTitle className="text-white">1. Select Recording</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="border-2 border-dashed border-zinc-700 rounded-lg p-10 flex flex-col items-center justify-center text-zinc-400 hover:border-vibe-green hover:text-vibe-green transition cursor-pointer relative">
                            <UploadCloud className="h-12 w-12 mb-4" />
                            <p className="text-sm text-center">Drag and drop or click to upload</p>
                            <input
                                type="file"
                                accept="audio/*,video/*"
                                onChange={handleFileChange}
                                className="absolute inset-0 opacity-0 cursor-pointer"
                            />
                        </div>
                        {file && (
                            <div className="mt-4 flex items-center text-vibe-green">
                                <CheckCircle className="h-4 w-4 mr-2" />
                                <span className="text-sm truncate">{file.name}</span>
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Interviewer Selection */}
                <Card className="bg-zinc-900 border-zinc-800">
                    <CardHeader>
                        <CardTitle className="text-white">2. Select Interviewer</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {!isCreatingInterviewer ? (
                            <>
                                <select
                                    className="w-full bg-black border border-zinc-700 rounded-md p-2 text-white outline-none focus:border-vibe-green"
                                    value={selectedInterviewer}
                                    onChange={(e) => setSelectedInterviewer(e.target.value)}
                                >
                                    <option value="" disabled>Select an interviewer</option>
                                    {interviewers.map((i) => (
                                        <option key={i.id} value={i.id}>{i.name}</option>
                                    ))}
                                </select>
                                <Button
                                    variant="outline"
                                    onClick={() => setIsCreatingInterviewer(true)}
                                    className="w-full border-zinc-700 text-zinc-300 hover:text-white"
                                >
                                    <User className="mr-2 h-4 w-4" />
                                    Create New Interviewer
                                </Button>
                            </>
                        ) : (
                            <div className="space-y-2">
                                <Input
                                    placeholder="Interviewer Name"
                                    value={newInterviewerName}
                                    onChange={(e) => setNewInterviewerName(e.target.value)}
                                    className="bg-black border-zinc-700 text-white"
                                />
                                <div className="flex space-x-2">
                                    <Button onClick={createInterviewer} className="flex-1 bg-vibe-green text-black">Save</Button>
                                    <Button onClick={() => setIsCreatingInterviewer(false)} variant="ghost" className="text-zinc-400">Cancel</Button>
                                </div>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>

            <div className="flex justify-end">
                <Button
                    size="lg"
                    className="bg-vibe-green text-black hover:bg-vibe-green/90 min-w-[200px]"
                    onClick={handleUpload}
                    disabled={!file || !selectedInterviewer || isUploading}
                >
                    {isUploading ? (
                        <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Uploading {uploadProgress}%
                        </>
                    ) : (
                        "Start Processing"
                    )}
                </Button>
            </div>
        </div>
    );
}
