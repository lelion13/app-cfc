import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../state/auth";

export function ProtectedRoute({
  children,
  allowRoles
}: {
  children: React.ReactNode;
  allowRoles?: Array<"Admin" | "Coordinador">;
}) {
  const { token, user, isLoading } = useAuth();
  if (isLoading) return <div className="min-h-screen grid place-items-center text-sm text-slate-600">Cargando…</div>;
  if (!token) return <Navigate to="/login" replace />;
  if (allowRoles && user && !allowRoles.includes(user.rol)) return <Navigate to="/dashboard" replace />;
  return <>{children}</>;
}
