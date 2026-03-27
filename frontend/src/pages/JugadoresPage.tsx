import React, { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Layout } from "../components/Layout";
import { ApiError, useApi } from "../lib/api";
import { useAuth } from "../state/auth";

type Categoria = { id_categoria: number; descripcion: string };
type Jugador = { id_jugador: number; nombre: string; apellido: string; tipo_documento: string; numero_documento: string; activo: boolean; categoria?: Categoria | null };
type Page<T> = { items: T[]; page: number; page_size: number; total: number };

export function JugadoresPage() {
  const api = useApi();
  const { user } = useAuth();
  const [sp, setSp] = useSearchParams();
  const [cats, setCats] = useState<Categoria[]>([]);
  const [data, setData] = useState<Page<Jugador> | null>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const idCategoria = sp.get("id_categoria") || "";
  const activo = sp.get("activo") || "";
  const q = sp.get("q") || "";
  const qs = useMemo(() => {
    const p = new URLSearchParams();
    if (idCategoria) p.set("id_categoria", idCategoria);
    if (activo) p.set("activo", activo);
    if (q) p.set("q", q);
    p.set("page", "1");
    p.set("page_size", "20");
    return p.toString();
  }, [idCategoria, activo, q]);

  useEffect(() => {
    api.get<Categoria[]>("/categorias").then(setCats).catch(() => setCats([]));
  }, [api]);
  useEffect(() => {
    api.get<Page<Jugador>>(`/jugadores?${qs}`).then(setData).catch(() => setData(null));
  }, [api, qs]);

  function updateParam(key: string, value: string) {
    const next = new URLSearchParams(sp);
    if (!value) next.delete(key); else next.set(key, value);
    setSp(next, { replace: true });
  }

  async function removeJugador(j: Jugador) {
    if (user?.rol !== "Admin") return;
    if (!window.confirm(`¿Eliminar a ${j.apellido}, ${j.nombre}?`)) return;
    try {
      await api.del<void>(`/jugadores/${j.id_jugador}`);
      setData(prev => prev ? { ...prev, items: prev.items.filter(x => x.id_jugador !== j.id_jugador), total: Math.max(0, prev.total - 1) } : prev);
      setMsg("Jugador eliminado");
    } catch (e) {
      const err = e as ApiError;
      setMsg(err.status === 409 ? "No se puede borrar: tiene pagos registrados" : "Error al eliminar");
    }
  }

  return (
    <Layout>
      <div className="space-y-4">
        <div className="rounded-2xl border bg-white p-4">
          <div className="flex justify-between items-end gap-3">
            <div>
              <h1 className="text-xl font-semibold">Jugadores</h1>
              <p className="text-sm text-slate-600">Filtrá por categoría y estado.</p>
            </div>
            <Link className="rounded-lg bg-slate-900 px-4 py-2 text-sm text-white" to="/jugadores/nuevo">Nuevo jugador</Link>
          </div>
          <div className="mt-3 grid md:grid-cols-3 gap-3">
            <select className="rounded-lg border px-3 py-2 text-sm" value={idCategoria} onChange={e => updateParam("id_categoria", e.target.value)}>
              <option value="">Todas</option>{cats.map(c => <option key={c.id_categoria} value={String(c.id_categoria)}>{c.descripcion}</option>)}
            </select>
            <select className="rounded-lg border px-3 py-2 text-sm" value={activo} onChange={e => updateParam("activo", e.target.value)}>
              <option value="">Todos</option><option value="true">Activos</option><option value="false">Inactivos</option>
            </select>
            <input className="rounded-lg border px-3 py-2 text-sm" value={q} onChange={e => updateParam("q", e.target.value)} placeholder="Buscar" />
          </div>
        </div>
        <div className="rounded-2xl border bg-white p-4">
          {msg && <div className="text-sm text-slate-700 mb-2">{msg}</div>}
          <table className="w-full text-sm">
            <thead className="text-slate-500"><tr><th className="text-left py-2">Jugador</th><th className="text-left py-2">Categoría</th><th className="text-left py-2">Documento</th><th className="text-left py-2">Estado</th><th className="text-left py-2">Acciones</th></tr></thead>
            <tbody>
              {data?.items.map(j => (
                <tr key={j.id_jugador} className="border-t">
                  <td className="py-2"><Link to={`/jugadores/${j.id_jugador}`} className="hover:underline">{j.apellido}, {j.nombre}</Link></td>
                  <td className="py-2">{j.categoria?.descripcion ?? "—"}</td>
                  <td className="py-2">{j.tipo_documento} {j.numero_documento}</td>
                  <td className="py-2">{j.activo ? "Activo" : "Inactivo"}</td>
                  <td className="py-2 space-x-2">
                    <Link className="rounded border px-2 py-1" to={`/jugadores/${j.id_jugador}/editar`}>Editar</Link>
                    {(user?.rol === "Admin" || user?.rol === "Coordinador") && <button className="rounded border px-2 py-1 text-red-700" onClick={() => removeJugador(j)}>Eliminar</button>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </Layout>
  );
}
