export function StatusBadge({ status }) {
  return (
    <span className={`badge badge-${status}`}>
      <span className="badge-dot" />
      {status}
    </span>
  );
}

export function PriorityLabel({ priority }) {
  return <span className={`priority-${priority}`}>{priority}</span>;
}
