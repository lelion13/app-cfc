import React, { useEffect, useMemo, useState } from "react";
import { JugadorCombobox } from "../components/JugadorCombobox";
import { Layout } from "../components/Layout";
import { ApiError, useApi } from "../lib/api";
import { useAuth } from "../state/auth";

const PAYMENT_METHODS = ["Efectivo", "Transferencia"] as const;
type PagoItem = {
  id_pago: number;
  id_jugador: number;
  fecha_pago: string;
  monto: number;
  mes_correspondiente: number;
  anio_correspondiente: number;
  metodo_pago: string;
  comprobante_url: string | null;
  jugador?: { id_jugador: number; nombre: string; apellido: string };
};

function todayIsoDate() {
  return new Date().toISOString().slice(0, 10);
}

function currentMonth() {
  return String(new Date().getMonth() + 1);
}

function currentYear() {
  return String(new Date().getFullYear());
}

function parseMontoInput(raw: string): number | null {
  const n = Number(String(raw).trim().replace(",", "."));
  if (!Number.isFinite(n) || n <= 0) return null;
  return n;
}

export function PagosPage() {
  const api = useApi();
  const { user } = useAuth();
  const [items, setItems] = useState<PagoItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const [idJugador, setIdJugador] = useState("");
  const [mes, setMes] = useState(currentMonth());
  const [anio, setAnio] = useState(currentYear());
  const [fromFecha, setFromFecha] = useState("");
  const [toFecha, setToFecha] = useState("");

  const [form, setForm] = useState({
    id_jugador: "",
    fecha_pago: todayIsoDate(),
    monto: "",
    mes_correspondiente: currentMonth(),
    anio_correspondiente: currentYear(),
    metodo_pago: "Efectivo",
    comprobante_url: ""
  });
  const [editingId, setEditingId] = useState<number | null>(null);

  const canDeletePago = user?.rol === "Admin" || user?.rol === "Coordinador";

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
      const data = await api.get<PagoItem[]>(`/pagos${query ? `?${query}` : ""}`);
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

  function resetForm() {
    setForm({
      id_jugador: "",
      fecha_pago: todayIsoDate(),
      monto: "",
      mes_correspondiente: currentMonth(),
      anio_correspondiente: currentYear(),
      metodo_pago: "Efectivo",
      comprobante_url: ""
    });
    setEditingId(null);
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setMessage(null);
    if (!form.id_jugador.trim()) {
      setMessage("Seleccioná un jugador de la lista de resultados");
      return;
    }
    const montoNum = parseMontoInput(form.monto);
    if (montoNum === null) {
      setMessage("Ingresá un importe válido mayor a cero");
      return;
    }
    const payload: Record<string, unknown> = {
      id_jugador: Number(form.id_jugador),
      monto: montoNum,
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
      if (err.status === 409 && err.detail.includes("closed rendicion")) setMessage("Este pago ya fue rendido y no se puede modificar");
      else if (err.status === 409) setMessage("Ya existe un pago para ese jugador y período");
      else if (err.status === 404) setMessage("Jugador no encontrado");
      else setMessage("No se pudo guardar el pago");
    }
  }

  function startEdit(p: PagoItem) {
    setEditingId(p.id_pago);
    setForm({
      id_jugador: String(p.id_jugador),
      fecha_pago: p.fecha_pago ?? "",
      monto: String(p.monto ?? ""),
      mes_correspondiente: String(p.mes_correspondiente ?? ""),
      anio_correspondiente: String(p.anio_correspondiente ?? ""),
      metodo_pago: PAYMENT_METHODS.includes(p.metodo_pago as (typeof PAYMENT_METHODS)[number]) ? p.metodo_pago : "Efectivo",
      comprobante_url: p.comprobante_url ?? ""
    });
  }

  async function onDelete(p: PagoItem) {
    setMessage(null);
    if (!canDeletePago) {
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
      else if (err.status === 409 && err.detail.includes("closed rendicion")) setMessage("Este pago ya fue rendido y no se puede eliminar");
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
            <div className="md:col-span-2">
              <JugadorCombobox value={idJugador} onChange={setIdJugador} api={api} placeholder="Filtrar por jugador…" />
            </div>
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
                setMes(currentMonth());
                setAnio(currentYear());
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
            <JugadorCombobox
              value={form.id_jugador}
              onChange={(id) => setForm((f) => ({ ...f, id_jugador: id }))}
              api={api}
              required
              placeholder="Buscar jugador…"
              inputClassName="rounded-lg border px-3 py-2 w-full"
            />
            <input type="date" className="rounded-lg border px-3 py-2" value={form.fecha_pago} onChange={(e) => setForm((f) => ({ ...f, fecha_pago: e.target.value }))} />
            <input
              className="rounded-lg border px-3 py-2"
              inputMode="decimal"
              placeholder="Importe"
              value={form.monto}
              onChange={(e) => setForm((f) => ({ ...f, monto: e.target.value }))}
              required
            />
            <input className="rounded-lg border px-3 py-2" placeholder="Mes" value={form.mes_correspondiente} onChange={(e) => setForm((f) => ({ ...f, mes_correspondiente: e.target.value }))} required />
            <input className="rounded-lg border px-3 py-2" placeholder="Año" value={form.anio_correspondiente} onChange={(e) => setForm((f) => ({ ...f, anio_correspondiente: e.target.value }))} required />
            <select className="rounded-lg border px-3 py-2" value={form.metodo_pago} onChange={(e) => setForm((f) => ({ ...f, metodo_pago: e.target.value }))} required>
              {PAYMENT_METHODS.map((method) => (
                <option key={method} value={method}>
                  {method}
                </option>
              ))}
            </select>
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
                        {canDeletePago && (
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
