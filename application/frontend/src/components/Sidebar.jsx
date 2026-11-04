const NAV = [
  { id: "dashboard", label: "Dashboard", icon: "⊞" },
  { id: "tasks", label: "All Tasks", icon: "☰" },
  { id: "create", label: "New Task", icon: "＋" },
];

export function Sidebar({ page, onNavigate }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <svg width="28" height="28" viewBox="0 0 32 32" fill="none">
          <rect width="32" height="32" rx="8" fill="#6366f1" />
          <path d="M8 16l6 6 10-12" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        <span>MicroTask</span>
      </div>
      <nav className="sidebar-nav">
        {NAV.map((item) => (
          <button
            key={item.id}
            className={`nav-item ${page === item.id ? "active" : ""}`}
            onClick={() => onNavigate(item.id)}
          >
            <span>{item.icon}</span>
            {item.label}
          </button>
        ))}
      </nav>
    </aside>
  );
}
