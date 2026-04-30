import React, { useCallback, useEffect, useState } from "react";
import { JugadorCombobox } from "../components/JugadorCombobox";
import { Layout } from "../components/Layout";
import { ApiError, useApi } from "../lib/api";
import { useAuth } from "../state/auth";

type CategoriaRow = { id_categoria: number; descripcion: string };
type GoleadorLineOut = { id_jugador: number; nombre: string; apellido: string; goles: number };

type FechaPartidoOut = {
  id_fecha_partido: number;
  fecha_partido: string;
  es_local: boolean;
  rival: string;
  created_at: string;
  updated_at: string;
};

type FechaResumen = {
  id_fecha_partido: number;
  fecha_partido: string;
  es_local: boolean;
  rival: string;
};

type PartidoOut = {
  id_partido: number;
  id_fecha_partido: number;
  id_categoria: number;
  hora_partido: string | null;
  goles_nuestro: number;
  goles_rival: number;
  categoria: CategoriaRow;
  fecha: FechaResumen;
  goleadores: GoleadorLineOut[];
  created_at: string;
  updated_at: string;
};

type FechaPartidoDetailOut = FechaPartidoOut & { partidos: PartidoOut[] };

type GoleadorTorneoOut = { id_jugador: number; nombre: string; apellido: string; goles_totales: number };

type GoleadorLineForm = { id_jugador: string; goles: string };

const emptyFechaForm = { fecha_partido: "", es_local: "true", rival: "" };

function timeToInput(v: string | null): string {
  if (!v) return "";
  return v.length >= 5 ? v.slice(0, 5) : v;
}

function inputToTimeApi(v: string): string | undefined {
  if (!v.trim()) return undefined;
  return v.length === 5 ? `${v}:00` : v;
}

