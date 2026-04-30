export function getApiBase() {
  return (import.meta.env.VITE_API_BASE_URL as string) || "/api/v1";
}
