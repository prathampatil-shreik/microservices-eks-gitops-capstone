import { useState } from "react";
import { Sidebar } from "./components/Sidebar.jsx";
import { ToastContainer } from "./components/Toast.jsx";
import { Dashboard } from "./pages/Dashboard.jsx";
import { TaskList } from "./pages/TaskList.jsx";
import { CreateTask } from "./pages/CreateTask.jsx";
import { useToast } from "./hooks/useToast.js";

export default function App() {
  const [page, setPage] = useState("dashboard");
  const { toasts, addToast } = useToast();

  const pages = {
    dashboard: <Dashboard onNavigate={setPage} />,
    tasks: <TaskList onNavigate={setPage} toast={addToast} />,
    create: <CreateTask onNavigate={setPage} toast={addToast} />,
  };

  return (
    <div className="layout">
      <Sidebar page={page} onNavigate={setPage} />
      <main className="main-content">
        {pages[page] ?? pages.dashboard}
      </main>
      <ToastContainer toasts={toasts} />
    </div>
  );
}
