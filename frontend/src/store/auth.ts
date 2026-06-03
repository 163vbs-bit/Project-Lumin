import { create } from "zustand";
import { api } from "../api/client";
import type { RoleName, User } from "../types";

interface AuthState {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (payload: { email: string; username: string; password: string; role: RoleName }) => Promise<void>;
  logout: () => void;
  hydrate: () => Promise<void>;
}

export const useAuth = create<AuthState>((set) => ({
  user: null,
  loading: false,
  login: async (username, password) => {
    set({ loading: true });
    try {
      const tokens = await api.post("/auth/login", { username, password });
      localStorage.setItem("lumin_access", tokens.data.access_token);
      localStorage.setItem("lumin_refresh", tokens.data.refresh_token);
      const me = await api.get("/auth/me");
      set({ user: me.data });
    } finally {
      set({ loading: false });
    }
  },
  register: async (payload) => {
    set({ loading: true });
    try {
      await api.post("/auth/register", payload);
      const tokens = await api.post("/auth/login", { username: payload.username, password: payload.password });
      localStorage.setItem("lumin_access", tokens.data.access_token);
      localStorage.setItem("lumin_refresh", tokens.data.refresh_token);
      const me = await api.get("/auth/me");
      set({ user: me.data });
    } finally {
      set({ loading: false });
    }
  },
  logout: () => {
    localStorage.removeItem("lumin_access");
    localStorage.removeItem("lumin_refresh");
    set({ user: null });
  },
  hydrate: async () => {
    const token = localStorage.getItem("lumin_access");
    if (!token) return;
    try {
      const me = await api.get("/auth/me");
      set({ user: me.data });
    } catch {
      localStorage.removeItem("lumin_access");
      localStorage.removeItem("lumin_refresh");
    }
  }
}));
