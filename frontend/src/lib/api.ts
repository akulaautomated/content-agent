import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Redirect to login on 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export default api;

// ─── Auth ─────────────────────────────────────────────────────
export const authApi = {
  register: (data: { org_name: string; email: string; password: string; full_name?: string }) =>
    api.post("/api/auth/register", data),
  login: (email: string, password: string) =>
    api.post("/api/auth/login", { email, password }),
  me: () => api.get("/api/auth/me"),
};

// ─── Content ──────────────────────────────────────────────────
export const contentApi = {
  list: (params?: Record<string, string | number>) =>
    api.get("/api/content", { params }),
  get: (id: string) => api.get(`/api/content/${id}`),
  create: (data: object) => api.post("/api/content", data),
  update: (id: string, data: object) => api.put(`/api/content/${id}`, data),
  generate: (data: object) => api.post("/api/content/generate", data),
  transition: (id: string, newStatus: string) =>
    api.post(`/api/content/${id}/transition`, { new_status: newStatus }),
  revisions: (id: string) => api.get(`/api/content/${id}/revisions`),
};

// ─── Brands ───────────────────────────────────────────────────
export const brandsApi = {
  list: () => api.get("/api/brands"),
  get: (id: string) => api.get(`/api/brands/${id}`),
  create: (data: object) => api.post("/api/brands", data),
  update: (id: string, data: object) => api.put(`/api/brands/${id}`, data),
  delete: (id: string) => api.delete(`/api/brands/${id}`),
};

// ─── Campaigns ────────────────────────────────────────────────
export const campaignsApi = {
  list: () => api.get("/api/campaigns"),
  get: (id: string) => api.get(`/api/campaigns/${id}`),
  create: (data: object) => api.post("/api/campaigns", data),
};

// ─── Calendar ─────────────────────────────────────────────────
export const calendarApi = {
  list: (start?: string, end?: string) =>
    api.get("/api/calendar", { params: { start, end } }),
  create: (data: object) => api.post("/api/calendar", data),
  update: (id: string, data: object) => api.put(`/api/calendar/${id}`, data),
  delete: (id: string) => api.delete(`/api/calendar/${id}`),
};

// ─── Analytics ────────────────────────────────────────────────
export const analyticsApi = {
  dashboard: () => api.get("/api/analytics/dashboard"),
  content: (id: string) => api.get(`/api/analytics/content/${id}`),
};

// ─── SEO ──────────────────────────────────────────────────────
export const seoApi = {
  keywords: () => api.get("/api/seo/keywords"),
  addKeyword: (data: object) => api.post("/api/seo/keywords", data),
  analyze: (text: string, keywords: string[]) =>
    api.post("/api/seo/analyze", { text, keywords }),
};
