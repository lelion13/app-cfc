import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getApiBase } from "../lib/api";

export function SetupPage() {
  const nav = useNavigate();
  const [allowed, setAllowed] = useState<boolean | null>(null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [setupToken, setSetupToken] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    fetch(`${getApiBase()}/auth/bootstrap-status`)
      .then(r => r.json() as Promise<{ allowed: boolean }>)
      .then(j => {
        if (!cancelled) setAllowed(j.allowed);
      })
      .catch(() => {
        if (!cancelled) setAllowed(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await fetch(`${getApiBase()}/auth/bootstrap`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password, setup_token: setupToken })
      });
      if (!res.ok) {
        if (res.status === 403) setError("El registro inicial no está disponible.");
        else if (res.status === 401) setError("Credenciales o token inválidos.");
        else if (res.status === 409) setError("El usuario ya existe.");
        else setError("No se pudo crear el administrador.");
        return;
      }
      nav("/login", { replace: true });
    } finally {
      setLoading(false);
    }
  }

  if (allowed === null) {
    return (
      <div className="min-h-screen grid place-items-center px-4 text-sm text-slate-600">Cargando…</div>
    );
  }

  if (!allowed) {
    return (
      <div className="min-h-screen grid place-items-center px-4">
        <div className="w-full max-w-md rounded-2xl border bg-white p-6 space-y-3 text-center">
          <p className="text-sm text-slate-700">El registro inicial no está habilitado (ya hay usuarios o falta configurar <code className="text-xs bg-slate-100 px-1 rounded">SETUP_TOKEN</code> en el servidor).</p>
          <Link to="/login" className="inline-block text-sm text-slate-900 underline">Volver al ingreso</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen grid place-items-center px-4">
      <form onSubmit={onSubmit} className="w-full max-w-md rounded-2xl border bg-white p-6 space-y-3">
        <h1 className="text-xl font-semibold">Primer administrador</h1>
        <p className="text-xs text-slate-600">Creá la cuenta Admin usando el token de configuración del servidor.</p>
        <input className="w-full rounded-lg border px-3 py-2 text-sm" placeholder="Usuario" value={username} onChange={e => setUsername(e.target.value)} required minLength={3} />
        <input className="w-full rounded-lg border px-3 py-2 text-sm" placeholder="Contraseña (mín. 10 caracteres)" type="password" value={password} onChange={e => setPassword(e.target.value)} required minLength={10} />
        <input className="w-full rounded-lg border px-3 py-2 text-sm" placeholder="Token de configuración (SETUP_TOKEN)" type="password" value={setupToken} onChange={e => setSetupToken(e.target.value)} required minLength={8} />
        {error && <div className="text-sm text-red-700">{error}</div>}
        <button disabled={loading} className="w-full rounded-lg bg-slate-900 px-3 py-2 text-sm text-white disabled:opacity-60">
          {loading ? "Creando…" : "Crear administrador"}
        </button>
        <Link to="/login" className="block text-center text-sm text-slate-600 underline">Ya tengo cuenta</Link>
      </form>
    </div>
  );
}
