import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Contact, Deal, Task } from "../types/crm";
import { getContacts, getDeals, getTasks } from "../api/crmClient";

export function CrmPanel() {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [deals, setDeals] = useState<Deal[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [selected, setSelected] = useState<Contact | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        setContacts(await getContacts());
        setDeals(await getDeals());
        setTasks(await getTasks());
      } catch (err) {
        console.warn("CRM load error", err);
      }
    };
    load();
  }, []);

  const contactDeals = selected ? deals.filter((d) => d.contact_id === selected.id) : [];
  const contactTasks = selected ? tasks.filter((t) => t.contact_id === selected.id) : [];

  return (
    <div className="grid grid-cols-3 gap-4 text-white">
      <div className="col-span-1 rounded-[16px] border border-slate-700 bg-[rgba(2,6,23,0.85)] p-3 overflow-y-auto max-h-[70vh] shadow-[0_0_24px_rgba(15,23,42,0.9)] panel-hover">
        <div className="hud-label mb-2">Contacts</div>
        {contacts.map((c) => (
          <motion.div
            key={c.id}
            className={`p-3 rounded-lg mb-2 border ${
              selected?.id === c.id
                ? "border-cyan-500 bg-[rgba(34,211,238,0.08)] shadow-[0_0_18px_rgba(34,211,238,0.35)]"
                : "border-slate-700 bg-[rgba(2,6,23,0.6)]"
            } panel-hover`}
            onClick={() => setSelected(c)}
            whileHover={{ y: -1 }}
          >
            <div className="font-semibold">{c.name}</div>
            <div className="text-xs text-white/60">{c.email || c.phone || "No contact info"}</div>
            <div className="text-xs text-neon-blue">{c.type || "contact"}</div>
          </motion.div>
        ))}
      </div>
      <div className="col-span-2 rounded-[16px] border border-slate-700 bg-[rgba(2,6,23,0.85)] p-4 shadow-[0_0_24px_rgba(15,23,42,0.9)] panel-hover">
        {selected ? (
          <div>
            <div className="flex items-center justify-between mb-2">
              <div>
                <div className="hud-label">Contact</div>
                <div className="text-xl font-semibold text-slate-50">{selected.name}</div>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <div className="hud-label">Deals</div>
                {contactDeals.length === 0 && <div className="text-white/50 text-sm">No deals.</div>}
                {contactDeals.map((d) => (
                  <div key={d.id} className="p-2 mt-1 rounded border border-slate-700 bg-[rgba(2,6,23,0.6)] panel-hover">
                    <div className="font-semibold text-slate-50">{d.title}</div>
                    <div className="text-xs text-slate-400">
                      {d.pipeline} • {d.stage}
                    </div>
                  </div>
                ))}
              </div>
              <div>
                <div className="hud-label">Tasks</div>
                {contactTasks.length === 0 && <div className="text-white/50 text-sm">No tasks.</div>}
                {contactTasks.map((t) => (
                  <div key={t.id} className="p-2 mt-1 rounded border border-slate-700 bg-[rgba(2,6,23,0.6)] panel-hover">
                    <div className="font-semibold text-slate-50">{t.title}</div>
                    <div className="text-xs text-slate-400">{t.status}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="text-white/60">Select a contact to view details.</div>
        )}
      </div>
    </div>
  );
}
