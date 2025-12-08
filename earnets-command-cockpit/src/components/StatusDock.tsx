type Notification = {
  id: string | number;
  message: string;
  timestamp?: string;
};

type Props = {
  notifications?: Notification[];
};

export function StatusDock({ notifications = [] }: Props) {
  return (
    <aside className="w-64 bg-[rgba(2,6,23,0.85)] border-l border-slate-800 text-white flex flex-col shadow-[0_0_20px_rgba(34,211,238,0.2)]">
      <div className="p-3 border-b border-slate-800 text-sm uppercase tracking-[0.25em] text-slate-400">
        Status Dock
      </div>
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {notifications.length === 0 && <div className="text-white/50 text-sm">No notifications.</div>}
        {notifications.map((n) => (
          <div
            key={n.id}
            className="p-2 rounded-lg border border-slate-700 bg-[rgba(2,6,23,0.75)] panel-hover"
          >
            <div className="text-xs text-cyan-300">{n.timestamp || ""}</div>
            <div className="text-sm text-slate-200">{n.message}</div>
          </div>
        ))}
      </div>
    </aside>
  );
}
