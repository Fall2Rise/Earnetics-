import { motion } from "framer-motion";

type Kpi = {
  label: string;
  value: string | number;
  accent?: string;
};

export function KpiTilesRow({ kpis }: { kpis: Kpi[] }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {kpis.map((kpi) => (
        <motion.div
          key={kpi.label}
          className="p-4 rounded-[16px] border border-slate-700 bg-[rgba(2,6,23,0.85)] text-white shadow-[0_0_24px_rgba(15,23,42,0.9)] panel-hover"
          whileHover={{ y: -2, scale: 1.01 }}
        >
          <div className="hud-label">{kpi.label}</div>
          <div className="text-2xl font-semibold text-cyan-300">{kpi.value}</div>
          {kpi.accent && <div className="text-emerald-400 text-xs">{kpi.accent}</div>}
        </motion.div>
      ))}
    </div>
  );
}
