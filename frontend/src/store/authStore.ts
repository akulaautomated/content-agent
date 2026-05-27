import { create } from "zustand";
import { persist } from "zustand/middleware";

interface AuthState {
  token: string | null;
  userId: string | null;
  orgId: string | null;
  isLoggedIn: boolean;
  login: (token: string, userId: string, orgId: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      userId: null,
      orgId: null,
      isLoggedIn: false,
      login: (token, userId, orgId) => {
        localStorage.setItem("token", token);
        set({ token, userId, orgId, isLoggedIn: true });
      },
      logout: () => {
        localStorage.removeItem("token");
        set({ token: null, userId: null, orgId: null, isLoggedIn: false });
      },
    }),
    { name: "auth-storage" }
  )
);
