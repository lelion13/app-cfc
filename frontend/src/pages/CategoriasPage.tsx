import React, { useEffect, useState } from "react";
import { Layout } from "../components/Layout";
import { ApiError, useApi } from "../lib/api";
import { useAuth } from "../state/auth";

type Categoria = { id_categoria: number; descripcion: string };

export function CategoriasPage() {
  const api = useApi();
  const { user } = useAuth();
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [newDesc, setNewDesc] = useState("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editingDesc, setEditingDesc] = useState("");
  const [msg, setMsg] = useState<string | null>(null);

  async function load() {
    setCategorias(await api.get<Categoria[]>("/categorias"));
  }
  useEffect(() => {
    load();
  }, [api]);

  async function createCategoria() {
    try {
      const c = await api.post<Categoria>("/categorias", { descripcion: newDesc.trim() });
      setCategorias(prev => [...prev, c]);
      setNewDesc("");
      setMsg("Categoría creada");
    } catch (e) {
      setMsg((e as ApiError).status === 409 ? "La categoría ya existe" : "Error al crear");
    }
  }

  async function saveEdit(id: number) {
    try {
      const updated = await api.patch<Categoria>(`/categorias/${id}`, { descripcion: editingDesc.trim() });
      setCategorias(prev => prev.map(c => (c.id_categoria === id ? updated : c)));
      setEditingId(null);
      setMsg("Categoría actualizada");
    } catch (e) {
      setMsg((e as ApiError).status === 409 ? "La categoría ya existe" : "Error al actualizar");
    }
  }

  async function removeCategoria(c: Categoria) {
    if (user?.rol !== "Admin") return;
    if (!window.confirm(`¿Eliminar ${c.descripcion}?`)) return;
    try {
      await api.del<void>(`/categorias/${c.id_categoria}`);
      setCategorias(prev => prev.filter(x => x.id_categoria !== c.id_categoria));
      setMsg("Categoría eliminada");
    } catch (e) {
      const err = e as ApiError;
      if (err.status === 409) setMsg("No se puede borrar: tiene jugadores asociados");
      else if (err.status === 403) setMsg("No tenés permisos");
      else setMsg("Error al eliminar");
    }
  }

  return (
    <Layout>
      <div className="rounded-2xl border bg-white p-6 space-y-4">
        <h1 className="text-xl font-semibold">Categorías</h1>
        <div className="flex gap-2">
          <input className="rounded-lg border px-3 py-2 text-sm flex-1" value={newDesc} onChange={e => setNewDesc(e.target.value)} placeholder="Descripción" />
          <button className="rounded-lg bg-slate-900 px-4 py-2 text-sm text-white" onClick={createCategoria}>Crear</button>
        </div>
        {msg && <div className="text-sm text-slate-700">{msg}</div>}
        <table className="w-full text-sm">
          <tbody>
            {categorias.map(c => (
              <tr key={c.id_categoria} className="border-t">
                <td className="py-2">
                  {editingId === c.id_categoria ? (
                    <input className="rounded border px-2 py-1" value={editingDesc} onChange={e => setEditingDesc(e.target.value)} />
                  ) : (
                    c.descripcion
                  )}
                </td>
                <td className="py-2 text-right space-x-2">
                  {editingId === c.id_categoria ? (
                    <>
                      <button className="rounded border px-2 py-1" onClick={() => saveEdit(c.id_categoria)}>Guardar</button>
                      <button className="rounded border px-2 py-1" onClick={() => setEditingId(null)}>Cancelar</button>
                    </>
                  ) : (
                    <>
                      <button className="rounded border px-2 py-1" onClick={() => { setEditingId(c.id_categoria); setEditingDesc(c.descripcion); }}>Editar</button>
                      {(user?.rol === "Admin" || user?.rol === "Coordinador") && <button className="rounded border px-2 py-1 text-red-700" onClick={() => removeCategoria(c)}>Eliminar</button>}
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Layout>
  );
}
