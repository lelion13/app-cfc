import React, { createContext, useContext, useEffect, useMemo, useState } from "react";

type Role = "Admin" | "Coordinador";
export type UserMe = {
  id_usuario: number;
  username: string;
  rol: Role;
  activo: boolean;
  created_at: string;
  updated_at: string;
};

type AuthState = {
  token: string | null;
  user: UserMe | null;
  isLoading: boolean;
  login: (token: string) => Promise<void>;
  logout: () => void;
};

const TOKEN_KEY = "club_token";
const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY));
  const [user, setUser] = useState<UserMe | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  async function fetchMe(nextToken: string) {
    const base = import.meta.env.VITE_API_BASE_URL as string;
    const res = await fetch(`${base}/auth/me`, { headers: { Authorization: `Bearer ${nextToken}` } });
    if (!res.ok) throw new Error("Unauthorized");
    setUser((await res.json()) as UserMe);
  }

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        if (!token) return;
        await fetchMe(token);
      } catch {
        if (!cancelled) {
          localStorage.removeItem(TOKEN_KEY);
          setToken(null);
          setUser(null);
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [token]);

  const value = useMemo<AuthState>(
    () => ({
      token,
      user,
      isLoading,
      login: async (nextToken: string) => {
        localStorage.setItem(TOKEN_KEY, nextToken);
        setToken(nextToken);
        await fetchMe(nextToken);
      },
      logout: () => {
        localStorage.removeItem(TOKEN_KEY);
        setToken(null);
        setUser(null);
      }
    }),
    [token, user, isLoading]
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
