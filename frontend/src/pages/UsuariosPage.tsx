import React, { useEffect, useState } from "react";
import { Layout } from "../components/Layout";
import { ApiError, useApi } from "../lib/api";
import { useAuth } from "../state/auth";

type Rol = "Admin" | "Coordinador";

type UserRow = {
  id_usuario: number;
  username: string;
  rol: Rol;
  activo: boolean;
  created_at: string;
  updated_at: string;
};

export function UsuariosPage() {
  const api = useApi();
  const { user } = useAuth();
  const [users, setUsers] = useState<UserRow[]>([]);
  const [newUsername, setNewUsername] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newRol, setNewRol] = useState<Rol>("Coordinador");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editRol, setEditRol] = useState<Rol>("Coordinador");
  const [editActivo, setEditActivo] = useState(true);
  const [editPassword, setEditPassword] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const list = await api.get<UserRow[]>("/usuarios");
      setUsers(list);
    } catch {
      setUsers([]);
      setMsg("No se pudo cargar la lista");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [api]);

  async function createUser() {
    setMsg(null);
    try {
      const u = await api.post<UserRow>("/usuarios", {
        username: newUsername.trim(),
        password: newPassword,
        rol: newRol
      });
      setUsers(prev => [...prev, u].sort((a, b) => a.username.localeCompare(b.username)));
      setNewUsername("");
      setNewPassword("");
      setNewRol("Coordinador");
      setMsg("Usuario creado");
    } catch (e) {
      const err = e as ApiError;
      setMsg(err.status === 409 ? "El usuario ya existe" : "Error al crear");
    }
  }

  function startEdit(u: UserRow) {
    setEditingId(u.id_usuario);
    setEditRol(u.rol);
    setEditActivo(u.activo);
    setEditPassword("");
    setMsg(null);
  }

  async function saveEdit(id: number) {
    setMsg(null);
    const body: { rol: Rol; activo: boolean; password?: string } = { rol: editRol, activo: editActivo };
    if (editPassword.trim().length > 0) {
      if (editPassword.length < 10) {
        setMsg("La contraseña debe tener al menos 10 caracteres");
        return;
      }
      body.password = editPassword;
    }
    try {
      const updated = await api.patch<UserRow>(`/usuarios/${id}`, body);
      setUsers(prev => prev.map(x => (x.id_usuario === id ? updated : x)).sort((a, b) => a.username.localeCompare(b.username)));
      setEditingId(null);
      setMsg("Usuario actualizado");
    } catch (e) {
      const err = e as ApiError;
      if (err.status === 409) setMsg("No se puede dejar al sistema sin administrador activo");
      else if (err.status === 403) setMsg("No tenés permisos");
      else setMsg("Error al actualizar");
    }
  }

  async function removeUser(u: UserRow) {
    if (user?.rol !== "Admin") return;
    if (!window.confirm(`¿Eliminar usuario ${u.username}?`)) return;
    setMsg(null);
    try {
      await api.del<void>(`/usuarios/${u.id_usuario}`);
      setUsers(prev => prev.filter(x => x.id_usuario !== u.id_usuario));
      setMsg("Usuario eliminado");
    } catch (e) {
      const err = e as ApiError;
      if (err.status === 409) setMsg("No se puede eliminar al último administrador");
      else if (err.status === 403) setMsg(err.detail === "Cannot delete self" ? "No podés eliminarte a vos mismo" : "No tenés permisos");
      else setMsg("Error al eliminar");
    }
  }

  function fmtDate(iso: string) {
    try {
      return new Date(iso).toLocaleString();
    } catch {
      return iso;
    }
  }

  return (
    <Layout>
      <div className="rounded-2xl border bg-white p-6 space-y-4">
        <h1 className="text-xl font-semibold">Usuarios</h1>

        <div className="rounded-lg border border-slate-200 p-4 space-y-2">
          <div className="text-sm font-medium text-slate-800">Nuevo usuario</div>
          <div className="flex flex-col sm:flex-row gap-2 flex-wrap">
            <input
              className="rounded-lg border px-3 py-2 text-sm flex-1 min-w-[140px]"
              placeholder="Usuario"
              value={newUsername}
              onChange={e => setNewUsername(e.target.value)}
              minLength={3}
            />
            <input
              className="rounded-lg border px-3 py-2 text-sm flex-1 min-w-[140px]"
              placeholder="Contraseña (mín. 10)"
              type="password"
              value={newPassword}
              onChange={e => setNewPassword(e.target.value)}
              minLength={10}
            />
            <select className="rounded-lg border px-3 py-2 text-sm" value={newRol} onChange={e => setNewRol(e.target.value as Rol)}>
              <option value="Coordinador">Coordinador</option>
              <option value="Admin">Admin</option>
            </select>
            <button type="button" className="rounded-lg bg-slate-900 px-4 py-2 text-sm text-white" onClick={createUser}>
              Crear
            </button>
          </div>
        </div>

        {msg && <div className="text-sm text-slate-700">{msg}</div>}
        {loading ? (
          <div className="text-sm text-slate-600">Cargando…</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-slate-600">
                  <th className="py-2 pr-2">Usuario</th>
                  <th className="py-2 pr-2">Rol</th>
                  <th className="py-2 pr-2">Activo</th>
                  <th className="py-2 pr-2 hidden md:table-cell">Creado</th>
                  <th className="py-2 text-right">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id_usuario} className="border-t align-top">
                    <td className="py-2 pr-2">{u.username}</td>
                    <td className="py-2 pr-2">
                      {editingId === u.id_usuario ? (
                        <select className="rounded border px-2 py-1 text-sm" value={editRol} onChange={e => setEditRol(e.target.value as Rol)}>
                          <option value="Coordinador">Coordinador</option>
                          <option value="Admin">Admin</option>
                        </select>
                      ) : (
                        u.rol
                      )}
                    </td>
                    <td className="py-2 pr-2">
                      {editingId === u.id_usuario ? (
                        <label className="inline-flex items-center gap-1 text-sm">
                          <input type="checkbox" checked={editActivo} onChange={e => setEditActivo(e.target.checked)} />
                          Activo
                        </label>
                      ) : (
                        u.activo ? "Sí" : "No"
                      )}
                    </td>
                    <td className="py-2 pr-2 hidden md:table-cell text-xs text-slate-600">{fmtDate(u.created_at)}</td>
                    <td className="py-2 text-right space-x-2 whitespace-nowrap">
                      {editingId === u.id_usuario ? (
                        <>
                          <div className="mb-1 text-left">
                            <input
                              className="w-full max-w-[200px] rounded border px-2 py-1 text-xs"
                              placeholder="Nueva contraseña (opcional)"
                              type="password"
                              value={editPassword}
                              onChange={e => setEditPassword(e.target.value)}
                            />
                          </div>
                          <button type="button" className="rounded border px-2 py-1" onClick={() => saveEdit(u.id_usuario)}>
                            Guardar
                          </button>
                          <button type="button" className="rounded border px-2 py-1" onClick={() => setEditingId(null)}>
                            Cancelar
                          </button>
                        </>
                      ) : (
                        <>
                          <button type="button" className="rounded border px-2 py-1" onClick={() => startEdit(u)}>
                            Editar
                          </button>
                          {user?.rol === "Admin" && (
                            <button type="button" className="rounded border px-2 py-1 text-red-700" onClick={() => removeUser(u)}>
                              Eliminar
                            </button>
                          )}
                        </>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Layout>
  );
}
