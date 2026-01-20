import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// Base API instance without authentication
export const api = axios.create({
    baseURL: API_URL,
    headers: {
        "Content-Type": "application/json",
    },
});

// Function to create an authenticated API call
// Usage: await authenticatedApi(getToken).get("/me")
export const createAuthenticatedApi = (token: string | null) => {
    const instance = axios.create({
        baseURL: API_URL,
        headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
    });

    return instance;
};

// Helper to make authenticated requests with Clerk token
// Used in components: const { getToken } = useAuth(); await apiWithAuth(await getToken()).get("/me")
export const apiWithAuth = (token: string | null) => createAuthenticatedApi(token);
