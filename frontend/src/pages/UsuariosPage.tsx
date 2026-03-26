import React, { useEffect, useState } from "react";
import { Layout } from "../components/Layout";
import { useApi } from "../lib/api";

export function UsuariosPage() {
  const api = useApi();
  const [users, setUsers] = useState<any[]>([]);
  useEffect(() => {
    api.get<any[]>("/usuarios").then(setUsers).catch(() => setUsers([]));
  }, [api]);
  return (
    <Layout>
      <div className="rounded-2xl border bg-white p-6">
        <h1 className="text-xl font-semibold">Usuarios</h1>
        <ul className="mt-3 divide-y text-sm">
          {users.map(u => <li key={u.id_usuario} className="py-2">{u.username} · {u.rol}</li>)}
        </ul>
      </div>
    </Layout>
  );
}
