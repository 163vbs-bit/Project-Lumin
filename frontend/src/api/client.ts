import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "/api",
  timeout: 12000
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("lumin_access");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
