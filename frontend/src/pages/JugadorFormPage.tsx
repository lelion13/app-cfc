import React, { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Layout } from "../components/Layout";
import { ApiError, useApi } from "../lib/api";

type Categoria = { id_categoria: number; descripcion: string };
type FormState = { nombre: string; apellido: string; fecha_nacimiento: string; tipo_documento: string; numero_documento: string; domicilio: string; nombre_tutor: string; apellido_tutor: string; celular_tutor: string; mail_tutor: string; id_categoria: string; activo: boolean };
const DOC_TYPES = ["DNI", "LC", "LE", "PASAPORTE"] as const;

const empty: FormState = { nombre: "", apellido: "", fecha_nacimiento: "", tipo_documento: "DNI", numero_documento: "", domicilio: "", nombre_tutor: "", apellido_tutor: "", celular_tutor: "", mail_tutor: "", id_categoria: "", activo: true };

export function JugadorFormPage() {
  const api = useApi();
  const nav = useNavigate();
  const { id } = useParams();
  const isEdit = Boolean(id);
  const [cats, setCats] = useState<Categoria[]>([]);
  const [form, setForm] = useState<FormState>(empty);
  const [msg, setMsg] = useState<string | null>(null);

  useEffect(() => { api.get<Categoria[]>("/categorias").then(setCats).catch(() => setCats([])); }, [api]);
  useEffect(() => {
    if (!isEdit || !id) return;
    api.get<any>(`/jugadores/${id}`).then(j => setForm({ ...empty, ...j, id_categoria: String(j.id_categoria), domicilio: j.domicilio ?? "", nombre_tutor: j.nombre_tutor ?? "", apellido_tutor: j.apellido_tutor ?? "", celular_tutor: j.celular_tutor ?? "", mail_tutor: j.mail_tutor ?? "" }));
  }, [api, id, isEdit]);

  async function save(e: React.FormEvent) {
    e.preventDefault();
    if (!DOC_TYPES.includes(form.tipo_documento as (typeof DOC_TYPES)[number])) {
      setMsg("Tipo de documento inválido");
      return;
    }
    const payload = { ...form, id_categoria: Number(form.id_categoria), domicilio: form.domicilio || null, nombre_tutor: form.nombre_tutor || null, apellido_tutor: form.apellido_tutor || null, celular_tutor: form.celular_tutor || null, mail_tutor: form.mail_tutor || null };
    try {
      if (isEdit && id) {
        await api.patch(`/jugadores/${id}`, payload);
        nav(`/jugadores/${id}`);
      } else {
        const created = await api.post<{ id_jugador: number }>("/jugadores", payload);
        nav(`/jugadores/${created.id_jugador}`);
      }
    } catch (e) {
      setMsg((e as ApiError).status === 409 ? "Jugador duplicado por documento" : "Error al guardar");
    }
  }

  return (
    <Layout>
      <div className="rounded-2xl border bg-white p-6">
        <h1 className="text-xl font-semibold">{isEdit ? "Editar jugador" : "Nuevo jugador"}</h1>
        {msg && <div className="text-sm text-red-700 mt-2">{msg}</div>}
        <form onSubmit={save} className="mt-4 grid md:grid-cols-2 gap-3 text-sm">
          {(["nombre","apellido","fecha_nacimiento"] as const).map((k) => (
            <input key={k} type={k==="fecha_nacimiento" ? "date" : k==="mail_tutor" ? "email" : "text"} className="rounded-lg border px-3 py-2" placeholder={k} value={(form as any)[k]} onChange={e => setForm(v => ({ ...v, [k]: e.target.value }))} />
          ))}
          <select
            className="rounded-lg border px-3 py-2"
            value={form.tipo_documento}
            onChange={e => setForm(v => ({ ...v, tipo_documento: e.target.value }))}
          >
            {DOC_TYPES.map(dt => (
              <option key={dt} value={dt}>
                {dt}
              </option>
            ))}
            {!DOC_TYPES.includes(form.tipo_documento as (typeof DOC_TYPES)[number]) && form.tipo_documento && (
              <option value={form.tipo_documento}>{form.tipo_documento}</option>
            )}
          </select>
          <input
            type="text"
            className="rounded-lg border px-3 py-2"
            placeholder="numero_documento"
            value={form.numero_documento}
            onChange={e => setForm(v => ({ ...v, numero_documento: e.target.value }))}
          />
          {(["domicilio","nombre_tutor","apellido_tutor","celular_tutor","mail_tutor"] as const).map((k) => (
            <input key={k} type={k==="mail_tutor" ? "email" : "text"} className="rounded-lg border px-3 py-2" placeholder={k} value={(form as any)[k]} onChange={e => setForm(v => ({ ...v, [k]: e.target.value }))} />
          ))}
          <select className="rounded-lg border px-3 py-2" value={form.id_categoria} onChange={e => setForm(v => ({ ...v, id_categoria: e.target.value }))}>
            <option value="">Categoría</option>{cats.map(c => <option key={c.id_categoria} value={String(c.id_categoria)}>{c.descripcion}</option>)}
          </select>
          <label className="flex items-center gap-2"><input type="checkbox" checked={form.activo} onChange={e => setForm(v => ({ ...v, activo: e.target.checked }))} />Activo</label>
          <div className="md:col-span-2 space-x-2">
            <button className="rounded-lg bg-slate-900 px-4 py-2 text-white">Guardar</button>
            <Link className="rounded-lg border px-4 py-2" to="/jugadores">Cancelar</Link>
          </div>
        </form>
      </div>
    </Layout>
  );
}
