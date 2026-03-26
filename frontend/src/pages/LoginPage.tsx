import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getApiBase } from "../lib/api";
import { useAuth } from "../state/auth";

export function LoginPage() {
  const { login } = useAuth();
  const nav = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [bootstrapAllowed, setBootstrapAllowed] = useState(false);

  useEffect(() => {
    let cancelled = false;
    fetch(`${getApiBase()}/auth/bootstrap-status`)
      .then(r => r.json() as Promise<{ allowed: boolean }>)
      .then(j => {
        if (!cancelled && j.allowed) setBootstrapAllowed(true);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    const res = await fetch(`${getApiBase()}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });
    if (!res.ok) {
      setError("Credenciales inválidas");
      return;
    }
    const data = (await res.json()) as { access_token: string };
    await login(data.access_token);
    nav("/dashboard", { replace: true });
  }

  return (
    <div className="min-h-screen grid place-items-center px-4">
      <form onSubmit={onSubmit} className="w-full max-w-md rounded-2xl border bg-white p-6 space-y-3">
        <h1 className="text-xl font-semibold">Ingresar</h1>
        <input className="w-full rounded-lg border px-3 py-2 text-sm" placeholder="Usuario" value={username} onChange={e => setUsername(e.target.value)} />
        <input className="w-full rounded-lg border px-3 py-2 text-sm" placeholder="Contraseña" type="password" value={password} onChange={e => setPassword(e.target.value)} />
        {error && <div className="text-sm text-red-700">{error}</div>}
        <button className="w-full rounded-lg bg-slate-900 px-3 py-2 text-sm text-white">Entrar</button>
        {bootstrapAllowed && (
          <p className="text-center text-sm text-slate-600">
            <Link to="/setup" className="underline">Configurar primer administrador</Link>
          </p>
        )}
      </form>
    </div>
  );
}
