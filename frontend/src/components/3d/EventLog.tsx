import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, Filter } from 'lucide-react';
import { useAgentStore } from '../../stores/agentStore';
import { DetailModal } from '../dashboard/DetailModal';

interface Event {
  id: string;
  timestamp: string;
  agent: string;
  message: string;
  type: string;
  raw?: Record<string, unknown>;
}

export const EventLog: React.FC = () => {
  const [events, setEvents] = useState<Event[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filter, setFilter] = useState<string>('all');
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const socket = useAgentStore((state) => state.socket);

  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data);
        if (!data || !data.type) return;
        const now = new Date().toISOString();
        const nextEvent: Event = {
          id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
          timestamp: data.timestamp || now,
          agent: data.agent || data.owner || 'System',
          message: data.message || data.summary || data.type,
          type: data.status === 'error' || String(data.type).includes('error') ? 'error' : data.type.includes('action') ? 'action' : 'directive',
          raw: data,
        };
        setEvents((prev) => [nextEvent, ...prev].slice(0, 50));
      } catch (err) {
        // Ignore parse errors
      }
    };

    socket.addEventListener('message', handleMessage);
    return () => socket.removeEventListener('message', handleMessage);
  }, [socket]);

  const filteredEvents = events.filter((event) => {
    const matchesSearch = event.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
      event.agent.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filter === 'all' || event.type === filter;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="absolute bottom-6 left-6 z-40 w-[420px]">
      <div className="bg-slate-950/90 backdrop-blur border border-cyan-500/20 rounded-xl shadow-[0_0_40px_rgba(0,214,255,0.18)] p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-bold text-cyan-300 uppercase tracking-widest">Event Log</h3>
          <div className="flex items-center gap-2">
            <div className="relative">
              <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 text-slate-400" size={14} />
              <input
                type="text"
                placeholder="Search..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-7 pr-3 py-1.5 bg-slate-900 border border-slate-700/70 rounded text-white text-xs"
              />
            </div>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="px-3 py-1.5 bg-slate-900 border border-slate-700/70 rounded text-white text-xs"
            >
              <option value="all">All</option>
              <option value="directive">Directives</option>
              <option value="action">Actions</option>
              <option value="error">Errors</option>
            </select>
          </div>
        </div>

        <div className="max-h-44 overflow-y-auto space-y-2 pr-1">
          {filteredEvents.length === 0 && (
            <div className="text-xs text-slate-400">No events yet.</div>
          )}
          {filteredEvents.map((event) => (
            <motion.div
              key={event.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-start gap-3 p-2 bg-slate-900/60 rounded border border-slate-700/60 text-xs cursor-pointer hover:border-cyan-500/40"
              onClick={() => setSelectedEvent(event)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  setSelectedEvent(event);
                }
              }}
            >
              <span className="text-slate-400 font-mono">
                {new Date(event.timestamp).toLocaleTimeString()}
              </span>
              <span className="text-cyan-300 font-semibold">{event.agent}</span>
              <span className="text-slate-300 flex-1">{event.message}</span>
            </motion.div>
          ))}
        </div>
      </div>
      <DetailModal
        isOpen={Boolean(selectedEvent)}
        onClose={() => setSelectedEvent(null)}
        title="Event Detail"
        subtitle={selectedEvent?.message ?? 'Event log entry'}
      >
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-xs text-slate-200">
            <div>
              <span className="text-slate-400">Agent</span>
              <div className="text-white">{selectedEvent?.agent ?? 'System'}</div>
            </div>
            <div>
              <span className="text-slate-400">Type</span>
              <div className="text-white">{selectedEvent?.type ?? 'N/A'}</div>
            </div>
            <div>
              <span className="text-slate-400">Timestamp</span>
              <div className="text-white">
                {selectedEvent?.timestamp ? new Date(selectedEvent.timestamp).toLocaleString() : 'N/A'}
              </div>
            </div>
          </div>
          <div>
            <h4 className="text-sm text-cyan-300 font-semibold mb-2">Raw payload</h4>
            <pre className="text-xs bg-black/40 border border-cyan-500/20 rounded-lg p-4 overflow-x-auto text-cyan-100">
              {JSON.stringify(selectedEvent?.raw ?? {}, null, 2)}
            </pre>
          </div>
        </div>
      </DetailModal>
    </div>
  );
};
