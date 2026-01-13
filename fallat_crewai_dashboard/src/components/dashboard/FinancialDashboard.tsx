import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import { DollarSign, TrendingUp, PieChart, RefreshCcw, AlertCircle, CheckCircle2 } from 'lucide-react';
import { useFinancialStore } from '../../stores/financialStore';

export const FinancialDashboard: React.FC = () => {
    const { metrics, loading, error, fetchMetrics } = useFinancialStore();

    useEffect(() => {
        fetchMetrics();
        const interval = setInterval(fetchMetrics, 30000); // Refresh every 30s
        return () => clearInterval(interval);
    }, [fetchMetrics]);

    if (loading && !metrics) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="w-8 h-8 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-6 bg-red-500/10 border border-red-500/30 rounded-2xl flex items-center gap-3 text-red-400">
                <AlertCircle size={20} />
                <span>{error}</span>
            </div>
        );
    }

    const ownerPayout = metrics?.total_revenue ? metrics.total_revenue * 0.8 : 0;
    const reinvestment = metrics?.total_revenue ? metrics.total_revenue * 0.2 : 0;

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
            {/* Gross Revenue Card */}
            <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                className="bg-slate-900/50 backdrop-blur-xl border border-cyan-500/20 rounded-2xl p-6 shadow-xl shadow-black/20"
            >
                <div className="flex items-center justify-between mb-4">
                    <div className="p-3 bg-cyan-500/10 rounded-xl text-cyan-400">
                        <DollarSign size={24} />
                    </div>
                    <span className="text-xs font-bold text-cyan-500/50 tracking-widest uppercase">Gross Revenue</span>
                </div>
                <div className="text-3xl font-bold text-white mb-1">
                    ${metrics?.total_revenue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </div>
                <div className="flex items-center gap-2 text-xs text-emerald-400">
                    <TrendingUp size={14} />
                    <span>+12.5% from last cycle</span>
                </div>
            </motion.div>

            {/* 80/20 Split Card */}
            <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.1 }}
                className="bg-slate-900/50 backdrop-blur-xl border border-purple-500/20 rounded-2xl p-6 shadow-xl shadow-black/20"
            >
                <div className="flex items-center justify-between mb-4">
                    <div className="p-3 bg-purple-500/10 rounded-xl text-purple-400">
                        <PieChart size={24} />
                    </div>
                    <span className="text-xs font-bold text-purple-500/50 tracking-widest uppercase">Profit Split (80/20)</span>
                </div>
                <div className="space-y-4">
                    <div>
                        <div className="flex justify-between text-xs text-gray-400 mb-1">
                            <span>Owner Payout (80%)</span>
                            <span className="text-purple-400">${ownerPayout.toLocaleString()}</span>
                        </div>
                        <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                            <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: '80%' }}
                                className="h-full bg-purple-500 shadow-[0_0_10px_rgba(168,85,247,0.5)]"
                            />
                        </div>
                    </div>
                    <div>
                        <div className="flex justify-between text-xs text-gray-400 mb-1">
                            <span>Reinvestment (20%)</span>
                            <span className="text-cyan-400">${reinvestment.toLocaleString()}</span>
                        </div>
                        <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                            <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: '20%' }}
                                className="h-full bg-cyan-500 shadow-[0_0_10px_rgba(6,182,212,0.5)]"
                            />
                        </div>
                    </div>
                </div>
            </motion.div>

            {/* Reinvestment Fund Card */}
            <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.2 }}
                className="bg-slate-900/50 backdrop-blur-xl border border-emerald-500/20 rounded-2xl p-6 shadow-xl shadow-black/20"
            >
                <div className="flex items-center justify-between mb-4">
                    <div className="p-3 bg-emerald-500/10 rounded-xl text-emerald-400">
                        <RefreshCcw size={24} />
                    </div>
                    <span className="text-xs font-bold text-emerald-500/50 tracking-widest uppercase">Reinvestment Fund</span>
                </div>
                <div className="text-3xl font-bold text-white mb-1">
                    ${metrics?.total_reinvested.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </div>
                <div className="flex items-center gap-2 text-xs text-emerald-400">
                    <CheckCircle2 size={14} />
                    <span>{metrics?.pending_payouts_count} pending allocations</span>
                </div>
            </motion.div>

            {/* Payout Status Card */}
            <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="bg-slate-900/50 backdrop-blur-xl border border-amber-500/20 rounded-2xl p-6 shadow-xl shadow-black/20 col-span-full"
            >
                <div className="flex items-center justify-between mb-6">
                    <h3 className="text-sm font-bold text-white tracking-widest uppercase">Payout Pipeline</h3>
                    <div className="flex gap-4">
                        <div className="text-center">
                            <div className="text-xs text-gray-500 uppercase">Pending</div>
                            <div className="text-lg font-bold text-amber-400">${metrics?.pending_payout_amount.toLocaleString()}</div>
                        </div>
                        <div className="text-center">
                            <div className="text-xs text-gray-500 uppercase">Failed</div>
                            <div className="text-lg font-bold text-red-400">{metrics?.failed_payouts_count}</div>
                        </div>
                    </div>
                </div>

                <div className="relative h-24 flex items-center justify-between px-12">
                    {/* Pipeline Line */}
                    <div className="absolute top-1/2 left-0 w-full h-0.5 bg-slate-800 -translate-y-1/2" />

                    {/* Steps */}
                    {[
                        { label: 'Revenue In', status: 'completed' },
                        { label: '80/20 Split', status: 'completed' },
                        { label: 'Owner Queue', status: metrics?.pending_payout_amount ? 'active' : 'idle' },
                        { label: 'Stripe Payout', status: 'idle' }
                    ].map((step, i) => (
                        <div key={i} className="relative z-10 flex flex-col items-center">
                            <div className={`w-4 h-4 rounded-full border-2 transition-all duration-500 ${step.status === 'completed' ? 'bg-emerald-500 border-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]' :
                                    step.status === 'active' ? 'bg-amber-500 border-amber-500 animate-pulse shadow-[0_0_10px_rgba(245,158,11,0.5)]' :
                                        'bg-slate-900 border-slate-700'
                                }`} />
                            <span className="absolute top-6 text-[10px] text-gray-500 whitespace-nowrap font-bold uppercase tracking-tighter">
                                {step.label}
                            </span>
                        </div>
                    ))}
                </div>
            </motion.div>
        </div>
    );
};
