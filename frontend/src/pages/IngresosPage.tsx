import React, { useEffect, useMemo, useState } from "react";
import { Layout } from "../components/Layout";
import { useApi } from "../lib/api";

type Categoria = { id_categoria: number; descripcion: string };
type ItemPago = { id_item_pago: number; codigo: string; descripcion: string; activo: boolean };
type IngresoResumen = { total_ingresos: number; cantidad_pagos: number };

function currentMonth() {
  return String(new Date().getMonth() + 1);
}

function currentYear() {
  return String(new Date().getFullYear());
}

export function IngresosPage() {
  const api = useApi();
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [itemsPago, setItemsPago] = useState<ItemPago[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [resumen, setResumen] = useState<IngresoResumen>({ total_ingresos: 0, cantidad_pagos: 0 });

  const [anio, setAnio] = useState(currentYear());
  const [mes, setMes] = useState(currentMonth());
  const [idCategoria, setIdCategoria] = useState("");
  const [idItemPago, setIdItemPago] = useState("");

  const query = useMemo(() => {
    const p = new URLSearchParams();
    if (anio) p.set("anio", anio);
    if (mes) p.set("mes", mes);
    if (idCategoria) p.set("id_categoria", idCategoria);
    if (idItemPago) p.set("id_item_pago", idItemPago);
    return p.toString();
  }, [anio, mes, idCategoria, idItemPago]);

  async function loadResumen() {
    setLoading(true);
    setError(null);
    try {
      const data = await api.get<IngresoResumen>(`/ingresos/resumen${query ? `?${query}` : ""}`);
      setResumen(data);
    } catch {
      setError("No se pudo cargar el resumen de ingresos");
      setResumen({ total_ingresos: 0, cantidad_pagos: 0 });
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadResumen();
  }, [api, query]);

  useEffect(() => {
    api.get<Categoria[]>("/categorias").then(setCategorias).catch(() => setCategorias([]));
    api.get<ItemPago[]>("/items-pago").then((res) => setItemsPago(res.filter((x) => x.activo))).catch(() => setItemsPago([]));
  }, [api]);

  return (
    <Layout>
      <div className="space-y-4">
        <div className="rounded-2xl border bg-white p-6 space-y-3">
          <h1 className="text-xl font-semibold">Ingresos</h1>
          <p className="text-sm text-slate-600">Resumen de ingresos según los filtros aplicados.</p>

          <div className="grid md:grid-cols-4 gap-2 text-sm">
            <input className="rounded-lg border px-3 py-2" placeholder="Año" value={anio} onChange={(e) => setAnio(e.target.value)} />
            <input className="rounded-lg border px-3 py-2" placeholder="Mes" value={mes} onChange={(e) => setMes(e.target.value)} />
            <select className="rounded-lg border px-3 py-2" value={idCategoria} onChange={(e) => setIdCategoria(e.target.value)}>
              <option value="">Categoría</option>
              {categorias.map((c) => (
                <option key={c.id_categoria} value={String(c.id_categoria)}>
                  {c.descripcion}
                </option>
              ))}
            </select>
            <select className="rounded-lg border px-3 py-2" value={idItemPago} onChange={(e) => setIdItemPago(e.target.value)}>
              <option value="">Item de pago</option>
              {itemsPago.map((it) => (
                <option key={it.id_item_pago} value={String(it.id_item_pago)}>
                  {it.descripcion}
                </option>
              ))}
            </select>
          </div>

          <div className="flex gap-2">
            <button className="rounded-lg border px-3 py-2 text-sm" onClick={() => loadResumen()}>
              Aplicar filtros
            </button>
            <button
              className="rounded-lg border px-3 py-2 text-sm"
              onClick={() => {
                setAnio(currentYear());
                setMes(currentMonth());
                setIdCategoria("");
                setIdItemPago("");
              }}
            >
              Limpiar
            </button>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          <div className="rounded-2xl border bg-white p-6">
            <div className="text-sm text-slate-600">Total ingresos</div>
            <div className="mt-2 text-3xl font-semibold">
              {loading ? "..." : `$${resumen.total_ingresos.toFixed(2)}`}
            </div>
          </div>
          <div className="rounded-2xl border bg-white p-6">
            <div className="text-sm text-slate-600">Cantidad de pagos</div>
            <div className="mt-2 text-3xl font-semibold">{loading ? "..." : resumen.cantidad_pagos}</div>
          </div>
        </div>

        {error && <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}
      </div>
    </Layout>
  );
}
