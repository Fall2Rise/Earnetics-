import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Stream } from "../types/streams";
import { getStreams, advanceStream, createStream } from "../api/streamsClient";

export function RevenueStreamsPanel() {
  const [streams, setStreams] = useState<Stream[]>([]);
  const load = async () => {
    try {
      setStreams(await getStreams());
    } catch (err) {
      console.warn("streams load", err);
    }
  };
  useEffect(() => {
    load();
  }, []);

  const onAdvance = async (id: number) => {
    await advanceStream(id);
    load();
  };

  const onNew = async () => {
    const name = prompt("Stream name?");
    if (!name) return;
    await createStream(name);
    load();
  };

  return (
    <div className="text-white">
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="hud-label">Revenue Streams</div>
          <h2 className="text-xl font-semibold text-slate-50">Pipelines & KPIs</h2>
          <p className="text-slate-300 text-sm">Cockpit console for stream control.</p>
        </div>
        <div className="flex gap-2">
          <button onClick={onNew} className="btn-primary">
            New Stream
          </button>
        </div>
      </div>
      <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
        {streams.map((s) => (
          <motion.div
            key={s.id}
            className="p-4 rounded-[16px] border border-slate-700 bg-[rgba(2,6,23,0.85)] shadow-[0_0_24px_rgba(15,23,42,0.9)] panel-hover"
            whileHover={{ y: -2, scale: 1.01 }}
          >
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm uppercase text-slate-400">Stream</div>
                <div className="text-lg font-semibold text-slate-50">{s.name}</div>
              </div>
              <div className="px-3 py-1 rounded-full text-xs border border-cyan-500 text-cyan-300">
                {s.stage || "unknown"}
              </div>
            </div>
            <div className="mt-3">
              <div className="h-2 rounded-full bg-slate-800 overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-cyan-400 via-emerald-400 to-violet-400"
                  style={{ width: `${s.progress || 0}%` }}
                />
              </div>
            </div>
            <div className="mt-3 flex gap-2">
              <button onClick={() => onAdvance(s.id)} className="btn-secondary">
                Advance
              </button>
              <button onClick={() => alert(JSON.stringify(s, null, 2))} className="btn-secondary">
                View
              </button>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
