import React, { useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { useAuth } from "../state/auth";

function NavItem({ to, label }: { to: string; label: string }) {
  return (
    <NavLink to={to} className={({ isActive }) => ["block rounded-lg px-3 py-2 text-sm", isActive ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100"].join(" ")}>
      {label}
    </NavLink>
  );
}

export function Layout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth();
  const [open, setOpen] = useState(false);
  return (
    <div className="min-h-screen">
      <div className="sticky top-0 z-20 border-b bg-white">
        <div className="mx-auto max-w-6xl px-4 py-3 flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <button className="md:hidden inline-flex items-center justify-center rounded-lg border px-3 py-2 text-sm" onClick={() => setOpen(v => !v)} aria-label="Menu">
              Menú
            </button>
            <Link to="/dashboard" className="font-semibold">Club Fútbol</Link>
          </div>
          <div className="flex items-center gap-3">
            {user && <div className="hidden sm:block text-xs text-slate-600">{user.username} · {user.rol}</div>}
            <button onClick={logout} className="rounded-lg bg-slate-900 px-3 py-2 text-sm text-white">Salir</button>
          </div>
        </div>
      </div>
      <div className="mx-auto max-w-6xl px-4 py-6 grid grid-cols-1 md:grid-cols-[240px_1fr] gap-6">
        <aside className={["md:block", open ? "block" : "hidden"].join(" ")}>
          <div className="rounded-xl border bg-white p-3 space-y-1">
            <NavItem to="/jugadores" label="Jugadores" />
            <NavItem to="/pagos" label="Pagos" />
            <NavItem to="/cajas" label={user?.rol === "Operador" ? "Mi caja" : "Cajas"} />
            <NavItem to="/partidos" label="Partidos" />
            {(user?.rol === "Admin" || user?.rol === "Coordinador") && <NavItem to="/ingresos" label="Ingresos" />}
            {(user?.rol === "Admin" || user?.rol === "Coordinador") && <NavItem to="/categorias" label="Categorías" />}
            {user?.rol === "Admin" && <NavItem to="/usuarios" label="Usuarios" />}
          </div>
        </aside>
        <main>{children}</main>
      </div>
    </div>
  );
}
