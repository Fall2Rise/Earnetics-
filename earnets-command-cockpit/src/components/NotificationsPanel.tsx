import { motion, AnimatePresence } from "framer-motion";

type Notification = {
  id: string | number;
  message: string;
  timestamp?: string;
};

export function NotificationsPanel({ notifications = [] }: { notifications?: Notification[] }) {
  return (
    <div className="space-y-2">
      <AnimatePresence>
        {notifications.map((n) => (
          <motion.div
            key={n.id}
            initial={{ x: 40, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 40, opacity: 0 }}
            className="p-2 rounded-lg border border-white/10 bg-white/5 text-white"
          >
            <div className="text-xs text-white/60">{n.timestamp || ""}</div>
            <div className="text-sm">{n.message}</div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
