import { useState } from "react";
import { api } from "../utils/api.js";
import { TaskForm } from "../components/TaskForm.jsx";

export function CreateTask({ onNavigate, toast }) {
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (form) => {
    setLoading(true);
    try {
      const task = await api.createTask(form);
      toast(`Task #${task.id} created successfully!`, "success");
      onNavigate("tasks");
    } catch (e) {
      toast(e.message, "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <div className="page-title">New Task</div>
          <div className="page-subtitle">Create a background processing task</div>
        </div>
      </div>

      <div className="card" style={{ maxWidth: 560 }}>
        <TaskForm
          onSubmit={handleSubmit}
          onCancel={() => onNavigate("tasks")}
          loading={loading}
        />
      </div>
    </div>
  );
}
