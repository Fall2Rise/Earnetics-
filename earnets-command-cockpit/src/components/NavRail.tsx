import { motion } from "framer-motion";

type NavItem = {
  key: string;
  label: string;
  icon?: string;
};

type Props = {
  active: string;
  onSelect: (key: string) => void;
};

const items: NavItem[] = [
  { key: "dashboard", label: "Dashboard", icon: "🏠" },
  { key: "streams", label: "Streams", icon: "🌊" },
  { key: "crm", label: "CRM", icon: "📇" },
  { key: "agents", label: "Agents", icon: "🤖" },
  { key: "library", label: "Library", icon: "📚" },
  { key: "settings", label: "Settings", icon: "⚙️" },
];

export function NavRail({ active, onSelect }: Props) {
  return (
    <nav className="w-24 bg-gradient-to-b from-[#020617] to-[#050814] border-r border-slate-800 flex flex-col items-center py-4 gap-3 shadow-[0_0_20px_rgba(34,211,238,0.25)]">
      {items.map((item) => {
        const isActive = active === item.key;
        return (
          <motion.button
            key={item.key}
            onClick={() => onSelect(item.key)}
            className={`w-16 h-16 rounded-2xl border ${
              isActive
                ? "border-cyan-500 text-cyan-200 shadow-[0_0_18px_rgba(6,182,212,0.45)]"
                : "border-slate-700 text-slate-300"
            } bg-[rgba(2,6,23,0.8)] flex flex-col items-center justify-center gap-1 hover:border-violet-400 hover:shadow-[0_0_18px_rgba(168,85,247,0.35)] transition`}
            whileHover={{ y: -2, scale: 1.02 }}
          >
            <span className="text-lg">{item.icon}</span>
            <span className="text-[11px] uppercase tracking-wide text-slate-200">{item.label}</span>
          </motion.button>
        );
      })}
    </nav>
  );
}
