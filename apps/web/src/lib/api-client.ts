import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const api = axios.create({
    baseURL: API_URL,
    headers: {
        "Content-Type": "application/json",
    },
});

api.interceptors.request.use(
    (config) => {
        if (typeof window !== "undefined") {
            const token = localStorage.getItem("token");
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

api.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        if (error.response && error.response.status === 401) {
            if (typeof window !== "undefined") {
                // Optional: Clear token?
                // localStorage.removeItem("token"); 
                // We might want to handle this in AuthContext or just let the error propagate
                // and let a global listener handle it? 
                // For now, allow the error to propagate so AuthContext can catch it.
            }
        }
        return Promise.reject(error);
    }
);
