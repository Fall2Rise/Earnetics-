import { motion } from "framer-motion";

type Props = {
  title?: string;
  stats?: { label: string; value: string | number }[];
};

export function TopHudBar({ title = "EARNETICS COMMAND COCKPIT – ONLINE", stats = [] }: Props) {
  return (
    <motion.header
      className="w-full px-6 py-3 bg-[rgba(2,6,23,0.9)] border-b border-slate-800 shadow-[0_0_24px_rgba(34,211,238,0.25)] flex items-center justify-between"
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="flex items-center gap-3">
        <div className="h-10 w-10 rounded-full bg-gradient-to-br from-[#06b6d4] to-[#a855f7] shadow-[0_0_20px_rgba(34,211,238,0.5)]" />
        <div>
          <div className="text-sm text-white/60 uppercase tracking-wide">Earnetics</div>
          <div className="text-lg font-semibold text-white">{title}</div>
        </div>
      </div>
      <div className="flex items-center gap-4">
        {stats.map((s) => (
          <div
            key={s.label}
            className="px-3 py-2 rounded-full border border-cyan-400/60 bg-[rgba(2,6,23,0.6)] text-white text-sm shadow-[0_0_14px_rgba(34,211,238,0.35)]"
          >
            <div className="text-white/60 text-xs uppercase tracking-wide">{s.label}</div>
            <div className="text-cyan-300 font-semibold">{s.value}</div>
          </div>
        ))}
      </div>
    </motion.header>
  );
}
