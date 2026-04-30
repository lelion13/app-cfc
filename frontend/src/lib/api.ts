import { useCallback, useMemo } from "react";
import { getApiBase } from "./config";
import { useAuth } from "../state/auth";

export type ApiError = { status: number; detail: string };

async function parseError(res: Response): Promise<ApiError> {
  try {
    const j = (await res.json()) as { detail?: string };
    return { status: res.status, detail: j.detail ?? "Request failed" };
  } catch {
    return { status: res.status, detail: "Request failed" };
  }
}

export function useApi() {
  const { token, logout } = useAuth();
  const base = getApiBase();
  const request = useCallback(
    async <T,>(path: string, init?: RequestInit): Promise<T> => {
      const headers = new Headers(init?.headers);
      headers.set("Content-Type", "application/json");
      if (token) headers.set("Authorization", `Bearer ${token}`);
      const res = await fetch(`${base}${path}`, { ...init, headers });
      if (res.status === 401) {
        logout();
        throw await parseError(res);
      }
      if (!res.ok) throw await parseError(res);
      if (res.status === 204) return undefined as T;
      return (await res.json()) as T;
    },
    [base, logout, token]
  );
  return useMemo(
    () => ({
      get: <T,>(path: string) => request<T>(path),
      post: <T,>(path: string, body: unknown) => request<T>(path, { method: "POST", body: JSON.stringify(body) }),
      patch: <T,>(path: string, body: unknown) => request<T>(path, { method: "PATCH", body: JSON.stringify(body) }),
      del: <T,>(path: string) => request<T>(path, { method: "DELETE" })
    }),
    [request]
  );
}
