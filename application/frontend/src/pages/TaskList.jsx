import { useEffect, useState, useCallback } from "react";
import { api } from "../utils/api.js";
import { StatusBadge, PriorityLabel } from "../components/StatusBadge.jsx";
import { TaskDetailModal } from "../components/TaskDetailModal.jsx";

const STATUSES = ["", "PENDING", "PROCESSING", "COMPLETED", "FAILED"];

function fmt(dt) {
  if (!dt) return "—";
  return new Date(dt + "Z").toLocaleString();
}

export function TaskList({ onNavigate, toast }) {
  const [data, setData] = useState({ items: [], total: 0, page: 1, total_pages: 1 });
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);
  const [detailId, setDetailId] = useState(null);
  const [deleting, setDeleting] = useState(null);

  const load = useCallback(() => {
    setLoading(true);
    api.getTasks({ status: statusFilter || undefined, search: search || undefined, page })
      .then(setData)
      .catch((e) => toast(e.message, "error"))
      .finally(() => setLoading(false));
  }, [statusFilter, search, page]);

  useEffect(() => { load(); }, [load]);

  // Auto-refresh every 5s so status changes appear without manual refresh
  useEffect(() => {
    const id = setInterval(load, 5000);
    return () => clearInterval(id);
  }, [load]);

  const handleDelete = async (id) => {
    if (!confirm("Delete this task?")) return;
    setDeleting(id);
    try {
      await api.deleteTask(id);
      toast("Task deleted", "success");
      load();
    } catch (e) {
      toast(e.message, "error");
    } finally {
      setDeleting(null);
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <div className="page-title">All Tasks</div>
          <div className="page-subtitle">{data.total} task{data.total !== 1 ? "s" : ""} total</div>
        </div>
        <button className="btn btn-primary" onClick={() => onNavigate("create")}>＋ New Task</button>
      </div>

      <div className="toolbar">
        <input
          className="search-input"
          placeholder="Search tasks…"
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
        />
        <select
          className="form-select"
          style={{ width: "auto" }}
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
        >
          {STATUSES.map((s) => (
            <option key={s} value={s}>{s || "All Statuses"}</option>
          ))}
        </select>
        <button className="btn btn-ghost btn-sm" onClick={load}>↻ Refresh</button>
      </div>

      <div className="card" style={{ padding: 0 }}>
        <div className="table-wrap">
          {loading ? (
            <div className="loading-center"><span className="spinner" /> Loading…</div>
          ) : data.items.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">📋</div>
              <div className="empty-state-title">No tasks found</div>
              <p>Create your first task to get started.</p>
            </div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Title</th>
                  <th>Type</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((task) => (
                  <tr key={task.id}>
                    <td style={{ color: "var(--text-muted)" }}>#{task.id}</td>
                    <td>
                      <button
                        style={{ background: "none", border: "none", color: "var(--text)", fontWeight: 500, cursor: "pointer", textAlign: "left" }}
                        onClick={() => setDetailId(task.id)}
                      >
                        {task.title}
                      </button>
                    </td>
                    <td style={{ color: "var(--text-muted)", fontSize: 12 }}>{task.task_type.replace(/_/g, " ")}</td>
                    <td><PriorityLabel priority={task.priority} /></td>
                    <td><StatusBadge status={task.status} /></td>
                    <td style={{ color: "var(--text-muted)", fontSize: 12 }}>{fmt(task.created_at)}</td>
                    <td>
                      <div style={{ display: "flex", gap: 6 }}>
                        <button className="btn btn-ghost btn-sm" onClick={() => setDetailId(task.id)}>View</button>
                        <button
                          className="btn btn-danger btn-sm"
                          onClick={() => handleDelete(task.id)}
                          disabled={deleting === task.id}
                        >
                          {deleting === task.id ? <span className="spinner" style={{ width: 12, height: 12 }} /> : "Delete"}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {data.total_pages > 1 && (
        <div className="pagination">
          <button className="btn btn-ghost btn-sm" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>← Prev</button>
          <span className="page-info">Page {page} of {data.total_pages}</span>
          <button className="btn btn-ghost btn-sm" disabled={page >= data.total_pages} onClick={() => setPage(p => p + 1)}>Next →</button>
        </div>
      )}

      {detailId && <TaskDetailModal taskId={detailId} onClose={() => setDetailId(null)} />}
    </div>
  );
}
