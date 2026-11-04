/**
 * API client — all HTTP calls to the backend go through here.
 * VITE_API_URL is set at build time; defaults to empty string so
 * Vite's dev proxy handles routing during local development.
 */
const BASE = import.meta.env.VITE_API_URL || "";

async function request(method, path, body) {
  const opts = {
    method,
    headers: { "Content-Type": "application/json" },
  };
  if (body !== undefined) opts.body = JSON.stringify(body);

  const res = await fetch(`${BASE}${path}`, opts);

  if (res.status === 204) return null; // DELETE returns no body

  const data = await res.json();
  if (!res.ok) {
    const msg = data?.detail || `HTTP ${res.status}`;
    throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
  }
  return data;
}

export const api = {
  // Tasks
  getTasks: (params = {}) => {
    const qs = new URLSearchParams(
      Object.fromEntries(Object.entries(params).filter(([, v]) => v != null && v !== ""))
    ).toString();
    return request("GET", `/api/v1/tasks${qs ? `?${qs}` : ""}`);
  },
  getTask: (id) => request("GET", `/api/v1/tasks/${id}`),
  createTask: (body) => request("POST", "/api/v1/tasks", body),
  updateTask: (id, body) => request("PUT", `/api/v1/tasks/${id}`, body),
  deleteTask: (id) => request("DELETE", `/api/v1/tasks/${id}`),
  getTaskHistory: (id) => request("GET", `/api/v1/tasks/${id}/history`),
  getStats: () => request("GET", "/api/v1/stats"),
  getHealth: () => request("GET", "/health"),
};
