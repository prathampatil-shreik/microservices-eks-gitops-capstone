import { useEffect, useState } from "react";
import { api } from "../utils/api.js";
import { StatusBadge, PriorityLabel } from "./StatusBadge.jsx";

function fmt(dt) {
  if (!dt) return "—";
  return new Date(dt + "Z").toLocaleString();
}

export function TaskDetailModal({ taskId, onClose }) {
  const [task, setTask] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getTask(taskId)
      .then(setTask)
      .finally(() => setLoading(false));
  }, [taskId]);

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-header">
          <span className="modal-title">Task Details</span>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        {loading && <div className="loading-center"><span className="spinner" /> Loading…</div>}

        {task && (
          <>
            <div style={{ marginBottom: 20 }}>
              <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 8 }}>{task.title}</div>
              <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginBottom: 12 }}>
                <StatusBadge status={task.status} />
                <PriorityLabel priority={task.priority} />
                <span style={{ color: "var(--text-muted)", fontSize: 12 }}>
                  {task.task_type.replace(/_/g, " ")}
                </span>
              </div>
              {task.description && (
                <p style={{ color: "var(--text-muted)", fontSize: 13 }}>{task.description}</p>
              )}
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 20 }}>
              {[
                ["Created", fmt(task.created_at)],
                ["Updated", fmt(task.updated_at)],
                ["Started", fmt(task.started_at)],
                ["Completed", fmt(task.completed_at)],
              ].map(([label, value]) => (
                <div key={label}>
                  <div style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase" }}>{label}</div>
                  <div style={{ fontSize: 13 }}>{value}</div>
                </div>
              ))}
            </div>

            {task.history?.length > 0 && (
              <>
                <div style={{ fontWeight: 600, marginBottom: 12 }}>Processing History</div>
                <div className="timeline">
                  {task.history.map((h) => (
                    <div key={h.id} className="timeline-item">
                      <div className="timeline-dot">→</div>
                      <div className="timeline-content">
                        <div className="timeline-status">{h.current_status}</div>
                        {h.message && <div className="timeline-message">{h.message}</div>}
                        <div className="timeline-time">{fmt(h.created_at)}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}
