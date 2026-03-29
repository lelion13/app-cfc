import React, { useEffect, useId, useRef, useState } from "react";
import { useApi } from "../lib/api";

export type JugadorMini = { id_jugador: number; nombre: string; apellido: string; id_categoria: number };

type PageJugadores = { items: JugadorMini[] };

function labelOf(j: JugadorMini) {
  return `${j.apellido}, ${j.nombre}`;
}

type Props = {
  value: string;
  onChange: (id: string) => void;
  api: ReturnType<typeof useApi>;
  /** Si se define, todas las búsquedas y el listado inicial quedan acotados a esa categoría. */
  idCategoria?: number;
  placeholder?: string;
  className?: string;
  required?: boolean;
  inputClassName?: string;
};

export function JugadorCombobox({
  value,
  onChange,
  api,
  idCategoria,
  placeholder = "Buscar por nombre o apellido…",
  className = "",
  required = false,
  inputClassName = "rounded-lg border px-3 py-2 text-sm w-full",
}: Props) {
  const listId = useId();
  const wrapRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<JugadorMini[]>([]);
  const [resolvedLabel, setResolvedLabel] = useState<string | null>(null);

  useEffect(() => {
    if (!value) {
      setResolvedLabel(null);
      return;
    }
    let cancelled = false;
    api
      .get<JugadorMini>(`/jugadores/${value}`)
      .then((j) => {
        if (!cancelled) setResolvedLabel(labelOf(j));
      })
      .catch(() => {
        if (!cancelled) setResolvedLabel(`#${value}`);
      });
    return () => {
      cancelled = true;
    };
  }, [value, api]);

  useEffect(() => {
    const q = query.trim();
    if (q.length >= 1) {
      return;
    }
    if (idCategoria == null || !open) {
      if (idCategoria == null) {
        setResults([]);
        setLoading(false);
      }
      return;
    }
    let cancelled = false;
    setLoading(true);
    const p = new URLSearchParams({
      page: "1",
      page_size: "100",
      activo: "true",
      id_categoria: String(idCategoria),
    });
    api
      .get<PageJugadores>(`/jugadores?${p.toString()}`)
      .then((res) => {
        if (!cancelled) setResults(res.items ?? []);
      })
      .catch(() => {
        if (!cancelled) setResults([]);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [open, idCategoria, query, api]);

  useEffect(() => {
    const q = query.trim();
    if (q.length < 1) {
      return;
    }
    const t = window.setTimeout(() => {
      setLoading(true);
      const p = new URLSearchParams({ q, page: "1", page_size: "50", activo: "true" });
      if (idCategoria != null) p.set("id_categoria", String(idCategoria));
      api
        .get<PageJugadores>(`/jugadores?${p.toString()}`)
        .then((res) => setResults(res.items ?? []))
        .catch(() => setResults([]))
        .finally(() => setLoading(false));
    }, 280);
    return () => window.clearTimeout(t);
  }, [query, api, idCategoria]);

  useEffect(() => {
    function onDocDown(e: MouseEvent) {
      if (wrapRef.current && !wrapRef.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onDocDown);
    return () => document.removeEventListener("mousedown", onDocDown);
  }, []);

  const displayValue = value && resolvedLabel && query === "" ? resolvedLabel : query;

  function pick(j: JugadorMini) {
    onChange(String(j.id_jugador));
    setResolvedLabel(labelOf(j));
    setQuery("");
    setOpen(false);
    setResults([]);
  }

  function clearSelection() {
    onChange("");
    setResolvedLabel(null);
    setQuery("");
    setResults([]);
    inputRef.current?.focus();
  }

  const scopedToCategory = idCategoria != null;
  const qEmpty = query.trim().length < 1;

  return (
    <div ref={wrapRef} className={["relative", className].join(" ")}>
      <div className="flex gap-1">
        <input
          ref={inputRef}
          type="text"
          role="combobox"
          aria-expanded={open}
          aria-controls={listId}
          aria-autocomplete="list"
          className={inputClassName}
          placeholder={placeholder}
          autoComplete="off"
          value={displayValue}
          aria-required={required}
          onChange={(e) => {
            const v = e.target.value;
            if (value) onChange("");
            setResolvedLabel(null);
            setQuery(v);
            setOpen(true);
          }}
          onFocus={() => {
            setOpen(true);
            if (value && resolvedLabel) {
              requestAnimationFrame(() => inputRef.current?.select());
            }
          }}
          onKeyDown={(e) => {
            if (e.key === "Escape") {
              setOpen(false);
            }
          }}
        />
        {value ? (
          <button type="button" className="shrink-0 rounded-lg border px-2 py-2 text-xs text-slate-600" onClick={clearSelection} title="Quitar jugador">
            ×
          </button>
        ) : null}
      </div>
      {open && (
        <ul
          id={listId}
          role="listbox"
          className="absolute z-30 mt-1 max-h-56 w-full overflow-auto rounded-lg border bg-white py-1 shadow-md text-sm"
        >
          {qEmpty && !scopedToCategory && <li className="px-3 py-2 text-slate-500">Escribí para buscar jugadores activos.</li>}
          {qEmpty && scopedToCategory && loading && <li className="px-3 py-2 text-slate-500">Cargando jugadores de la categoría…</li>}
          {qEmpty && scopedToCategory && !loading && results.length === 0 && (
            <li className="px-3 py-2 text-slate-500">No hay jugadores activos en esta categoría.</li>
          )}
          {!qEmpty && loading && <li className="px-3 py-2 text-slate-500">Buscando…</li>}
          {!qEmpty && !loading && results.length === 0 && <li className="px-3 py-2 text-slate-500">Sin resultados.</li>}
          {results.map((j) => (
            <li key={j.id_jugador}>
              <button
                type="button"
                role="option"
                className="w-full text-left px-3 py-2 hover:bg-slate-100"
                onMouseDown={(e) => e.preventDefault()}
                onClick={() => pick(j)}
              >
                {labelOf(j)}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
