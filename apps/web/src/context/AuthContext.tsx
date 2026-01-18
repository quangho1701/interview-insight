"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { api } from "@/lib/api-client";

interface AuthContextType {
    user: any | null; // Replace with User type when available
    isAuthenticated: boolean;
    isLoading: boolean;
    login: (token: string) => void;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<any | null>(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();
    const pathname = usePathname();

    useEffect(() => {
        const initAuth = async () => {
            const token = localStorage.getItem("token");

            // Dev mode: auto-fetch guest token if no token exists
            if (!token && process.env.NEXT_PUBLIC_DEV_AUTH_BYPASS === "true") {
                try {
                    const { data } = await api.get("/dev-token");
                    if (data.access_token) {
                        localStorage.setItem("token", data.access_token);
                        setIsAuthenticated(true);
                        setIsLoading(false);
                        return;
                    }
                } catch (error) {
                    console.warn("Dev auth bypass failed:", error);
                }
            }

            if (token) {
                setIsAuthenticated(true);
            }
            setIsLoading(false);
        };

        initAuth();
    }, []);

    const login = (token: string) => {
        localStorage.setItem("token", token);
        setIsAuthenticated(true);
        router.push("/dashboard");
    };

    const logout = () => {
        localStorage.removeItem("token");
        setIsAuthenticated(false);
        setUser(null);
        router.push("/login");
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                isAuthenticated,
                isLoading,
                login,
                logout,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
}
