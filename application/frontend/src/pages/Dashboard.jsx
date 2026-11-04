import { useEffect, useState } from "react";
import { api } from "../utils/api.js";

export function Dashboard({ onNavigate }) {
  const [stats, setStats] = useState(null);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = () => {
    Promise.all([api.getStats(), api.getHealth()])
      .then(([s, h]) => { setStats(s); setHealth(h); })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
    const id = setInterval(load, 10000); // auto-refresh every 10s
    return () => clearInterval(id);
  }, []);

  return (
    <div>
      <div className="page-header">
        <div>
          <div className="page-title">Dashboard</div>
          <div className="page-subtitle">Overview of all background tasks</div>
        </div>
        <div style={{ display: "flex", gap: 10 }}>
          <button className="btn btn-ghost btn-sm" onClick={load}>↻ Refresh</button>
          <button className="btn btn-primary" onClick={() => onNavigate("create")}>＋ New Task</button>
        </div>
      </div>

      {loading ? (
        <div className="loading-center"><span className="spinner" /> Loading stats…</div>
      ) : (
        <>
          <div className="stats-grid">
            {[
              { key: "total", label: "Total Tasks", cls: "total" },
              { key: "pending", label: "Pending", cls: "pending" },
              { key: "processing", label: "Processing", cls: "processing" },
              { key: "completed", label: "Completed", cls: "completed" },
              { key: "failed", label: "Failed", cls: "failed" },
            ].map(({ key, label, cls }) => (
              <div key={key} className={`stat-card ${cls}`}>
                <div className="stat-label">{label}</div>
                <div className="stat-value">{stats?.[key] ?? 0}</div>
              </div>
            ))}
          </div>

          <div className="card">
            <div style={{ fontWeight: 600, marginBottom: 12 }}>System Status</div>
            <div style={{ display: "flex", gap: 24, flexWrap: "wrap" }}>
              <div>
                <span style={{ color: "var(--text-muted)", fontSize: 12 }}>API</span>{" "}
                <span style={{ color: health?.status === "healthy" ? "var(--success)" : "var(--danger)", fontWeight: 600 }}>
                  {health?.status ?? "unknown"}
                </span>
              </div>
              <div>
                <span style={{ color: "var(--text-muted)", fontSize: 12 }}>Database</span>{" "}
                <span style={{ color: health?.database === "connected" ? "var(--success)" : "var(--danger)", fontWeight: 600 }}>
                  {health?.database ?? "unknown"}
                </span>
              </div>
              <div>
                <span style={{ color: "var(--text-muted)", fontSize: 12 }}>Version</span>{" "}
                <span style={{ fontWeight: 600 }}>{health?.version ?? "—"}</span>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