export function PartidosPage() {
  const api = useApi();
  const { user } = useAuth();
  const canDelete = user?.rol === "Admin" || user?.rol === "Coordinador";

  const [fechas, setFechas] = useState<FechaPartidoOut[]>([]);
  const [selectedFechaId, setSelectedFechaId] = useState<number | null>(null);
  const [detalle, setDetalle] = useState<FechaPartidoDetailOut | null>(null);
  const [categorias, setCategorias] = useState<CategoriaRow[]>([]);
  const [loadingFechas, setLoadingFechas] = useState(true);
  const [loadingDetalle, setLoadingDetalle] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const [fechaHeader, setFechaHeader] = useState({ ...emptyFechaForm });
  const [editingFechaId, setEditingFechaId] = useState<number | null>(null);

  const [nuevoPartido, setNuevoPartido] = useState({ id_categoria: "", hora_partido: "" });

  const [goleadoresPartidoId, setGoleadoresPartidoId] = useState<number | null>(null);
  const [goleadores, setGoleadores] = useState<GoleadorLineForm[]>([{ id_jugador: "", goles: "1" }]);

  const [torneoDesde, setTorneoDesde] = useState("");
  const [torneoHasta, setTorneoHasta] = useState("");
  const [torneoRows, setTorneoRows] = useState<GoleadorTorneoOut[]>([]);
  const [loadingTorneo, setLoadingTorneo] = useState(false);

  const loadFechas = useCallback(async () => {
    setLoadingFechas(true);
    try {
      const list = await api.get<FechaPartidoOut[]>("/fechas-partido");
      setFechas(list);
    } catch {
      setMsg("No se pudieron cargar las fechas de encuentro");
      setFechas([]);
    } finally {
      setLoadingFechas(false);
    }
  }, [api]);

  const loadDetalle = useCallback(
    async (id: number) => {
      setLoadingDetalle(true);
      try {
        const d = await api.get<FechaPartidoDetailOut>(`/fechas-partido/${id}`);
        setDetalle(d);
      } catch {
        setMsg("No se pudo cargar el detalle de la fecha");
        setDetalle(null);
      } finally {
        setLoadingDetalle(false);
      }
    },
    [api]
  );

  useEffect(() => {
    api.get<CategoriaRow[]>("/categorias").then(setCategorias).catch(() => setCategorias([]));
  }, [api]);

  useEffect(() => {
    loadFechas();
  }, [loadFechas]);

  useEffect(() => {
    if (selectedFechaId == null) {
      setDetalle(null);
      return;
    }
    loadDetalle(selectedFechaId);
  }, [selectedFechaId, loadDetalle]);

  function resetFechaForm() {
    setFechaHeader({ ...emptyFechaForm });
    setEditingFechaId(null);
  }

  function startEditFecha(f: FechaPartidoOut) {
    setEditingFechaId(f.id_fecha_partido);
    setFechaHeader({
      fecha_partido: f.fecha_partido,
      es_local: f.es_local ? "true" : "false",
      rival: f.rival,
    });
  }

  async function onSubmitFecha(e: React.FormEvent) {
    e.preventDefault();
    setMsg(null);
    const body = {
      fecha_partido: fechaHeader.fecha_partido,
      es_local: fechaHeader.es_local === "true",
      rival: fechaHeader.rival.trim(),
    };
    try {
      if (editingFechaId) {
        await api.patch(`/fechas-partido/${editingFechaId}`, body);
        setMsg("Fecha actualizada");
        resetFechaForm();
        await loadFechas();
        if (selectedFechaId === editingFechaId) await loadDetalle(editingFechaId);
      } else {
        const created = await api.post<FechaPartidoOut>("/fechas-partido", body);
        setMsg("Fecha de encuentro creada");
        setSelectedFechaId(created.id_fecha_partido);
        resetFechaForm();
        await loadFechas();
        await loadDetalle(created.id_fecha_partido);
      }
    } catch (err) {
      const e2 = err as ApiError;
      if (e2.status === 409) setMsg(e2.detail || "Ya existe una fecha para ese día");
      else setMsg("No se pudo guardar la fecha");
    }
  }

  async function onDeleteFecha(f: FechaPartidoOut) {
    setMsg(null);
    if (!canDelete) return;
    if (!window.confirm("¿Eliminar esta fecha y todos los partidos por categoría?")) return;
    try {
      await api.del(`/fechas-partido/${f.id_fecha_partido}`);
      setMsg("Fecha eliminada");
      if (selectedFechaId === f.id_fecha_partido) {
        setSelectedFechaId(null);
        setDetalle(null);
      }
      await loadFechas();
    } catch (err) {
      const e2 = err as ApiError;
      if (e2.status === 403) setMsg("No tenés permisos para eliminar");
      else setMsg("No se pudo eliminar");
    }
  }

  async function onAddPartido(e: React.FormEvent) {
    e.preventDefault();
    if (selectedFechaId == null) return;
    setMsg(null);
    if (!nuevoPartido.id_categoria.trim()) {
      setMsg("Elegí una categoría");
      return;
    }
    const hora = inputToTimeApi(nuevoPartido.hora_partido);
    try {
      await api.post<PartidoOut>("/partidos", {
        id_fecha_partido: selectedFechaId,
        id_categoria: Number(nuevoPartido.id_categoria),
        hora_partido: hora ?? null,
        goles_nuestro: 0,
        goles_rival: 0,
        goleadores: [],
      });
      setMsg("Partido agregado");
      setNuevoPartido({ id_categoria: "", hora_partido: "" });
      await loadDetalle(selectedFechaId);
    } catch (err) {
      const e2 = err as ApiError;
      if (e2.status === 409) setMsg("Ya hay un partido de esa categoría en esta fecha");
      else setMsg("No se pudo crear el partido");
    }
  }

  async function patchMarcador(p: PartidoOut, field: "goles_nuestro" | "goles_rival", delta: number) {
    setMsg(null);
    const cur = field === "goles_nuestro" ? p.goles_nuestro : p.goles_rival;
    const next = Math.max(0, Math.min(99, cur + delta));
    if (next === cur && delta < 0) return;
    try {
      const updated = await api.patch<PartidoOut>(`/partidos/${p.id_partido}`, { [field]: next });
      setDetalle((d) => {
        if (!d || d.id_fecha_partido !== updated.id_fecha_partido) return d;
        return {
          ...d,
          partidos: d.partidos.map((x) => (x.id_partido === updated.id_partido ? updated : x)),
        };
      });
    } catch (err) {
      const e2 = err as ApiError;
      setMsg(e2.status === 400 ? e2.detail || "No se puede actualizar el marcador" : "No se pudo actualizar");
    }
  }

  async function onSaveHora(p: PartidoOut, horaInput: string) {
    setMsg(null);
    const hora = inputToTimeApi(horaInput);
    try {
      const updated = await api.patch<PartidoOut>(`/partidos/${p.id_partido}`, {
        hora_partido: hora === undefined ? null : hora,
      });
      setDetalle((d) => {
        if (!d || d.id_fecha_partido !== updated.id_fecha_partido) return d;
        return {
          ...d,
          partidos: d.partidos.map((x) => (x.id_partido === updated.id_partido ? updated : x)),
        };
      });
      setMsg("Hora actualizada");
    } catch {
      setMsg("No se pudo guardar la hora");
    }
  }

  function openGoleadores(p: PartidoOut) {
    setGoleadoresPartidoId(p.id_partido);
    if (p.goleadores.length === 0) {
      setGoleadores([{ id_jugador: "", goles: "1" }]);
    } else {
      setGoleadores(p.goleadores.map((g) => ({ id_jugador: String(g.id_jugador), goles: String(g.goles) })));
    }
  }

  function buildGoleadoresPayload(): { id_jugador: number; goles: number }[] {
    const out: { id_jugador: number; goles: number }[] = [];
    for (const row of goleadores) {
      if (!row.id_jugador.trim()) continue;
      const g = Number(row.goles);
      if (!Number.isFinite(g) || g < 1) continue;
      out.push({ id_jugador: Number(row.id_jugador), goles: g });
    }
    return out;
  }

  async function onSaveGoleadores() {
    if (goleadoresPartidoId == null || !detalle) return;
    const p = detalle.partidos.find((x) => x.id_partido === goleadoresPartidoId);
    if (!p) return;
    setMsg(null);
    const golesPayload = buildGoleadoresPayload();
    const seen = new Set<number>();
    for (const g of golesPayload) {
      if (seen.has(g.id_jugador)) {
        setMsg("No repetir el mismo jugador en goleadores");
        return;
      }
      seen.add(g.id_jugador);
    }
    try {
      await api.patch(`/partidos/${goleadoresPartidoId}`, { goleadores: golesPayload });
      setMsg("Goleadores guardados");
      await loadDetalle(p.id_fecha_partido);
    } catch (err) {
      const e2 = err as ApiError;
      if (e2.status === 400) setMsg(e2.detail || "Datos inválidos");
      else setMsg("No se pudo guardar goleadores");
    }
  }

  async function onDeletePartido(p: PartidoOut) {
    setMsg(null);
    if (!canDelete) return;
    if (!window.confirm("¿Eliminar este partido y sus goleadores?")) return;
    try {
      await api.del(`/partidos/${p.id_partido}`);
      setMsg("Partido eliminado");
      if (goleadoresPartidoId === p.id_partido) setGoleadoresPartidoId(null);
      await loadDetalle(p.id_fecha_partido);
    } catch (err) {
      const e2 = err as ApiError;
      if (e2.status === 403) setMsg("No tenés permisos");
      else setMsg("No se pudo eliminar");
    }
  }

  async function loadTorneo() {
    setLoadingTorneo(true);
    setMsg(null);
    try {
      const q = new URLSearchParams();
      if (torneoDesde.trim()) q.set("fecha_desde", torneoDesde.trim());
      if (torneoHasta.trim()) q.set("fecha_hasta", torneoHasta.trim());
      const qs = q.toString();
      const path = qs ? `/partidos/goleadores?${qs}` : "/partidos/goleadores";
      const rows = await api.get<GoleadorTorneoOut[]>(path);
      setTorneoRows(rows);
    } catch {
      setTorneoRows([]);
      setMsg("No se pudo cargar la tabla de goleadores");
    } finally {
      setLoadingTorneo(false);
    }
  }

  function addGoleadorRow() {
    setGoleadores((rows) => [...rows, { id_jugador: "", goles: "1" }]);
  }

  function removeGoleadorRow(i: number) {
    setGoleadores((rows) => rows.filter((_, idx) => idx !== i));
  }

  function setGoleadorRow(i: number, patch: Partial<GoleadorLineForm>) {
    setGoleadores((rows) => rows.map((r, idx) => (idx === i ? { ...r, ...patch } : r)));
  }

  return (
    <Layout>
      <div className="space-y-4">
        <div className="rounded-2xl border bg-white p-6 space-y-2">
          <h1 className="text-xl font-semibold">Partidos</h1>
          <p className="text-sm text-slate-600">
            Creá una fecha de encuentro (día, local/visitante, rival). Luego asociá un partido por categoría con hora, usá los contadores para el marcador y cargá goleadores por jugador.
          </p>
        </div>

        <div className="rounded-2xl border bg-white p-6 space-y-3">
          <h2 className="text-lg font-semibold">{editingFechaId ? "Editar fecha de encuentro" : "Nueva fecha de encuentro"}</h2>
          {msg && <div className="text-sm text-slate-700">{msg}</div>}
          <form onSubmit={onSubmitFecha} className="space-y-3 text-sm">
            <div className="grid md:grid-cols-4 gap-2">
              <input
                type="date"
                className="rounded-lg border px-3 py-2"
                value={fechaHeader.fecha_partido}
                onChange={(e) => setFechaHeader((h) => ({ ...h, fecha_partido: e.target.value }))}
                required
              />
              <select
                className="rounded-lg border px-3 py-2"
                value={fechaHeader.es_local}
                onChange={(e) => setFechaHeader((h) => ({ ...h, es_local: e.target.value }))}
              >
                <option value="true">Local</option>
                <option value="false">Visitante</option>
              </select>
              <input
                className="rounded-lg border px-3 py-2 md:col-span-2"
                placeholder="Rival"
                value={fechaHeader.rival}
                onChange={(e) => setFechaHeader((h) => ({ ...h, rival: e.target.value }))}
                required
              />
            </div>
            <div className="flex gap-2">
              <button type="submit" className="rounded-lg bg-slate-900 px-4 py-2 text-white">
                {editingFechaId ? "Guardar fecha" : "Crear fecha"}
              </button>
              {editingFechaId && (
                <button type="button" className="rounded-lg border px-4 py-2" onClick={resetFechaForm}>
                  Cancelar
                </button>
              )}
            </div>
          </form>
        </div>

        <div className="rounded-2xl border bg-white p-6 space-y-3">
          <h2 className="text-lg font-semibold">Fechas de encuentro</h2>
          {loadingFechas ? (
            <div className="text-sm text-slate-600">Cargando…</div>
          ) : fechas.length === 0 ? (
            <div className="text-sm text-slate-600">No hay fechas cargadas.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="text-xs uppercase text-slate-500">
                  <tr>
                    <th className="py-2 text-left">Fecha</th>
                    <th className="py-2 text-left">Condición</th>
                    <th className="py-2 text-left">Rival</th>
                    <th className="py-2 text-left">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {fechas.map((f) => (
                    <tr key={f.id_fecha_partido} className={["border-t", selectedFechaId === f.id_fecha_partido ? "bg-slate-50" : ""].join(" ")}>
                      <td className="py-2">{f.fecha_partido}</td>
                      <td className="py-2">{f.es_local ? "Local" : "Visitante"}</td>
                      <td className="py-2">{f.rival}</td>
                      <td className="py-2 space-x-2">
                        <button type="button" className="rounded border px-2 py-1" onClick={() => setSelectedFechaId(f.id_fecha_partido)}>
                          Seleccionar
                        </button>
                        <button type="button" className="rounded border px-2 py-1" onClick={() => startEditFecha(f)}>
                          Editar
                        </button>
                        {canDelete && (
                          <button type="button" className="rounded border px-2 py-1 text-red-700" onClick={() => onDeleteFecha(f)}>
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

        {selectedFechaId != null && (
          <div className="rounded-2xl border bg-white p-6 space-y-4">
            <h2 className="text-lg font-semibold">Partidos por categoría</h2>
            {detalle && (
              <p className="text-sm text-slate-600">
                {detalle.fecha_partido} · {detalle.es_local ? "Local" : "Visitante"} vs {detalle.rival}
              </p>
            )}
            <form onSubmit={onAddPartido} className="space-y-2 text-sm">
              <div className="font-medium text-slate-700">Agregar partido</div>
              <div className="flex flex-wrap gap-2 items-end">
                <select
                  className="rounded-lg border px-3 py-2 min-w-[180px]"
                  value={nuevoPartido.id_categoria}
                  onChange={(e) => setNuevoPartido((n) => ({ ...n, id_categoria: e.target.value }))}
                  required
                >
                  <option value="">Categoría</option>
                  {categorias.map((c) => (
                    <option key={c.id_categoria} value={String(c.id_categoria)}>
                      {c.descripcion}
                    </option>
                  ))}
                </select>
                <input
                  type="time"
                  className="rounded-lg border px-3 py-2"
                  value={nuevoPartido.hora_partido}
                  onChange={(e) => setNuevoPartido((n) => ({ ...n, hora_partido: e.target.value }))}
                />
                <button type="submit" className="rounded-lg bg-slate-900 px-4 py-2 text-white">
                  Agregar
                </button>
              </div>
            </form>

            {loadingDetalle ? (
              <div className="text-sm text-slate-600">Cargando partidos…</div>
            ) : detalle && detalle.partidos.length === 0 ? (
              <div className="text-sm text-slate-600">Todavía no hay partidos por categoría para esta fecha.</div>
            ) : (
              detalle && (
                <div className="space-y-4">
                  {detalle.partidos.map((p) => (
                    <div key={p.id_partido} className="border rounded-xl p-4 space-y-3">
                      <div className="flex flex-wrap justify-between gap-2 items-start">
                        <div>
                          <div className="font-medium">{p.categoria.descripcion}</div>
                          <div className="text-xs text-slate-500 mt-1 flex flex-wrap items-center gap-2">
                            <span>Hora</span>
                            <input
                              key={`${p.id_partido}-${p.hora_partido ?? ""}`}
                              type="time"
                              className="rounded border px-2 py-1 text-xs"
                              defaultValue={timeToInput(p.hora_partido)}
                              onBlur={(e) => {
                                const v = e.target.value;
                                if (v !== timeToInput(p.hora_partido)) onSaveHora(p, v);
                              }}
                            />
                          </div>
                        </div>
                        {canDelete && (
                          <button type="button" className="rounded border px-2 py-1 text-xs text-red-700" onClick={() => onDeletePartido(p)}>
                            Eliminar partido
                          </button>
                        )}
                      </div>
                      <div className="flex flex-wrap items-center gap-4">
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-slate-600">Nosotros</span>
                          <button type="button" className="rounded-lg border w-9 h-9 text-lg leading-none" onClick={() => patchMarcador(p, "goles_nuestro", -1)}>
                            −
                          </button>
                          <span className="font-semibold w-8 text-center">{p.goles_nuestro}</span>
                          <button type="button" className="rounded-lg border w-9 h-9 text-lg leading-none" onClick={() => patchMarcador(p, "goles_nuestro", 1)}>
                            +
                          </button>
                        </div>
                        <div className="text-slate-400">—</div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-slate-600">Rival</span>
                          <button type="button" className="rounded-lg border w-9 h-9 text-lg leading-none" onClick={() => patchMarcador(p, "goles_rival", -1)}>
                            −
                          </button>
                          <span className="font-semibold w-8 text-center">{p.goles_rival}</span>
                          <button type="button" className="rounded-lg border w-9 h-9 text-lg leading-none" onClick={() => patchMarcador(p, "goles_rival", 1)}>
                            +
                          </button>
                        </div>
                      </div>
                      <div>
                        <button
                          type="button"
                          className="rounded-lg border px-3 py-2 text-sm"
                          onClick={() => {
                            if (goleadoresPartidoId === p.id_partido) setGoleadoresPartidoId(null);
                            else openGoleadores(p);
                          }}
                        >
                          {goleadoresPartidoId === p.id_partido ? "Ocultar goleadores" : "Goleadores"}
                        </button>
                        {goleadoresPartidoId === p.id_partido && (
                          <div className="mt-3 space-y-2 border-t pt-3">
                            <div className="text-sm font-medium text-slate-700">Goleadores — {p.categoria.descripcion}</div>
                            <p className="text-xs text-slate-500">
                              Solo jugadores activos de esta categoría: elegí de la lista al abrir el campo o buscá por apellido o nombre.
                            </p>
                            {p.goles_nuestro === 0 && (
                              <p className="text-xs text-amber-700">Subí el contador de goles del equipo antes de asignar jugadores.</p>
                            )}
                            {goleadores.map((row, i) => (
                              <div key={`${p.id_partido}-g-${i}`} className="flex flex-wrap gap-2 items-center">
                                <JugadorCombobox
                                  className="flex-1 min-w-[200px]"
                                  value={row.id_jugador}
                                  onChange={(id) => setGoleadorRow(i, { id_jugador: id })}
                                  api={api}
                                  idCategoria={p.id_categoria}
                                  placeholder="Elegí o buscá jugador…"
                                  inputClassName="rounded-lg border px-3 py-2 text-sm w-full"
                                />
                                <input
                                  className="w-24 rounded-lg border px-3 py-2"
                                  type="number"
                                  min={1}
                                  value={row.goles}
                                  onChange={(e) => setGoleadorRow(i, { goles: e.target.value })}
                                />
                                {goleadores.length > 1 && (
                                  <button type="button" className="rounded border px-2 py-1 text-xs" onClick={() => removeGoleadorRow(i)}>
                                    Quitar
                                  </button>
                                )}
                              </div>
                            ))}
                            <button type="button" className="rounded-lg border px-3 py-2 text-sm" onClick={addGoleadorRow}>
                              Agregar goleador
                            </button>
                            <div>
                              <button type="button" className="rounded-lg bg-slate-900 px-4 py-2 text-sm text-white" onClick={onSaveGoleadores}>
                                Guardar goleadores
                              </button>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )
            )}
          </div>
        )}

        <div className="rounded-2xl border bg-white p-6 space-y-3">
          <h2 className="text-lg font-semibold">Goleadores del campeonato</h2>
          <p className="text-sm text-slate-600">Suma de goles asignados a jugadores en el rango de fechas de encuentro (opcional).</p>
          <div className="flex flex-wrap gap-2 items-end text-sm">
            <input type="date" className="rounded-lg border px-3 py-2" value={torneoDesde} onChange={(e) => setTorneoDesde(e.target.value)} />
            <input type="date" className="rounded-lg border px-3 py-2" value={torneoHasta} onChange={(e) => setTorneoHasta(e.target.value)} />
            <button type="button" className="rounded-lg bg-slate-900 px-4 py-2 text-white" onClick={loadTorneo}>
              Consultar
            </button>
          </div>
          {loadingTorneo ? (
            <div className="text-sm text-slate-600">Cargando…</div>
          ) : torneoRows.length === 0 ? (
            <div className="text-sm text-slate-600">Sin datos. Elegí fechas y pulsá Consultar, o verificá que haya goleadores cargados.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="text-xs uppercase text-slate-500">
                  <tr>
                    <th className="py-2 text-left">Jugador</th>
                    <th className="py-2 text-left">Goles</th>
                  </tr>
                </thead>
                <tbody>
                  {torneoRows.map((r) => (
                    <tr key={r.id_jugador} className="border-t">
                      <td className="py-2">
                        {r.apellido}, {r.nombre}
                      </td>
                      <td className="py-2">{r.goles_totales}</td>
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
