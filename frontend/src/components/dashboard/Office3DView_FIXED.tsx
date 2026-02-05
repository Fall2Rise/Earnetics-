import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Canvas, Suspense } from '@react-three/fiber';
import { fetchSystemStatus, SystemStatusResponse } from '../../api/systemStatusApi';
import { toStatusLabel, toStatusTone } from '../../utils/status';
import { CommandRoom3D } from '../3d/CommandRoom3D';
import { DepartmentRoom } from '../3d/DepartmentRoom';
import { useAgentStore } from '../../stores/agentStore';

const formatCurrency = (value?: number) =>
  new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
  }).format(value ?? 0);

// Department zones configuration
const DEPARTMENT_ZONES = [
  { department: 'Executive Board', color: '#FFD700' },
  { department: 'Finance & Revenue', color: '#00D4FF' },
  { department: 'Creative & Product', color: '#FF1493' },
  { department: 'Tech & Infrastructure', color: '#00FFFF' },
  { department: 'Legal & Sovereignty', color: '#FFA500' },
  { department: 'Health & Human Factor', color: '#FF6B9D' },
  { department: 'Corporate Analytics', color: '#9D4EDD' },
  { department: 'Corporate Execution', color: '#10B981' },
  { department: 'Email Marketing', color: '#F59E0B' },
  { department: 'Revenue Strategy Cell', color: '#9333EA' },
  { department: 'Revenue Execution', color: '#EF4444' },
  { department: 'Lead Generation & Acquisition', color: '#06B6D4' },
  { department: 'Website Growth & Digital Presence', color: '#8B5CF6' },
];

export const Office3DView: React.FC = () => {
  const [status, setStatus] = useState<SystemStatusResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const mountedRef = useRef(true);
  const { fetchAgents, connectWebSocket, disconnectWebSocket, selectedDepartment, selectDepartment, getAgentsByDepartment } = useAgentStore();

  const loadStatus = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetchSystemStatus();
      
      if (!mountedRef.current) {
        return;
      }
      
      setStatus(response);
      setError(null);
      await fetchAgents();
    } catch (err) {
      if (!mountedRef.current) return;
      const message = err instanceof Error ? err.message : 'Unable to sync system status';
      setError(message);
    } finally {
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  }, [fetchAgents]);

  useEffect(() => {
    mountedRef.current = true;
    
    // Load status immediately
    void loadStatus();
    connectWebSocket();
    
    // Set up polling to refresh status every 5 seconds
    const intervalId = setInterval(() => {
      if (mountedRef.current) {
        void loadStatus();
      }
    }, 5000);
    
    return () => {
      clearInterval(intervalId);
      mountedRef.current = false;
      disconnectWebSocket();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Empty deps: only run on mount/unmount to prevent premature unmounting

  const metrics = status?.metrics;
  const lastUpdated = useMemo(() => {
    const timestamp = status?.timestamp;
    if (!timestamp) {
      return 'Awaiting telemetry sync';
    }
    
    const parsed = new Date(timestamp);
    if (Number.isNaN(parsed.valueOf())) {
      return 'Awaiting telemetry sync';
    }
    
    return `Last sync ${parsed.toLocaleString()}`;
  }, [status]);

  const totalRevenue = metrics?.total_revenue ?? 0;
  const monthlyTarget = 10000; // Default target or fetch from settings
  const progress = monthlyTarget > 0 ? Math.min(100, (totalRevenue / monthlyTarget) * 100) : 0;

  const statusPillClass = `status-pill status-pill--${toStatusTone(status?.status)}`;
  const statusLabel = toStatusLabel(status?.status);

  // Get department color and agents
  const departmentZone = DEPARTMENT_ZONES.find(z => z.department === selectedDepartment);
  const departmentAgents = selectedDepartment ? getAgentsByDepartment(selectedDepartment) : [];
  const departmentColor = departmentZone?.color || '#00D4FF';

  return (
    <div className="relative w-full h-screen group">
      {selectedDepartment ? (
        <div className="w-full h-full bg-slate-950 rounded-xl overflow-hidden border border-cyan-500/20">
          <Canvas
            shadows
            gl={{
              preserveDrawingBuffer: true,
              antialias: true,
              powerPreference: "high-performance",
              failIfMajorPerformanceCaveat: false,
            }}
          >
            <Suspense fallback={null}>
              <DepartmentRoom
                department={selectedDepartment}
                color={departmentColor}
                agents={departmentAgents}
                onExit={() => selectDepartment(null)}
              />
            </Suspense>
          </Canvas>
        </div>
      ) : (
        <CommandRoom3D />
      )}

      {/* Overlay UI - only show on main view */}
      {!selectedDepartment && (
        <div className="absolute inset-0 pointer-events-none p-6 flex flex-col justify-between z-10">
          <div className="flex justify-between items-start">
            <div className="bg-black/60 backdrop-blur-xl p-4 rounded-xl border border-cyan-500/30 pointer-events-auto">
              <h2 className="text-xl font-bold text-cyan-400">Fallat Command Nexus</h2>
              <p className="text-[10px] text-gray-400 uppercase tracking-widest">{lastUpdated}</p>
            </div>
            <span className={`${statusPillClass} pointer-events-auto`}>{statusLabel}</span>
          </div>

          <div className="flex justify-between items-end gap-4">
            <div className="bg-black/60 backdrop-blur-xl p-4 rounded-xl border border-cyan-500/30 pointer-events-auto flex-1 max-w-[300px]">
              <span className="text-[10px] text-gray-400 uppercase block mb-1">Total Revenue</span>
              <strong className="text-2xl text-white block">{formatCurrency(totalRevenue)}</strong>
              <div className="mt-2 h-1 bg-gray-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-cyan-500 shadow-[0_0_10px_#06b6d4]"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <small className="text-[9px] text-gray-500 mt-1 block">
                {monthlyTarget > 0
                  ? `${progress.toFixed(1)}% of ${formatCurrency(monthlyTarget)} target`
                  : 'Set monthly target in finance controls'}
              </small>
            </div>

            <div className="flex gap-2 pointer-events-auto">
              <button
                type="button"
                className="bg-cyan-500/20 hover:bg-cyan-500/40 border border-cyan-500/50 text-cyan-300 px-4 py-2 rounded-lg text-xs font-bold transition-all"
                onClick={() => void loadStatus()}
                disabled={loading}
              >
                {loading ? 'SYNCING...' : 'RESYNC TELEMETRY'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Department room overlay - exit button */}
      {selectedDepartment && (
        <div className="absolute top-4 left-4 z-10">
          <button
            onClick={() => selectDepartment(null)}
            className="bg-black/80 backdrop-blur-xl px-4 py-2 rounded-lg border-2 text-white font-bold hover:bg-black/90 transition-all"
            style={{ borderColor: departmentColor }}
          >
            ← Exit {selectedDepartment}
          </button>
        </div>
      )}

      {error && (
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-red-500/20 border border-red-500/50 text-red-400 p-4 rounded-xl backdrop-blur-xl text-sm z-20">
          {error}
        </div>
      )}
    </div>
  );
};
