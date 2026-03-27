import React, { useEffect, useState } from "react";
import { Layout } from "../components/Layout";
import { ApiError, useApi } from "../lib/api";

type ItemPago = { id_item_pago: number; codigo: string; descripcion: string; activo: boolean };
type PrecioItem = {
  id_precio_item: number;
  id_item_pago: number;
  id_categoria: number | null;
  monto: number;
  vigencia_desde: string;
  vigencia_hasta: string | null;
  activo: boolean;
};
type Categoria = { id_categoria: number; descripcion: string };

export function ArancelesPage() {
  const api = useApi();
  const [items, setItems] = useState<ItemPago[]>([]);
  const [precios, setPrecios] = useState<PrecioItem[]>([]);
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [msg, setMsg] = useState<string | null>(null);
  const [itemEditId, setItemEditId] = useState<number | null>(null);
  const [precioEditId, setPrecioEditId] = useState<number | null>(null);

  const [itemForm, setItemForm] = useState({ codigo: "", descripcion: "", activo: true });
  const [precioForm, setPrecioForm] = useState({
    id_item_pago: "",
    id_categoria: "",
    monto: "",
    vigencia_desde: "",
    vigencia_hasta: "",
    activo: true,
  });

  async function load() {
    try {
      const [it, pr, cat] = await Promise.all([
        api.get<ItemPago[]>("/items-pago"),
        api.get<PrecioItem[]>("/items-pago/precios"),
        api.get<Categoria[]>("/categorias"),
      ]);
      setItems(it);
      setPrecios(pr);
      setCategorias(cat);
    } catch {
      setMsg("No se pudo cargar aranceles");
    }
  }

  useEffect(() => {
    load();
  }, [api]);

  async function saveItem(e: React.FormEvent) {
    e.preventDefault();
    setMsg(null);
    try {
      if (itemEditId) {
        await api.patch(`/items-pago/${itemEditId}`, itemForm);
        setMsg("Item actualizado");
      } else {
        await api.post("/items-pago", itemForm);
        setMsg("Item creado");
      }
      setItemForm({ codigo: "", descripcion: "", activo: true });
      setItemEditId(null);
      await load();
    } catch (err) {
      const e2 = err as ApiError;
      setMsg(e2.status === 409 ? "Código duplicado" : "No se pudo guardar item");
    }
  }

  async function savePrecio(e: React.FormEvent) {
    e.preventDefault();
    setMsg(null);
    const payload = {
      id_item_pago: Number(precioForm.id_item_pago),
      id_categoria: precioForm.id_categoria ? Number(precioForm.id_categoria) : null,
      monto: Number(precioForm.monto),
      vigencia_desde: precioForm.vigencia_desde,
      vigencia_hasta: precioForm.vigencia_hasta || null,
      activo: precioForm.activo,
    };
    try {
      if (precioEditId) {
        await api.patch(`/items-pago/precios/${precioEditId}`, payload);
        setMsg("Precio actualizado");
      } else {
        await api.post("/items-pago/precios", payload);
        setMsg("Precio creado");
      }
      setPrecioForm({ id_item_pago: "", id_categoria: "", monto: "", vigencia_desde: "", vigencia_hasta: "", activo: true });
      setPrecioEditId(null);
      await load();
    } catch (err) {
      const e2 = err as ApiError;
      if (e2.status === 409) setMsg("Vigencia superpuesta para item/categoría");
      else setMsg("No se pudo guardar precio");
    }
  }

  return (
    <Layout>
      <div className="space-y-4">
        <div className="rounded-2xl border bg-white p-6 space-y-3">
          <h1 className="text-xl font-semibold">Aranceles</h1>
          <p className="text-sm text-slate-600">Administrá ítems tabulados y sus precios por vigencia.</p>
          {msg && <div className="text-sm text-slate-700">{msg}</div>}
        </div>

        <div className="rounded-2xl border bg-white p-6 space-y-3">
          <h2 className="text-lg font-semibold">Items de pago</h2>
          <form onSubmit={saveItem} className="grid md:grid-cols-4 gap-2 text-sm">
            <input className="rounded-lg border px-3 py-2" placeholder="Código" value={itemForm.codigo} onChange={(e) => setItemForm((f) => ({ ...f, codigo: e.target.value }))} required />
            <input className="rounded-lg border px-3 py-2 md:col-span-2" placeholder="Descripción" value={itemForm.descripcion} onChange={(e) => setItemForm((f) => ({ ...f, descripcion: e.target.value }))} required />
            <label className="flex items-center gap-2 rounded-lg border px-3 py-2">
              <input type="checkbox" checked={itemForm.activo} onChange={(e) => setItemForm((f) => ({ ...f, activo: e.target.checked }))} />
              Activo
            </label>
            <div className="md:col-span-4 flex gap-2">
              <button className="rounded-lg bg-slate-900 px-4 py-2 text-white">{itemEditId ? "Guardar item" : "Crear item"}</button>
              {itemEditId && (
                <button type="button" className="rounded-lg border px-4 py-2" onClick={() => { setItemEditId(null); setItemForm({ codigo: "", descripcion: "", activo: true }); }}>
                  Cancelar
                </button>
              )}
            </div>
          </form>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="text-xs uppercase text-slate-500">
                <tr><th className="py-2">Código</th><th className="py-2">Descripción</th><th className="py-2">Activo</th><th className="py-2">Acciones</th></tr>
              </thead>
              <tbody>
                {items.map((it) => (
                  <tr key={it.id_item_pago} className="border-t">
                    <td className="py-2">{it.codigo}</td>
                    <td className="py-2">{it.descripcion}</td>
                    <td className="py-2">{it.activo ? "Sí" : "No"}</td>
                    <td className="py-2">
                      <button className="rounded border px-2 py-1" onClick={() => { setItemEditId(it.id_item_pago); setItemForm({ codigo: it.codigo, descripcion: it.descripcion, activo: it.activo }); }}>Editar</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="rounded-2xl border bg-white p-6 space-y-3">
          <h2 className="text-lg font-semibold">Precios por vigencia</h2>
          <form onSubmit={savePrecio} className="grid md:grid-cols-4 gap-2 text-sm">
            <select className="rounded-lg border px-3 py-2" value={precioForm.id_item_pago} onChange={(e) => setPrecioForm((f) => ({ ...f, id_item_pago: e.target.value }))} required>
              <option value="">Item</option>
              {items.map((it) => <option key={it.id_item_pago} value={String(it.id_item_pago)}>{it.descripcion}</option>)}
            </select>
            <select className="rounded-lg border px-3 py-2" value={precioForm.id_categoria} onChange={(e) => setPrecioForm((f) => ({ ...f, id_categoria: e.target.value }))}>
              <option value="">Todas las categorías</option>
              {categorias.map((c) => <option key={c.id_categoria} value={String(c.id_categoria)}>{c.descripcion}</option>)}
            </select>
            <input className="rounded-lg border px-3 py-2" placeholder="Monto" value={precioForm.monto} onChange={(e) => setPrecioForm((f) => ({ ...f, monto: e.target.value }))} required />
            <label className="flex items-center gap-2 rounded-lg border px-3 py-2"><input type="checkbox" checked={precioForm.activo} onChange={(e) => setPrecioForm((f) => ({ ...f, activo: e.target.checked }))} />Activo</label>
            <input type="date" className="rounded-lg border px-3 py-2" value={precioForm.vigencia_desde} onChange={(e) => setPrecioForm((f) => ({ ...f, vigencia_desde: e.target.value }))} required />
            <input type="date" className="rounded-lg border px-3 py-2" value={precioForm.vigencia_hasta} onChange={(e) => setPrecioForm((f) => ({ ...f, vigencia_hasta: e.target.value }))} />
            <div className="md:col-span-4 flex gap-2">
              <button className="rounded-lg bg-slate-900 px-4 py-2 text-white">{precioEditId ? "Guardar precio" : "Crear precio"}</button>
              {precioEditId && (
                <button type="button" className="rounded-lg border px-4 py-2" onClick={() => { setPrecioEditId(null); setPrecioForm({ id_item_pago: "", id_categoria: "", monto: "", vigencia_desde: "", vigencia_hasta: "", activo: true }); }}>
                  Cancelar
                </button>
              )}
            </div>
          </form>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="text-xs uppercase text-slate-500">
                <tr><th className="py-2">Item</th><th className="py-2">Categoría</th><th className="py-2">Monto</th><th className="py-2">Vigencia</th><th className="py-2">Acciones</th></tr>
              </thead>
              <tbody>
                {precios.map((p) => (
                  <tr key={p.id_precio_item} className="border-t">
                    <td className="py-2">{items.find((i) => i.id_item_pago === p.id_item_pago)?.descripcion ?? `#${p.id_item_pago}`}</td>
                    <td className="py-2">{p.id_categoria ? categorias.find((c) => c.id_categoria === p.id_categoria)?.descripcion ?? `#${p.id_categoria}` : "General"}</td>
                    <td className="py-2">${p.monto}</td>
                    <td className="py-2">{p.vigencia_desde} {p.vigencia_hasta ? `a ${p.vigencia_hasta}` : "en adelante"}</td>
                    <td className="py-2">
                      <button
                        className="rounded border px-2 py-1"
                        onClick={() => {
                          setPrecioEditId(p.id_precio_item);
                          setPrecioForm({
                            id_item_pago: String(p.id_item_pago),
                            id_categoria: p.id_categoria ? String(p.id_categoria) : "",
                            monto: String(p.monto),
                            vigencia_desde: p.vigencia_desde,
                            vigencia_hasta: p.vigencia_hasta ?? "",
                            activo: p.activo,
                          });
                        }}
                      >
                        Editar
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </Layout>
  );
}
