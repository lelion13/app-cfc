import React, { useEffect, useMemo, useState } from "react";
import { Layout } from "../components/Layout";
import { ApiError, useApi } from "../lib/api";
import { useAuth } from "../state/auth";

type CajaResumen = {
  id_caja: number;
  id_usuario: number;
  saldo_actual: number;
  total_pendiente: number;
  cantidad_pendientes: number;
  usuario?: { id_usuario: number; username: string; rol: string };
};

type MovimientoCaja = {
  id_movimiento: number;
  id_pago: number | null;
  id_rendicion: number | null;
  tipo: string;
  monto: number;
  metodo_pago: string | null;
  descripcion: string | null;
  created_at: string;
};

type RendicionCaja = {
  id_rendicion: number;
  estado: string;
  total_sistema: number;
  monto_contado: number | null;
  ajuste_manual: number;
  motivo_ajuste: string | null;
  comprobante_url: string | null;
  cerrada_at: string;
};

function toNumber(value: string): number {
  return Number(String(value).trim().replace(",", "."));
}

export function CajasPage() {
  const api = useApi();
  const { user } = useAuth();
  const [cajas, setCajas] = useState<CajaResumen[]>([]);
  const [selectedCaja, setSelectedCaja] = useState<number | null>(null);
  const [movimientos, setMovimientos] = useState<MovimientoCaja[]>([]);
  const [rendiciones, setRendiciones] = useState<RendicionCaja[]>([]);
  const [msg, setMsg] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const canManageAll = user?.rol === "Admin" || user?.rol === "Coordinador";

  const [form, setForm] = useState({
    monto_contado: "",
    ajuste_manual: "",
    motivo_ajuste: "",
    comprobante_url: "",
  });

  const selectedCajaInfo = useMemo(() => cajas.find((c) => c.id_caja === selectedCaja) ?? null, [cajas, selectedCaja]);

  async function loadCajas() {
    setLoading(true);
    setMsg(null);
    try {
      if (canManageAll) {
        const data = await api.get<CajaResumen[]>("/cajas");
        setCajas(data);
        setSelectedCaja((prev) => prev ?? data[0]?.id_caja ?? null);
      } else {
        const mine = await api.get<CajaResumen>("/cajas/me");
        setCajas([mine]);
        setSelectedCaja(mine.id_caja);
      }
    } catch {
      setMsg("No se pudieron cargar las cajas");
      setCajas([]);
      setSelectedCaja(null);
    } finally {
      setLoading(false);
    }
  }

  async function loadCajaDetails(idCaja: number) {
    try {
      const [movs, rends] = await Promise.all([
        api.get<MovimientoCaja[]>(`/cajas/${idCaja}/movimientos`),
        api.get<RendicionCaja[]>(`/cajas/${idCaja}/rendiciones`),
      ]);
      setMovimientos(movs);
      setRendiciones(rends);
    } catch {
      setMovimientos([]);
      setRendiciones([]);
      setMsg("No se pudo cargar el detalle de caja");
    }
  }

  useEffect(() => {
    loadCajas();
  }, [canManageAll]);

  useEffect(() => {
    if (!selectedCaja) {
      setMovimientos([]);
      setRendiciones([]);
      return;
    }
    loadCajaDetails(selectedCaja);
  }, [selectedCaja]);

  async function onCerrarRendicion(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedCaja) return;
    setMsg(null);
    const payload: Record<string, unknown> = {};
    if (form.monto_contado.trim()) payload.monto_contado = toNumber(form.monto_contado);
    if (form.ajuste_manual.trim()) payload.ajuste_manual = toNumber(form.ajuste_manual);
    if (form.motivo_ajuste.trim()) payload.motivo_ajuste = form.motivo_ajuste.trim();
    if (form.comprobante_url.trim()) payload.comprobante_url = form.comprobante_url.trim();
    try {
      await api.post(`/cajas/${selectedCaja}/rendiciones/cerrar`, payload);
      setMsg("Rendición cerrada");
      setForm({ monto_contado: "", ajuste_manual: "", motivo_ajuste: "", comprobante_url: "" });
      await loadCajas();
      await loadCajaDetails(selectedCaja);
    } catch (e2) {
      const err = e2 as ApiError;
      if (err.status === 422) setMsg("Revisá los datos: si hay ajuste manual, el motivo es obligatorio");
      else setMsg("No se pudo cerrar la rendición");
    }
  }

  return (
    <Layout>
      <div className="space-y-4">
        <div className="rounded-2xl border bg-white p-6 space-y-3">
          <h1 className="text-xl font-semibold">{canManageAll ? "Cajas" : "Mi caja"}</h1>
          <p className="text-sm text-slate-600">
            {canManageAll
              ? "Visualizá cajas de usuarios, cotejá y cerrá rendiciones."
              : "Vista de solo lectura de tus movimientos y rendiciones."}
          </p>
          {msg && <div className="text-sm text-slate-700">{msg}</div>}
          {canManageAll && cajas.length > 0 && (
            <select
              className="rounded-lg border px-3 py-2 text-sm"
              value={selectedCaja ?? ""}
              onChange={(e) => setSelectedCaja(Number(e.target.value))}
            >
              {cajas.map((c) => (
                <option key={c.id_caja} value={c.id_caja}>
                  {c.usuario?.username ?? `Usuario #${c.id_usuario}`} · Saldo ${c.saldo_actual.toFixed(2)}
                </option>
              ))}
            </select>
          )}
        </div>

        {loading && <div className="text-sm text-slate-600">Cargando…</div>}
        {!loading && selectedCajaInfo && (
          <>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="rounded-2xl border bg-white p-6">
                <div className="text-sm text-slate-600">Saldo actual</div>
                <div className="mt-2 text-2xl font-semibold">${selectedCajaInfo.saldo_actual.toFixed(2)}</div>
              </div>
              <div className="rounded-2xl border bg-white p-6">
                <div className="text-sm text-slate-600">Pendiente a rendir</div>
                <div className="mt-2 text-2xl font-semibold">${selectedCajaInfo.total_pendiente.toFixed(2)}</div>
              </div>
              <div className="rounded-2xl border bg-white p-6">
                <div className="text-sm text-slate-600">Movimientos pendientes</div>
                <div className="mt-2 text-2xl font-semibold">{selectedCajaInfo.cantidad_pendientes}</div>
              </div>
            </div>

            {canManageAll && (
              <div className="rounded-2xl border bg-white p-6">
                <h2 className="text-lg font-semibold mb-3">Cerrar rendición</h2>
                <form onSubmit={onCerrarRendicion} className="grid md:grid-cols-2 gap-2 text-sm">
                  <input
                    className="rounded-lg border px-3 py-2"
                    placeholder="Monto contado (opcional)"
                    inputMode="decimal"
                    value={form.monto_contado}
                    onChange={(e) => setForm((f) => ({ ...f, monto_contado: e.target.value }))}
                  />
                  <input
                    className="rounded-lg border px-3 py-2"
                    placeholder="Ajuste manual (+/-) opcional"
                    inputMode="decimal"
                    value={form.ajuste_manual}
                    onChange={(e) => setForm((f) => ({ ...f, ajuste_manual: e.target.value }))}
                  />
                  <input
                    className="rounded-lg border px-3 py-2 md:col-span-2"
                    placeholder="Motivo de ajuste (obligatorio si hay ajuste)"
                    value={form.motivo_ajuste}
                    onChange={(e) => setForm((f) => ({ ...f, motivo_ajuste: e.target.value }))}
                  />
                  <input
                    className="rounded-lg border px-3 py-2 md:col-span-2"
                    placeholder="Comprobante URL (opcional)"
                    value={form.comprobante_url}
                    onChange={(e) => setForm((f) => ({ ...f, comprobante_url: e.target.value }))}
                  />
                  <div className="md:col-span-2">
                    <button className="rounded-lg bg-slate-900 px-4 py-2 text-white">Cerrar rendición</button>
                  </div>
                </form>
              </div>
            )}

            <div className="rounded-2xl border bg-white p-6">
              <h2 className="text-lg font-semibold mb-3">Movimientos</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="text-xs uppercase text-slate-500">
                    <tr>
                      <th className="py-2 text-left">Fecha</th>
                      <th className="py-2 text-left">Tipo</th>
                      <th className="py-2 text-left">Monto</th>
                      <th className="py-2 text-left">Método</th>
                      <th className="py-2 text-left">Estado</th>
                    </tr>
                  </thead>
                  <tbody>
                    {movimientos.map((m) => (
                      <tr key={m.id_movimiento} className="border-t">
                        <td className="py-2">{new Date(m.created_at).toLocaleString()}</td>
                        <td className="py-2">{m.tipo}</td>
                        <td className="py-2">${m.monto.toFixed(2)}</td>
                        <td className="py-2">{m.metodo_pago ?? "—"}</td>
                        <td className="py-2">{m.id_rendicion ? "Rendido" : "Pendiente"}</td>
                      </tr>
                    ))}
                    {movimientos.length === 0 && (
                      <tr>
                        <td className="py-2 text-slate-600" colSpan={5}>
                          No hay movimientos.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="rounded-2xl border bg-white p-6">
              <h2 className="text-lg font-semibold mb-3">Rendiciones</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="text-xs uppercase text-slate-500">
                    <tr>
                      <th className="py-2 text-left">Fecha</th>
                      <th className="py-2 text-left">Total sistema</th>
                      <th className="py-2 text-left">Contado</th>
                      <th className="py-2 text-left">Ajuste</th>
                      <th className="py-2 text-left">Comprobante</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rendiciones.map((r) => (
                      <tr key={r.id_rendicion} className="border-t">
                        <td className="py-2">{new Date(r.cerrada_at).toLocaleString()}</td>
                        <td className="py-2">${r.total_sistema.toFixed(2)}</td>
                        <td className="py-2">{r.monto_contado !== null ? `$${r.monto_contado.toFixed(2)}` : "—"}</td>
                        <td className="py-2">${r.ajuste_manual.toFixed(2)}</td>
                        <td className="py-2">
                          {r.comprobante_url ? (
                            <a className="underline" href={r.comprobante_url} target="_blank" rel="noreferrer">
                              Ver
                            </a>
                          ) : (
                            "—"
                          )}
                        </td>
                      </tr>
                    ))}
                    {rendiciones.length === 0 && (
                      <tr>
                        <td className="py-2 text-slate-600" colSpan={5}>
                          No hay rendiciones.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>
    </Layout>
  );
}

