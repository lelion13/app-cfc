import React, { useEffect, useMemo, useState } from "react";
import { Layout } from "../components/Layout";
import { ApiError, useApi } from "../lib/api";
import { useAuth } from "../state/auth";

export function PagosPage() {
  const api = useApi();
  const { user } = useAuth();
  const [items, setItems] = useState<any[]>([]);
  const [jugadores, setJugadores] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const [idJugador, setIdJugador] = useState("");
  const [mes, setMes] = useState("");
  const [anio, setAnio] = useState("");
  const [fromFecha, setFromFecha] = useState("");
  const [toFecha, setToFecha] = useState("");

  const [form, setForm] = useState({
    id_jugador: "",
    fecha_pago: "",
    monto: "",
    mes_correspondiente: "",
    anio_correspondiente: "",
    metodo_pago: "",
    comprobante_url: ""
  });
  const [editingId, setEditingId] = useState<number | null>(null);

  const isAdmin = user?.rol === "Admin";

  const query = useMemo(() => {
    const p = new URLSearchParams();
    if (idJugador) p.set("id_jugador", idJugador);
    if (mes) p.set("mes", mes);
    if (anio) p.set("anio", anio);
    if (fromFecha) p.set("from_fecha", fromFecha);
    if (toFecha) p.set("to_fecha", toFecha);
    return p.toString();
  }, [idJugador, mes, anio, fromFecha, toFecha]);

  async function loadPagos() {
    setLoading(true);
    setError(null);
    try {
      const data = await api.get<any[]>(`/pagos${query ? `?${query}` : ""}`);
      setItems(data);
    } catch {
      setError("No se pudo cargar pagos");
      setItems([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadPagos();
  }, [api, query]);

  useEffect(() => {
    api
      .get<any>("/jugadores?page=1&page_size=100&activo=true")
      .then((res) => setJugadores(res.items ?? []))
      .catch(() => setJugadores([]));
  }, [api]);

  function resetForm() {
    setForm({
      id_jugador: "",
      fecha_pago: "",
      monto: "",
      mes_correspondiente: "",
      anio_correspondiente: "",
      metodo_pago: "",
      comprobante_url: ""
    });
    setEditingId(null);
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setMessage(null);
    const payload: any = {
      id_jugador: Number(form.id_jugador),
      monto: Number(form.monto),
      mes_correspondiente: Number(form.mes_correspondiente),
      anio_correspondiente: Number(form.anio_correspondiente),
      metodo_pago: form.metodo_pago.trim()
    };
    if (form.fecha_pago) payload.fecha_pago = form.fecha_pago;
    if (form.comprobante_url.trim()) payload.comprobante_url = form.comprobante_url.trim();
    try {
      if (editingId) {
        await api.patch(`/pagos/${editingId}`, payload);
        setMessage("Pago actualizado");
      } else {
        await api.post("/pagos", payload);
        setMessage("Pago creado");
      }
      resetForm();
      await loadPagos();
    } catch (e) {
      const err = e as ApiError;
      if (err.status === 409) setMessage("Ya existe un pago para ese jugador y período");
      else if (err.status === 404) setMessage("Jugador no encontrado");
      else setMessage("No se pudo guardar el pago");
    }
  }

  function startEdit(p: any) {
    setEditingId(p.id_pago);
    setForm({
      id_jugador: String(p.id_jugador),
      fecha_pago: p.fecha_pago ?? "",
      monto: String(p.monto ?? ""),
      mes_correspondiente: String(p.mes_correspondiente ?? ""),
      anio_correspondiente: String(p.anio_correspondiente ?? ""),
      metodo_pago: p.metodo_pago ?? "",
      comprobante_url: p.comprobante_url ?? ""
    });
  }

  async function onDelete(p: any) {
    setMessage(null);
    if (!isAdmin) {
      setMessage("No tenés permisos para eliminar pagos");
      return;
    }
    if (!window.confirm("¿Eliminar este pago?")) return;
    try {
      await api.del(`/pagos/${p.id_pago}`);
      setMessage("Pago eliminado");
      await loadPagos();
    } catch (e) {
      const err = e as ApiError;
      if (err.status === 403) setMessage("No tenés permisos para eliminar pagos");
      else setMessage("No se pudo eliminar el pago");
    }
  }

  return (
    <Layout>
      <div className="space-y-4">
        <div className="rounded-2xl border bg-white p-6 space-y-3">
          <h1 className="text-xl font-semibold">Pagos</h1>
          <p className="text-sm text-slate-600">ABM completo con filtros y permisos por rol.</p>
          <div className="grid md:grid-cols-5 gap-2">
            <select className="rounded-lg border px-3 py-2 text-sm" value={idJugador} onChange={(e) => setIdJugador(e.target.value)}>
              <option value="">Jugador</option>
              {jugadores.map((j) => (
                <option key={j.id_jugador} value={String(j.id_jugador)}>
                  {j.apellido}, {j.nombre}
                </option>
              ))}
            </select>
            <input className="rounded-lg border px-3 py-2 text-sm" placeholder="Mes" value={mes} onChange={(e) => setMes(e.target.value)} />
            <input className="rounded-lg border px-3 py-2 text-sm" placeholder="Año" value={anio} onChange={(e) => setAnio(e.target.value)} />
            <input type="date" className="rounded-lg border px-3 py-2 text-sm" value={fromFecha} onChange={(e) => setFromFecha(e.target.value)} />
            <input type="date" className="rounded-lg border px-3 py-2 text-sm" value={toFecha} onChange={(e) => setToFecha(e.target.value)} />
          </div>
          <div className="flex gap-2">
            <button className="rounded-lg border px-3 py-2 text-sm" onClick={() => loadPagos()}>
              Aplicar filtros
            </button>
            <button
              className="rounded-lg border px-3 py-2 text-sm"
              onClick={() => {
                setIdJugador("");
                setMes("");
                setAnio("");
                setFromFecha("");
                setToFecha("");
              }}
            >
              Limpiar
            </button>
          </div>
        </div>

        <div className="rounded-2xl border bg-white p-6">
          <form onSubmit={onSubmit} className="grid md:grid-cols-4 gap-2 text-sm">
            <select className="rounded-lg border px-3 py-2" value={form.id_jugador} onChange={(e) => setForm((f) => ({ ...f, id_jugador: e.target.value }))} required>
              <option value="">Jugador</option>
              {jugadores.map((j) => (
                <option key={j.id_jugador} value={String(j.id_jugador)}>
                  {j.apellido}, {j.nombre}
                </option>
              ))}
            </select>
            <input type="date" className="rounded-lg border px-3 py-2" value={form.fecha_pago} onChange={(e) => setForm((f) => ({ ...f, fecha_pago: e.target.value }))} />
            <input className="rounded-lg border px-3 py-2" placeholder="Monto" value={form.monto} onChange={(e) => setForm((f) => ({ ...f, monto: e.target.value }))} required />
            <input className="rounded-lg border px-3 py-2" placeholder="Mes" value={form.mes_correspondiente} onChange={(e) => setForm((f) => ({ ...f, mes_correspondiente: e.target.value }))} required />
            <input className="rounded-lg border px-3 py-2" placeholder="Año" value={form.anio_correspondiente} onChange={(e) => setForm((f) => ({ ...f, anio_correspondiente: e.target.value }))} required />
            <input className="rounded-lg border px-3 py-2" placeholder="Método de pago" value={form.metodo_pago} onChange={(e) => setForm((f) => ({ ...f, metodo_pago: e.target.value }))} required />
            <input className="rounded-lg border px-3 py-2 md:col-span-2" placeholder="Comprobante URL (opcional)" value={form.comprobante_url} onChange={(e) => setForm((f) => ({ ...f, comprobante_url: e.target.value }))} />
            <div className="md:col-span-4 flex gap-2">
              <button className="rounded-lg bg-slate-900 px-4 py-2 text-white">{editingId ? "Guardar cambios" : "Crear pago"}</button>
              {editingId && (
                <button type="button" className="rounded-lg border px-4 py-2" onClick={resetForm}>
                  Cancelar edición
                </button>
              )}
            </div>
          </form>
        </div>

        <div className="rounded-2xl border bg-white p-6">
          {message && <div className="mb-2 text-sm text-slate-700">{message}</div>}
          {loading && <div className="text-sm text-slate-600">Cargando…</div>}
          {error && <div className="text-sm text-red-700">{error}</div>}
          {!loading && !error && items.length === 0 && <div className="text-sm text-slate-600">No hay pagos para los filtros aplicados.</div>}
          {!loading && !error && items.length > 0 && (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="text-xs uppercase text-slate-500">
                  <tr>
                    <th className="py-2">Jugador</th>
                    <th className="py-2">Período</th>
                    <th className="py-2">Fecha</th>
                    <th className="py-2">Monto</th>
                    <th className="py-2">Método</th>
                    <th className="py-2">Comprobante</th>
                    <th className="py-2">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((p) => (
                    <tr key={p.id_pago} className="border-t">
                      <td className="py-2">{p.jugador ? `${p.jugador.apellido}, ${p.jugador.nombre}` : `#${p.id_jugador}`}</td>
                      <td className="py-2">
                        {p.mes_correspondiente}/{p.anio_correspondiente}
                      </td>
                      <td className="py-2">{p.fecha_pago}</td>
                      <td className="py-2">${p.monto}</td>
                      <td className="py-2">{p.metodo_pago}</td>
                      <td className="py-2">{p.comprobante_url ? <a className="underline" href={p.comprobante_url} target="_blank" rel="noreferrer">Ver</a> : "—"}</td>
                      <td className="py-2 space-x-2">
                        <button className="rounded border px-2 py-1" onClick={() => startEdit(p)}>
                          Editar
                        </button>
                        {isAdmin && (
                          <button className="rounded border px-2 py-1 text-red-700" onClick={() => onDelete(p)}>
                            Eliminar
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
