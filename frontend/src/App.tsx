import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { ArancelesPage } from "./pages/ArancelesPage";
import { CategoriasPage } from "./pages/CategoriasPage";
import { DashboardPage } from "./pages/DashboardPage";
import { IngresosPage } from "./pages/IngresosPage";
import { JugadorDetailPage } from "./pages/JugadorDetailPage";
import { JugadorFormPage } from "./pages/JugadorFormPage";
import { JugadoresPage } from "./pages/JugadoresPage";
import { LoginPage } from "./pages/LoginPage";
import { PagosPage } from "./pages/PagosPage";
import { SetupPage } from "./pages/SetupPage";
import { UsuariosPage } from "./pages/UsuariosPage";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/setup" element={<SetupPage />} />
      <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
      <Route path="/jugadores" element={<ProtectedRoute><JugadoresPage /></ProtectedRoute>} />
      <Route path="/jugadores/nuevo" element={<ProtectedRoute><JugadorFormPage /></ProtectedRoute>} />
      <Route path="/jugadores/:id/editar" element={<ProtectedRoute><JugadorFormPage /></ProtectedRoute>} />
      <Route path="/jugadores/:id" element={<ProtectedRoute><JugadorDetailPage /></ProtectedRoute>} />
      <Route path="/pagos" element={<ProtectedRoute><PagosPage /></ProtectedRoute>} />
      <Route path="/ingresos" element={<ProtectedRoute allowRoles={["Admin", "Coordinador"]}><IngresosPage /></ProtectedRoute>} />
      <Route path="/aranceles" element={<ProtectedRoute allowRoles={["Admin", "Coordinador"]}><ArancelesPage /></ProtectedRoute>} />
      <Route path="/categorias" element={<ProtectedRoute allowRoles={["Admin", "Coordinador"]}><CategoriasPage /></ProtectedRoute>} />
      <Route path="/usuarios" element={<ProtectedRoute allowRoles={["Admin"]}><UsuariosPage /></ProtectedRoute>} />
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
