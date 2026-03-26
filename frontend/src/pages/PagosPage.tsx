import React, { useEffect, useState } from "react";
import { Layout } from "../components/Layout";
import { useApi } from "../lib/api";

export function PagosPage() {
  const api = useApi();
  const [items, setItems] = useState<any[]>([]);
  useEffect(() => { api.get<any[]>("/pagos").then(setItems).catch(() => setItems([])); }, [api]);
  return (
    <Layout>
      <div className="rounded-2xl border bg-white p-6">
        <h1 className="text-xl font-semibold">Pagos</h1>
        <ul className="mt-3 divide-y text-sm">
          {items.map(p => <li key={p.id_pago} className="py-2">{p.mes_correspondiente}/{p.anio_correspondiente} - ${p.monto}</li>)}
        </ul>
      </div>
    </Layout>
  );
}
