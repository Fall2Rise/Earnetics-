import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import { Zap, TrendingUp, Brain, History, Play } from 'lucide-react';
import { useEvolutionStore } from '../../stores/evolutionStore';

export const EvolutionView: React.FC = () => {
    const { metrics, loading, fetchMetrics, triggerEvolution } = useEvolutionStore();

    useEffect(() => {
        fetchMetrics();
        // Reduced polling from 30s to 60s to reduce server load
        const interval = setInterval(fetchMetrics, 60000);
        return () => clearInterval(interval);
    }, [fetchMetrics]);

    if (loading && !metrics) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="w-8 h-8 border-4 border-purple-500 border-t-transparent rounded-full animate-spin" />
            </div>
        );
    }

    return (
        <div className="p-6 space-y-8">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-xl font-bold text-white mb-1">Agent Evolution Engine</h2>
                    <p className="text-xs text-gray-500 uppercase tracking-widest">Self-Optimization & Doctrine Mutation</p>
                </div>
                <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={triggerEvolution}
                    disabled={loading}
                    className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-xl font-bold text-xs transition-colors shadow-lg shadow-purple-500/20 disabled:opacity-50"
                >
                    <Play size={14} fill="currentColor" />
                    <span>EVOLVE NOW</span>
                </motion.button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Performance Overview */}
                <div className="lg:col-span-2 space-y-6">
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                        <div className="bg-slate-900/40 border border-purple-500/20 rounded-2xl p-4">
                            <div className="text-[10px] text-gray-500 uppercase mb-1">Total Actions</div>
                            <div className="text-2xl font-bold text-white">{metrics?.total_actions || 0}</div>
                        </div>
                        <div className="bg-slate-900/40 border border-emerald-500/20 rounded-2xl p-4">
                            <div className="text-[10px] text-gray-500 uppercase mb-1">Success Rate</div>
                            <div className="text-2xl font-bold text-emerald-400">
                                {metrics?.total_actions ? Math.round((metrics.successes.length / metrics.total_actions) * 100) : 0}%
                            </div>
                        </div>
                        <div className="bg-slate-900/40 border border-red-500/20 rounded-2xl p-4">
                            <div className="text-[10px] text-gray-500 uppercase mb-1">Anomalies</div>
                            <div className="text-2xl font-bold text-red-400">{metrics?.failures.length || 0}</div>
                        </div>
                    </div>

                    <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 h-64 relative overflow-hidden">
                        <div className="flex items-center justify-between mb-6">
                            <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest flex items-center gap-2">
                                <TrendingUp size={14} />
                                Performance Trends
                            </h3>
                        </div>
                        {metrics && Object.keys(metrics.by_agent || {}).length > 0 ? (
                            <div className="absolute inset-0 flex items-end justify-around px-6 pb-6">
                                {Object.entries(metrics.by_agent)
                                    .sort((a, b) => b[1] - a[1])
                                    .slice(0, 7)
                                    .map(([agent, count], i, arr) => {
                                        const max = Math.max(...arr.map((entry) => entry[1]), 1);
                                        const height = Math.round((count / max) * 100);
                                        return (
                                            <motion.div
                                                key={agent}
                                                initial={{ height: 0 }}
                                                animate={{ height: `${height}%` }}
                                                className="w-8 bg-gradient-to-t from-purple-600/20 to-purple-500 rounded-t-lg shadow-[0_0_15px_rgba(168,85,247,0.3)]"
                                                title={`${agent}: ${count}`}
                                            />
                                        );
                                    })}
                            </div>
                        ) : (
                            <div className="flex items-center justify-center h-full text-xs text-gray-500">
                                No performance data available yet.
                            </div>
                        )}
                    </div>
                </div>

                {/* Doctrine Mutations */}
                <div className="bg-slate-900/40 border border-purple-500/20 rounded-2xl p-6 space-y-6">
                    <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest flex items-center gap-2">
                        <Brain size={14} className="text-purple-400" />
                        Active Mutations
                    </h3>
                    <div className="space-y-4">
                        {metrics?.successes.slice(0, 3).map((row, i) => (
                            <div key={`success-${i}`} className="p-3 bg-purple-500/5 border border-purple-500/10 rounded-xl">
                                <div className="text-[10px] text-purple-400 font-bold uppercase mb-1">Success</div>
                                <p className="text-xs text-gray-300 leading-relaxed">{row[1]}</p>
                                <p className="text-[10px] text-gray-500 mt-1">{row[0]} • {new Date(row[3]).toLocaleString()}</p>
                            </div>
                        ))}
                        {metrics?.failures.slice(0, 2).map((row, i) => (
                            <div key={`failure-${i}`} className="p-3 bg-red-500/5 border border-red-500/10 rounded-xl">
                                <div className="text-[10px] text-red-400 font-bold uppercase mb-1">Failure</div>
                                <p className="text-xs text-gray-300 leading-relaxed">{row[1]}</p>
                                <p className="text-[10px] text-gray-500 mt-1">{row[0]} • {new Date(row[3]).toLocaleString()}</p>
                            </div>
                        ))}
                        {metrics && metrics.successes.length === 0 && metrics.failures.length === 0 && (
                            <div className="flex flex-col items-center justify-center py-8 text-gray-600">
                                <Zap size={24} className="mb-2 opacity-20" />
                                <span className="text-[10px] uppercase font-bold">No mutations pending</span>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Audit Log Snippet */}
            <div className="bg-slate-900/40 border border-slate-800 rounded-2xl overflow-hidden">
                <div className="p-4 border-b border-slate-800 flex items-center justify-between">
                    <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest flex items-center gap-2">
                        <History size={14} />
                        Evolution History
                    </h3>
                </div>
                <div className="divide-y divide-slate-800">
                    {metrics?.successes.slice(0, 5).map((row, i) => (
                        <div key={i} className="p-4 flex items-center justify-between hover:bg-white/5 transition-colors">
                            <div className="flex items-center gap-4">
                                <div className="w-8 h-8 rounded-full bg-emerald-500/10 flex items-center justify-center text-emerald-400">
                                    <Zap size={14} />
                                </div>
                                <div>
                                    <div className="text-xs font-bold text-white">{row[1]}</div>
                                    <div className="text-[10px] text-gray-500">{row[0]} • {new Date(row[3]).toLocaleString()}</div>
                                </div>
                            </div>
                            <div className="px-2 py-1 bg-emerald-500/10 text-emerald-400 text-[9px] font-bold rounded uppercase">
                                Success
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};
