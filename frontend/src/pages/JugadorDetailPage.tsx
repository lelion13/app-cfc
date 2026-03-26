import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Layout } from "../components/Layout";
import { useApi } from "../lib/api";

export function JugadorDetailPage() {
  const api = useApi();
  const { id } = useParams();
  const [jugador, setJugador] = useState<any>(null);
  useEffect(() => {
    if (!id) return;
    api.get(`/jugadores/${id}`).then(setJugador).catch(() => setJugador(null));
  }, [api, id]);
  return (
    <Layout>
      <div className="rounded-2xl border bg-white p-6">
        <div className="flex justify-between items-center">
          <h1 className="text-xl font-semibold">Detalle de jugador</h1>
          <div className="space-x-3">
            {id && <Link to={`/jugadores/${id}/editar`} className="rounded border px-3 py-1 text-sm">Editar</Link>}
            <Link to="/jugadores" className="text-sm hover:underline">Volver</Link>
          </div>
        </div>
        {jugador && (
          <div className="mt-4 grid md:grid-cols-2 gap-3 text-sm">
            <div><div className="text-slate-500">Nombre</div><div>{jugador.apellido}, {jugador.nombre}</div></div>
            <div><div className="text-slate-500">Categoría</div><div>{jugador.categoria?.descripcion ?? "—"}</div></div>
            <div><div className="text-slate-500">Documento</div><div>{jugador.tipo_documento} {jugador.numero_documento}</div></div>
            <div><div className="text-slate-500">Fecha de nacimiento</div><div>{jugador.fecha_nacimiento}</div></div>
            <div className="md:col-span-2"><div className="text-slate-500">Domicilio</div><div>{jugador.domicilio ?? "—"}</div></div>
            <div><div className="text-slate-500">Tutor nombre</div><div>{jugador.nombre_tutor ?? "—"}</div></div>
            <div><div className="text-slate-500">Tutor apellido</div><div>{jugador.apellido_tutor ?? "—"}</div></div>
            <div><div className="text-slate-500">Tutor celular</div><div>{jugador.celular_tutor ?? "—"}</div></div>
            <div><div className="text-slate-500">Tutor mail</div><div>{jugador.mail_tutor ?? "—"}</div></div>
          </div>
        )}
      </div>
    </Layout>
  );
}
