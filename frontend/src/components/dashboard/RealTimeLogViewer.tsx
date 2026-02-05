import React, { useEffect, useRef, useState, useCallback } from 'react';
import { X, Maximize2, Minimize2, Trash2, Filter } from 'lucide-react';
import { useAgentStore } from '../../stores/agentStore';

interface LogEntry {
  id: string;
  timestamp: string;
  level: 'info' | 'warning' | 'error' | 'success';
  agent?: string;
  department?: string;
  message: string;
  details?: any;
}

const formatTimestamp = (timestamp: string): string => {
  try {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour12: false, 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit',
      fractionalSecondDigits: 3
    });
  } catch {
    return timestamp;
  }
};

const getLogColor = (level: LogEntry['level']): string => {
  switch (level) {
    case 'error': return 'text-red-400 border-red-500/30 bg-red-500/5';
    case 'warning': return 'text-yellow-400 border-yellow-500/30 bg-yellow-500/5';
    case 'success': return 'text-green-400 border-green-500/30 bg-green-500/5';
    default: return 'text-cyan-400 border-cyan-500/30 bg-cyan-500/5';
  }
};

export const RealTimeLogViewer: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [filter, setFilter] = useState<string>('all'); // 'all', 'error', 'warning', 'info', 'success'
  const [maxLogs, setMaxLogs] = useState(500);
  const scrollRef = useRef<HTMLDivElement>(null);
  const { socket } = useAgentStore();

  const addLog = useCallback((entry: LogEntry) => {
    setLogs((prev) => {
      const newLogs = [...prev, entry];
      // Keep only the last maxLogs entries
      return newLogs.slice(-maxLogs);
    });
  }, [maxLogs]);

  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data);
        
        // Handle different event types
        let logEntry: LogEntry | null = null;

        if (data.type === 'AUDIT_LOG' || data.type === 'audit_event') {
          const payload = data.payload || data;
          logEntry = {
            id: `${Date.now()}-${Math.random()}`,
            timestamp: payload.timestamp || new Date().toISOString(),
            level: payload.level === 'error' ? 'error' : 
                   payload.level === 'warning' ? 'warning' : 
                   payload.status === 'success' ? 'success' : 'info',
            agent: payload.agent || payload.agent_name,
            department: payload.department,
            message: payload.message || payload.event || JSON.stringify(payload),
            details: payload,
          };
        } else if (data.type === 'agent_thinking' || data.type === 'agent_action') {
          logEntry = {
            id: `${Date.now()}-${Math.random()}`,
            timestamp: data.timestamp || new Date().toISOString(),
            level: 'info',
            agent: data.agent,
            message: data.message || data.action || 'Agent activity',
            details: data,
          };
        } else if (data.type === 'atom_response') {
          logEntry = {
            id: `${Date.now()}-${Math.random()}`,
            timestamp: data.timestamp || new Date().toISOString(),
            level: 'info',
            agent: 'ATOM',
            message: data.message,
            details: data,
          };
        } else if (data.event) {
          // Handle structured log events
          logEntry = {
            id: `${Date.now()}-${Math.random()}`,
            timestamp: data.timestamp || new Date().toISOString(),
            level: data.level === 'error' ? 'error' : 
                   data.level === 'warning' ? 'warning' : 'info',
            agent: data.agent,
            message: data.event || data.message || JSON.stringify(data),
            details: data,
          };
        }

        if (logEntry) {
          addLog(logEntry);
        }
      } catch (err) {
        console.error('Failed to parse log message:', err);
      }
    };

    socket.addEventListener('message', handleMessage);
    return () => socket.removeEventListener('message', handleMessage);
  }, [socket, addLog]);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (scrollRef.current && !isMinimized) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs, isMinimized]);

  const filteredLogs = filter === 'all' 
    ? logs 
    : logs.filter(log => log.level === filter);

  const clearLogs = () => {
    setLogs([]);
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-50 bg-cyan-500/20 hover:bg-cyan-500/30 backdrop-blur-xl border border-cyan-500/50 rounded-xl px-4 py-2 text-cyan-400 font-bold text-sm transition-all shadow-lg shadow-cyan-500/20"
      >
        📊 Real-Time Logs
      </button>
    );
  }

  return (
    <div className={`fixed bottom-6 right-6 z-50 transition-all duration-300 ${
      isMinimized ? 'h-12 w-96' : 'h-[500px] w-[600px]'
    }`}>
      <div className="w-full h-full bg-slate-950/95 backdrop-blur-2xl border border-cyan-500/30 rounded-2xl flex flex-col shadow-2xl shadow-black overflow-hidden">
        {/* Header */}
        <div className="p-3 border-b border-cyan-500/20 flex items-center justify-between bg-cyan-500/5 flex-shrink-0">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse" />
            <span className="text-xs font-bold text-cyan-400 tracking-widest uppercase">
              Real-Time Operations Log
            </span>
            <span className="ml-2 px-2 py-0.5 bg-blue-600/30 text-blue-300 text-xs rounded-full">
              {filteredLogs.length}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="text-xs bg-slate-900/50 border border-cyan-500/20 rounded px-2 py-1 text-cyan-300 focus:outline-none focus:border-cyan-500/50"
            >
              <option value="all">All</option>
              <option value="error">Errors</option>
              <option value="warning">Warnings</option>
              <option value="info">Info</option>
              <option value="success">Success</option>
            </select>
            <button
              onClick={clearLogs}
              className="text-gray-400 hover:text-red-400 transition-colors p-1"
              title="Clear logs"
            >
              <Trash2 size={14} />
            </button>
            <button
              onClick={() => setIsMinimized(!isMinimized)}
              className="text-gray-400 hover:text-white transition-colors p-1"
            >
              {isMinimized ? <Maximize2 size={14} /> : <Minimize2 size={14} />}
            </button>
            <button
              onClick={() => setIsOpen(false)}
              className="text-gray-400 hover:text-white transition-colors p-1"
            >
              <X size={14} />
            </button>
          </div>
        </div>

        {/* Logs Container */}
        {!isMinimized && (
          <div
            ref={scrollRef}
            className="flex-1 overflow-y-auto p-3 space-y-2 custom-scrollbar"
          >
            {filteredLogs.length === 0 ? (
              <div className="text-center text-gray-500 text-sm py-8">
                No logs yet. Waiting for activity...
              </div>
            ) : (
              filteredLogs.map((log) => (
                <div
                  key={log.id}
                  className={`p-2 rounded-lg border text-xs ${getLogColor(log.level)}`}
                >
                  <div className="flex items-start justify-between gap-2 mb-1">
                    <div className="flex items-center gap-2 flex-1 min-w-0">
                      <span className="text-gray-500 font-mono flex-shrink-0">
                        {formatTimestamp(log.timestamp)}
                      </span>
                      {log.agent && (
                        <span className="text-cyan-300 font-semibold flex-shrink-0">
                          [{log.agent}]
                        </span>
                      )}
                      {log.department && (
                        <span className="text-purple-300 text-[10px] flex-shrink-0">
                          ({log.department})
                        </span>
                      )}
                    </div>
                    <span className="text-[10px] text-gray-500 uppercase flex-shrink-0">
                      {log.level}
                    </span>
                  </div>
                  <div className="text-gray-300 break-words">
                    {log.message}
                  </div>
                  {log.details && Object.keys(log.details).length > 3 && (
                    <details className="mt-1">
                      <summary className="text-[10px] text-gray-500 cursor-pointer hover:text-gray-400">
                        Details
                      </summary>
                      <pre className="text-[10px] text-gray-400 mt-1 overflow-x-auto">
                        {JSON.stringify(log.details, null, 2)}
                      </pre>
                    </details>
                  )}
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
};

