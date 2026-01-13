import React, { useCallback, useEffect, useState } from 'react';
import { X, Users, Activity, TrendingUp, Clock, CheckCircle } from 'lucide-react';
import { useAgentStore } from '../../stores/agentStore';
import { fetchOperationsMetrics, OperationsMetricsResponse } from '../../api/operationsApi';
import { API_BASE_URL } from '../../api/config';

interface DepartmentDetailModalProps {
  department: string;
  color: string;
  onClose: () => void;
}

interface DepartmentTask {
  id: string;
  title: string;
  status: string;
  priority: string;
  created_at: string;
  assigned_agent?: string;
}

export const DepartmentDetailModal: React.FC<DepartmentDetailModalProps> = ({
  department,
  color,
  onClose,
}) => {
  const { getAgentsByDepartment } = useAgentStore();
  const [tasks, setTasks] = useState<DepartmentTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [operations, setOperations] = useState<OperationsMetricsResponse | null>(null);

  const agents = getAgentsByDepartment(department);
  const activeAgents = agents.filter(a => a.status === 'active').length;
  const totalMemory = agents.reduce((sum, a) => sum + (a.memoryEntries || 0), 0);
  const avgPerformance = agents.length > 0
    ? agents.reduce((sum, a) => sum + a.performance, 0) / agents.length
    : 0;

  const loadDepartmentData = useCallback(async () => {
    setLoading(true);
    try {
      // Fetch tasks for this department
      try {
        const tasksResponse = await fetch(`${API_BASE_URL}/api/workflows/pending`);
        if (tasksResponse.ok) {
          const data = await tasksResponse.json();
          const departmentTasks = (data.workflows || [])
            .filter((t: any) => t.department === department)
            .slice(0, 10); // Limit to 10 recent tasks
          setTasks(departmentTasks);
        }
      } catch (err) {
        console.error('Failed to fetch department tasks:', err);
      }

      // Fetch operations metrics
      try {
        const opsData = await fetchOperationsMetrics();
        setOperations(opsData);
      } catch (err) {
        console.error('Failed to fetch operations:', err);
      }
    } finally {
      setLoading(false);
    }
  }, [department]);

  useEffect(() => {
    void loadDepartmentData();
    const interval = setInterval(loadDepartmentData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [loadDepartmentData]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div className="relative w-full max-w-4xl max-h-[90vh] overflow-hidden rounded-2xl shadow-2xl border-2" style={{ borderColor: color }}>
        {/* Glow effect */}
        <div
          className="absolute inset-0 rounded-2xl blur-2xl opacity-30"
          style={{ backgroundColor: color }}
        />
        
        {/* Main panel */}
        <div className="relative bg-black/95 backdrop-blur-xl overflow-hidden flex flex-col h-full">
          {/* Header */}
          <div
            className="px-6 py-4 border-b flex items-center justify-between"
            style={{ borderColor: `${color}40` }}
          >
            <div className="flex items-center gap-3">
              <div
                className="w-3 h-3 rounded-full animate-pulse"
                style={{ backgroundColor: color }}
              />
              <h2 className="text-2xl font-bold text-white" style={{ textShadow: `0 0 10px ${color}` }}>
                {department}
              </h2>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-white transition-colors p-2 hover:bg-white/10 rounded-lg"
            >
              <X size={20} />
            </button>
          </div>

          {/* Scrollable content */}
          <div className="flex-1 overflow-y-auto">
            {/* Stats */}
            <div className="px-6 py-4 grid grid-cols-4 gap-4 border-b" style={{ borderColor: `${color}40` }}>
              <div className="text-center">
                <div className="flex items-center justify-center gap-2 mb-1">
                  <Users size={16} className="text-gray-400" />
                  <span className="text-2xl font-bold text-white">{agents.length}</span>
                </div>
                <div className="text-xs text-gray-400">Total Agents</div>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center gap-2 mb-1">
                  <Activity size={16} className="text-green-400" />
                  <span className="text-2xl font-bold text-green-400">{activeAgents}</span>
                </div>
                <div className="text-xs text-gray-400">Active</div>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center gap-2 mb-1">
                  <TrendingUp size={16} className="text-blue-400" />
                  <span className="text-2xl font-bold text-blue-400">{totalMemory}</span>
                </div>
                <div className="text-xs text-gray-400">Memory Entries</div>
              </div>
              <div className="text-center">
                <div className="mb-1">
                  <span className="text-2xl font-bold text-white">{avgPerformance.toFixed(0)}%</span>
                </div>
                <div className="text-xs text-gray-400">Avg Performance</div>
              </div>
            </div>

            {/* Recent Tasks */}
            <div className="px-6 py-4">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Clock size={18} />
                Recent Operations
              </h3>
              {loading ? (
                <div className="text-center py-8 text-gray-400">Loading operations...</div>
              ) : tasks.length === 0 ? (
                <div className="text-center py-8 text-gray-400 rounded-lg bg-white/5 border" style={{ borderColor: `${color}20` }}>
                  No recent operations for this department
                </div>
              ) : (
                <div className="space-y-2">
                  {tasks.map((task) => (
                    <div
                      key={task.id}
                      className="p-4 rounded-lg bg-white/5 hover:bg-white/10 transition-colors border"
                      style={{ borderColor: `${color}20` }}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="text-white font-semibold mb-1">{task.title || 'Untitled Task'}</div>
                          {task.description && (
                            <div className="text-sm text-gray-400 mb-2">{task.description}</div>
                          )}
                          <div className="flex items-center gap-4 text-xs text-gray-500">
                            <span className="flex items-center gap-1">
                              <Activity size={12} />
                              {task.status || 'pending'}
                            </span>
                            <span className="px-2 py-1 rounded bg-white/10">{task.priority || 'medium'}</span>
                            {task.assigned_agent && (
                              <span>Agent: {task.assigned_agent}</span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Agent List */}
            <div className="px-6 py-4 border-t" style={{ borderColor: `${color}40` }}>
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Users size={18} />
                Agents ({agents.length})
              </h3>
              {agents.length === 0 ? (
                <div className="text-center py-8 text-gray-400 rounded-lg bg-white/5 border" style={{ borderColor: `${color}20` }}>
                  No agents in this department
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {agents.map((agent) => (
                    <div
                      key={agent.id}
                      className="flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors border"
                      style={{ borderColor: `${color}20` }}
                    >
                      <div className="flex items-center gap-3 flex-1">
                        <div
                          className="w-2 h-2 rounded-full"
                          style={{
                            backgroundColor:
                              agent.status === 'active'
                                ? '#10b981'
                                : agent.status === 'idle'
                                ? '#f59e0b'
                                : '#ef4444',
                          }}
                        />
                        <div className="flex-1 min-w-0">
                          <div className="text-white font-semibold truncate">{agent.name}</div>
                          <div className="text-xs text-gray-400 truncate">{agent.role}</div>
                          {agent.currentTask && (
                            <div className="text-xs text-gray-500 mt-1 truncate italic">
                              {agent.currentTask}
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="text-right flex-shrink-0 ml-2">
                        <div className="text-sm text-white font-mono">
                          {agent.performance.toFixed(0)}%
                        </div>
                        <div className="text-xs text-gray-400">
                          {agent.memoryEntries || 0} entries
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
