export function InternalLibraryPanel() {
  const items = [
    { id: 1, title: "TikTok Affiliate Loop", category: "playbook" },
    { id: 2, title: "Email Funnel – Automation Clients", category: "playbook" },
  ];
  return (
    <div className="text-white space-y-3">
      <div>
        <div className="hud-label">Internal Library</div>
        <h2 className="text-xl font-semibold text-slate-50">Playbooks & Guides</h2>
      </div>
      <div className="grid md:grid-cols-2 gap-3">
        {items.map((i) => (
          <div
            key={i.id}
            className="p-3 rounded-[16px] border border-slate-700 bg-[rgba(2,6,23,0.85)] shadow-[0_0_24px_rgba(15,23,42,0.9)] panel-hover"
          >
            <div className="text-sm uppercase text-slate-400">{i.category}</div>
            <div className="font-semibold text-cyan-200">{i.title}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
