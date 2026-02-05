import React, { useEffect, useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertCircle, ArrowRight, Lightbulb, Shield, Zap } from 'lucide-react';
import { SystemStatusResponse } from '../../api/systemStatusApi';
import { MetricsResult } from '../../api/metricsApi';
import { ScrapedLead, leadManagementApi } from '../../api/leadManagementApi';

interface NextStepAdvisorProps {
  status: SystemStatusResponse | null;
  metrics: MetricsResult | null;
}

interface Suggestion {
  id: string;
  type: 'critical' | 'action' | 'info';
  title: string;
  description: string;
  actionLabel?: string;
  actionTarget?: string; // Could be used to switch tabs
  condition: boolean;
}

export const NextStepAdvisor: React.FC<NextStepAdvisorProps> = ({ status, metrics }) => {
  const [leadsCount, setLeadsCount] = useState(0);
  const [minimized, setMinimized] = useState(false);

  // Check for leads
  useEffect(() => {
    const checkLeads = async () => {
      try {
        const stats = await leadManagementApi.getScrapedLeadsStats();
        setLeadsCount(stats.total_leads || 0);
      } catch (e) {
        // Silent fail
      }
    };
    checkLeads();
  }, []);

  const suggestions = useMemo<Suggestion[]>(() => {
    const list: Suggestion[] = [];

    // Critical Checks
    if (status?.safe_mode) {
      list.push({
        id: 'disable_safe_mode',
        type: 'critical',
        title: 'System in Safe Mode',
        description: 'Autonomous actions are restricted. Disable Safe Mode to enable full agent capabilities.',
        actionLabel: 'Go to Controls',
        actionTarget: 'overview',
        condition: true
      });
    }

    if (status?.agent_paused) {
      list.push({
        id: 'resume_agents',
        type: 'critical',
        title: 'Agents Paused',
        description: 'No tasks will be executed. Resume agent execution to continue operations.',
        actionLabel: 'Resume',
        actionTarget: 'overview',
        condition: true
      });
    }

    // Operational Checks
    const totalRevenue = parseFloat(metrics?.metrics.find(m => m.id === 'total_revenue')?.value.replace(/[^0-9.]/g, '') || '0');
    if (totalRevenue === 0) {
      list.push({
        id: 'setup_revenue',
        type: 'action',
        title: 'No Revenue Detected',
        description: 'Ensure you have active products and payment gateways configured.',
        actionLabel: 'Check Products',
        actionTarget: 'financial',
        condition: true
      });
    }

    if (leadsCount > 0) {
      list.push({
        id: 'process_leads',
        type: 'action',
        title: `${leadsCount} Unprocessed Leads`,
        description: 'Scraped leads are waiting for qualification.',
        actionLabel: 'Review Leads',
        actionTarget: 'leads',
        condition: true
      });
    }

    // General Advice
    if (!status?.safe_mode && !status?.agent_paused) {
       list.push({
        id: 'run_cycle',
        type: 'info',
        title: 'System Ready',
        description: 'Trigger an autonomous cycle to process pending tasks.',
        actionLabel: 'Run Cycle',
        actionTarget: 'overview',
        condition: true
       });
    }

    return list.filter(s => s.condition).slice(0, 3); // Top 3 priority
  }, [status, metrics, leadsCount]);

  if (suggestions.length === 0) return null;

  const current = suggestions[0]; // Show top priority

  return (
    <AnimatePresence>
      {!minimized && (
        <motion.div
          initial={{ opacity: 0, y: 50, x: 50 }}
          animate={{ opacity: 1, y: 0, x: 0 }}
          exit={{ opacity: 0, y: 50 }}
          className="fixed bottom-6 right-6 z-50 max-w-sm w-full"
        >
          <div className={`
            p-4 rounded-xl shadow-2xl backdrop-blur-xl border border-white/10
            ${current.type === 'critical' ? 'bg-rose-900/90 border-rose-500/30' : 
              current.type === 'action' ? 'bg-indigo-900/90 border-indigo-500/30' : 
              'bg-slate-900/90 border-cyan-500/30'}
          `}>
            <div className="flex items-start gap-3">
              <div className={`p-2 rounded-full ${
                current.type === 'critical' ? 'bg-rose-500/20 text-rose-400' : 
                current.type === 'action' ? 'bg-indigo-500/20 text-indigo-400' : 
                'bg-cyan-500/20 text-cyan-400'
              }`}>
                {current.type === 'critical' ? <Shield size={20} /> : 
                 current.type === 'action' ? <Zap size={20} /> : 
                 <Lightbulb size={20} />}
              </div>
              <div className="flex-1">
                <h4 className="font-bold text-white text-sm mb-1">{current.title}</h4>
                <p className="text-xs text-slate-300 mb-3">{current.description}</p>
                
                <div className="flex items-center gap-2">
                    {current.actionLabel && (
                        <button 
                            className="px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-xs font-semibold text-white transition-colors flex items-center gap-1"
                            onClick={() => {
                                // Dispatch custom event to switch tab
                                window.dispatchEvent(new CustomEvent('switch-tab', { detail: current.actionTarget }));
                            }}
                        >
                            {current.actionLabel}
                            <ArrowRight size={12} />
                        </button>
                    )}
                    <button 
                        onClick={() => setMinimized(true)}
                        className="px-3 py-1.5 rounded-lg hover:bg-white/5 text-xs text-slate-400 transition-colors"
                    >
                        Dismiss
                    </button>
                </div>
              </div>
              <button 
                onClick={() => setMinimized(true)}
                className="text-white/40 hover:text-white transition-colors"
              >
                <XIcon />
              </button>
            </div>
            
            {suggestions.length > 1 && (
                <div className="mt-3 pt-3 border-t border-white/10 flex justify-between items-center">
                    <span className="text-[10px] text-white/40">{suggestions.length - 1} more suggestions</span>
                    <div className="flex gap-1">
                        <div className="w-1.5 h-1.5 rounded-full bg-white/60"></div>
                        <div className="w-1.5 h-1.5 rounded-full bg-white/20"></div>
                        <div className="w-1.5 h-1.5 rounded-full bg-white/20"></div>
                    </div>
                </div>
            )}
          </div>
        </motion.div>
      )}
      {minimized && (
          <motion.button
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            onClick={() => setMinimized(false)}
            className="fixed bottom-6 right-6 z-50 w-12 h-12 bg-cyan-500/20 hover:bg-cyan-500/40 border border-cyan-500/50 rounded-full flex items-center justify-center text-cyan-400 shadow-lg backdrop-blur-md transition-colors"
          >
              <Lightbulb size={20} />
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-rose-500 rounded-full text-[10px] flex items-center justify-center text-white font-bold">
                  {suggestions.length}
              </div>
          </motion.button>
      )}
    </AnimatePresence>
  );
};

const XIcon = () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
    </svg>
);
