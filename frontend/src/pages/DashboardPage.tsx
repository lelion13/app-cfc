import { Layout } from "../components/Layout";

export function DashboardPage() {
  return (
    <Layout>
      <div className="rounded-2xl border bg-white p-6">
        <h1 className="text-xl font-semibold">Dashboard</h1>
        <p className="mt-2 text-sm text-slate-600">Bienvenido al sistema del club.</p>
      </div>
    </Layout>
  );
}
