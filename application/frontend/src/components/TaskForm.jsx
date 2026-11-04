import { useState } from "react";

const TASK_TYPES = [
  "DATA_PROCESSING",
  "REPORT_GENERATION",
  "EMAIL_NOTIFICATION",
  "FILE_EXPORT",
  "CLEANUP",
];

const PRIORITIES = ["LOW", "MEDIUM", "HIGH"];

const EMPTY = { title: "", description: "", task_type: "DATA_PROCESSING", priority: "MEDIUM" };

export function TaskForm({ initial = EMPTY, onSubmit, onCancel, loading }) {
  const [form, setForm] = useState(initial);

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(form);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-group">
        <label className="form-label">Title *</label>
        <input
          className="form-input"
          value={form.title}
          onChange={set("title")}
          placeholder="Enter task title"
          required
          maxLength={255}
        />
      </div>

      <div className="form-group">
        <label className="form-label">Description</label>
        <textarea
          className="form-textarea"
          value={form.description}
          onChange={set("description")}
          placeholder="Optional description"
          maxLength={2000}
        />
      </div>

      <div className="form-group">
        <label className="form-label">Task Type</label>
        <select className="form-select" value={form.task_type} onChange={set("task_type")}>
          {TASK_TYPES.map((t) => (
            <option key={t} value={t}>{t.replace(/_/g, " ")}</option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label className="form-label">Priority</label>
        <select className="form-select" value={form.priority} onChange={set("priority")}>
          {PRIORITIES.map((p) => (
            <option key={p} value={p}>{p}</option>
          ))}
        </select>
      </div>

      <div style={{ display: "flex", gap: "10px", justifyContent: "flex-end", marginTop: "8px" }}>
        {onCancel && (
          <button type="button" className="btn btn-ghost" onClick={onCancel}>
            Cancel
          </button>
        )}
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? <span className="spinner" /> : null}
          {loading ? "Saving…" : "Save Task"}
        </button>
      </div>
    </form>
  );
}
