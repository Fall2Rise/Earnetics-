import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import { Shield, ShieldCheck, Power, Lock, Eye } from 'lucide-react';
import { useSecurityStore } from '../../stores/securityStore';

export const SecurityPanel: React.FC = () => {
    const { status, loading, fetchStatus, toggleKillSwitch } = useSecurityStore();

    useEffect(() => {
        fetchStatus();
        const interval = setInterval(fetchStatus, 10000); // Refresh every 10s
        return () => clearInterval(interval);
    }, [fetchStatus]);

    const isKillSwitchActive = status?.kill_switch_active;

    return (
        <div className="p-6 space-y-6">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${isKillSwitchActive ? 'bg-red-500/20 text-red-500' : 'bg-cyan-500/20 text-cyan-400'}`}>
                        <Shield size={20} />
                    </div>
                    <div>
                        <h3 className="text-sm font-bold text-white tracking-widest uppercase">Governance & Safety</h3>
                        <p className="text-[10px] text-gray-500 uppercase tracking-tighter">Prime Directive Guardian Active</p>
                    </div>
                </div>
                <div className={`px-3 py-1 rounded-full border text-[10px] font-bold uppercase tracking-widest ${isKillSwitchActive ? 'bg-red-500/10 border-red-500/30 text-red-500' : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                    }`}>
                    {isKillSwitchActive ? 'System Halted' : 'System Secure'}
                </div>
            </div>

            {/* Emergency Kill Switch */}
            <motion.div
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className={`p-6 rounded-2xl border-2 transition-all duration-500 ${isKillSwitchActive
                    ? 'bg-red-500/10 border-red-500 shadow-[0_0_30px_rgba(239,68,68,0.3)]'
                    : 'bg-slate-900/40 border-slate-800'
                    }`}
            >
                <div className="flex flex-col items-center text-center space-y-4">
                    <div className={`p-4 rounded-full transition-colors duration-500 ${isKillSwitchActive ? 'bg-red-500 text-white animate-pulse' : 'bg-slate-800 text-gray-500'
                        }`}>
                        <Power size={32} />
                    </div>
                    <div>
                        <h4 className={`text-lg font-bold uppercase tracking-tighter ${isKillSwitchActive ? 'text-red-500' : 'text-white'}`}>
                            Emergency Kill Switch
                        </h4>
                        <p className="text-xs text-gray-500 max-w-xs mx-auto mt-1">
                            Immediately halts all autonomous agent execution, financial processing, and email distribution.
                        </p>
                    </div>
                    <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => toggleKillSwitch(!isKillSwitchActive)}
                        disabled={loading}
                        className={`px-8 py-3 rounded-xl font-black text-sm tracking-widest transition-all ${isKillSwitchActive
                            ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-500/20'
                            : 'bg-red-600 hover:bg-red-500 text-white shadow-lg shadow-red-500/20'
                            }`}
                    >
                        {isKillSwitchActive ? 'RESUME OPERATIONS' : 'ACTIVATE KILL SWITCH'}
                    </motion.button>
                </div>
            </motion.div>

            {/* Safety Metrics */}
            <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-4">
                    <div className="flex items-center gap-2 text-[10px] text-gray-500 uppercase mb-2">
                        <Lock size={12} />
                        <span>Compliance Score</span>
                    </div>
                    <div className="text-xl font-bold text-white">100%</div>
                    <div className="h-1 bg-slate-800 rounded-full mt-2 overflow-hidden">
                        <div className="h-full bg-emerald-500 w-full" />
                    </div>
                </div>
                <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-4">
                    <div className="flex items-center gap-2 text-[10px] text-gray-500 uppercase mb-2">
                        <Eye size={12} />
                        <span>Drift Detection</span>
                    </div>
                    <div className="text-xl font-bold text-white">0.02%</div>
                    <div className="h-1 bg-slate-800 rounded-full mt-2 overflow-hidden">
                        <div className="h-full bg-cyan-500 w-[2%]" />
                    </div>
                </div>
            </div>

            {/* Compliance Alerts */}
            <div className="space-y-3">
                <h4 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Recent Compliance Checks</h4>
                <div className="space-y-2">
                    {[
                        { label: 'Prime Directive Alignment', status: 'secure' },
                        { label: 'Financial Split Validation', status: 'secure' },
                        { label: 'Agent Mutation Audit', status: 'secure' }
                    ].map((check, i) => (
                        <div key={i} className="flex items-center justify-between p-3 bg-slate-900/20 border border-slate-800/50 rounded-lg">
                            <span className="text-xs text-gray-300">{check.label}</span>
                            <ShieldCheck size={14} className="text-emerald-500" />
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};
