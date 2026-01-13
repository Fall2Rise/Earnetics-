import React, { useEffect, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link2, Link2Off, Shield, ShieldAlert, Globe, Mail, CreditCard, Share2, Settings, X, Check, AlertCircle, Loader2, Trash2 } from 'lucide-react';
import { useIntegrationStore } from '../../stores/integrationStore';
import { 
    fetchIntegrationRequirements, 
    configureIntegration, 
    testIntegration, 
    removeIntegration,
    type IntegrationRequirements,
    type TestResult 
} from '../../api/integrationsApi';

interface ConfigFormState {
    [key: string]: string;
}

export const IntegrationsPanel: React.FC = () => {
    const { integrations, fetchIntegrations } = useIntegrationStore();
    const [selectedIntegration, setSelectedIntegration] = useState<string | null>(null);
    const [requirements, setRequirements] = useState<IntegrationRequirements | null>(null);
    const [formData, setFormData] = useState<ConfigFormState>({});
    const [loading, setLoading] = useState(false);
    const [testing, setTesting] = useState(false);
    const [testResult, setTestResult] = useState<TestResult | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    useEffect(() => {
        fetchIntegrations();
        const interval = setInterval(fetchIntegrations, 60000);
        return () => clearInterval(interval);
    }, [fetchIntegrations]);

    const handleConfigureClick = useCallback(async (integrationName: string) => {
        setSelectedIntegration(integrationName);
        setError(null);
        setSuccess(null);
        setTestResult(null);
        
        try {
            const reqs = await fetchIntegrationRequirements(integrationName);
            setRequirements(reqs);
            
            // Pre-fill form with empty strings
            const initialData: ConfigFormState = {};
            reqs.requirements.forEach(req => {
                initialData[req.name] = '';
            });
            setFormData(initialData);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load requirements');
        }
    }, []);

    const handleCloseModal = useCallback(() => {
        setSelectedIntegration(null);
        setRequirements(null);
        setFormData({});
        setError(null);
        setSuccess(null);
        setTestResult(null);
    }, []);

    const handleInputChange = useCallback((name: string, value: string) => {
        setFormData(prev => ({ ...prev, [name]: value }));
        setError(null);
    }, []);

    const handleSubmit = useCallback(async (e: React.FormEvent, testConnection: boolean = false) => {
        e.preventDefault();
        if (!selectedIntegration) return;

        setLoading(true);
        setError(null);
        setSuccess(null);
        setTestResult(null);

        try {
            const result = await configureIntegration(selectedIntegration, {
                credentials: formData,
                test_connection: testConnection
            });

            setSuccess(`Integration configured successfully! ${result.credentials_stored.length} credentials stored.`);
            
            if (result.test_result) {
                setTestResult(result.test_result);
            }

            // Refresh integrations list
            await fetchIntegrations();

            // Close modal after short delay if successful
            if (!testConnection) {
                setTimeout(() => {
                    handleCloseModal();
                }, 2000);
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to configure integration');
        } finally {
            setLoading(false);
        }
    }, [selectedIntegration, formData, fetchIntegrations, handleCloseModal]);

    const handleTest = useCallback(async () => {
        if (!selectedIntegration) return;

        setTesting(true);
        setError(null);
        setTestResult(null);

        try {
            const result = await testIntegration(selectedIntegration);
            setTestResult(result);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to test integration');
        } finally {
            setTesting(false);
        }
    }, [selectedIntegration]);

    const handleRemove = useCallback(async (integrationName: string) => {
        if (!window.confirm(`Are you sure you want to remove all credentials for ${integrationName}? This action cannot be undone.`)) {
            return;
        }

        setLoading(true);
        setError(null);

        try {
            await removeIntegration(integrationName);
            setSuccess(`Integration ${integrationName} removed successfully`);
            await fetchIntegrations();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to remove integration');
        } finally {
            setLoading(false);
        }
    }, [fetchIntegrations]);

    const getIcon = (name: string) => {
        switch (name.toLowerCase()) {
            case 'stripe': return <CreditCard size={18} />;
            case 'email': return <Mail size={18} />;
            case 'social': return <Share2 size={18} />;
            case 'llm': return <Globe size={18} />;
            default: return <Globe size={18} />;
        }
    };

    return (
        <div className="p-6 space-y-6">
            <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white tracking-widest uppercase">External Integrations</h3>
                <div className="flex items-center gap-2 px-3 py-1 bg-cyan-500/10 border border-cyan-500/20 rounded-full">
                    <Shield size={12} className="text-cyan-400" />
                    <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-tighter">Secure Link Active</span>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(integrations).map(([name, data]) => (
                    <motion.div
                        key={name}
                        initial={{ scale: 0.95, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className={`p-4 rounded-xl border transition-all cursor-pointer hover:border-opacity-60 ${
                            data.status === 'connected'
                                ? 'bg-slate-900/40 border-emerald-500/20'
                                : 'bg-slate-900/40 border-red-500/20'
                        }`}
                    >
                        <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center gap-3">
                                <div className={`p-2 rounded-lg ${
                                    data.status === 'connected' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'
                                }`}>
                                    {getIcon(name)}
                                </div>
                                <span className="text-sm font-bold text-white capitalize">{name}</span>
                            </div>
                            <div className="flex items-center gap-2">
                                {data.status === 'connected' ? (
                                    <Link2 size={16} className="text-emerald-500" />
                                ) : (
                                    <Link2Off size={16} className="text-red-500" />
                                )}
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        handleConfigureClick(name);
                                    }}
                                    className="p-1 hover:bg-white/10 rounded transition-colors"
                                    title="Configure"
                                >
                                    <Settings size={14} className="text-gray-400 hover:text-white" />
                                </button>
                                {data.status === 'connected' && (
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            handleRemove(name);
                                        }}
                                        className="p-1 hover:bg-red-500/20 rounded transition-colors"
                                        title="Remove"
                                    >
                                        <Trash2 size={14} className="text-red-400 hover:text-red-300" />
                                    </button>
                                )}
                            </div>
                        </div>

                        <div className="space-y-2">
                            <div className="flex items-center justify-between text-[10px] uppercase tracking-widest">
                                <span className="text-gray-500">Status</span>
                                <span className={data.status === 'connected' ? 'text-emerald-400' : 'text-red-400'}>
                                    {data.status}
                                </span>
                            </div>

                            <div className="flex items-center justify-between text-[10px] uppercase tracking-widest">
                                <span className="text-gray-500">Mode</span>
                                <span className={data.production_mode ? 'text-amber-400' : 'text-cyan-400'}>
                                    {data.production_mode ? 'PRODUCTION' : 'SIMULATION'}
                                </span>
                            </div>

                            {data.missing_vars.length > 0 && (
                                <div className="mt-2 p-2 bg-red-500/5 rounded border border-red-500/10">
                                    <div className="flex items-center gap-1 text-[9px] text-red-400 font-bold uppercase mb-1">
                                        <ShieldAlert size={10} />
                                        <span>Missing Configuration</span>
                                    </div>
                                    <div className="flex flex-wrap gap-1">
                                        {data.missing_vars.map(v => (
                                            <span key={v} className="px-1.5 py-0.5 bg-red-500/10 text-red-300 text-[8px] rounded font-mono">
                                                {v}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </motion.div>
                ))}
            </div>

            {/* Configuration Modal */}
            <AnimatePresence>
                {selectedIntegration && requirements && (
                    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.9 }}
                            className="bg-slate-900 border border-cyan-500/30 rounded-xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
                        >
                            <div className="flex items-center justify-between mb-6">
                                <h2 className="text-xl font-bold text-white capitalize">
                                    Configure {selectedIntegration}
                                </h2>
                                <button
                                    onClick={handleCloseModal}
                                    className="p-2 hover:bg-white/10 rounded transition-colors"
                                >
                                    <X size={20} className="text-gray-400" />
                                </button>
                            </div>

                            <form onSubmit={(e) => handleSubmit(e, false)} className="space-y-4">
                                {requirements.requirements.map((req) => (
                                    <div key={req.name}>
                                        <label className="block text-sm font-medium text-gray-300 mb-2">
                                            {req.name}
                                            <span className="text-red-400 ml-1">*</span>
                                        </label>
                                        <p className="text-xs text-gray-500 mb-2">{req.description}</p>
                                        <input
                                            type={req.name.toLowerCase().includes('password') || req.name.toLowerCase().includes('secret') || req.name.toLowerCase().includes('key') ? 'password' : 'text'}
                                            value={formData[req.name] || ''}
                                            onChange={(e) => handleInputChange(req.name, e.target.value)}
                                            className="w-full px-4 py-2 bg-slate-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500"
                                            placeholder={`Enter ${req.name}`}
                                            required
                                        />
                                    </div>
                                ))}

                                {error && (
                                    <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-2 text-red-400 text-sm">
                                        <AlertCircle size={16} />
                                        <span>{error}</span>
                                    </div>
                                )}

                                {success && (
                                    <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg flex items-center gap-2 text-emerald-400 text-sm">
                                        <Check size={16} />
                                        <span>{success}</span>
                                    </div>
                                )}

                                {testResult && (
                                    <div className={`p-3 border rounded-lg flex items-start gap-2 text-sm ${
                                        testResult.success
                                            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                                            : 'bg-red-500/10 border-red-500/30 text-red-400'
                                    }`}>
                                        {testResult.success ? <Check size={16} className="mt-0.5" /> : <AlertCircle size={16} className="mt-0.5" />}
                                        <div className="flex-1">
                                            <p className="font-medium">{testResult.message}</p>
                                            {testResult.details && Object.keys(testResult.details).length > 0 && (
                                                <pre className="text-xs mt-2 opacity-75">
                                                    {JSON.stringify(testResult.details, null, 2)}
                                                </pre>
                                            )}
                                        </div>
                                    </div>
                                )}

                                <div className="flex gap-3 pt-4">
                                    <button
                                        type="submit"
                                        disabled={loading}
                                        className="flex-1 bg-cyan-500 hover:bg-cyan-600 text-white font-bold py-2 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                                    >
                                        {loading ? (
                                            <>
                                                <Loader2 size={16} className="animate-spin" />
                                                Saving...
                                            </>
                                        ) : (
                                            'Save Configuration'
                                        )}
                                    </button>
                                    <button
                                        type="button"
                                        onClick={(e) => handleSubmit(e, true)}
                                        disabled={loading}
                                        className="flex-1 bg-emerald-500 hover:bg-emerald-600 text-white font-bold py-2 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                                    >
                                        {loading ? (
                                            <>
                                                <Loader2 size={16} className="animate-spin" />
                                                Testing...
                                            </>
                                        ) : (
                                            'Save & Test'
                                        )}
                                    </button>
                                    <button
                                        type="button"
                                        onClick={handleTest}
                                        disabled={testing || Object.values(formData).some(v => !v)}
                                        className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                                    >
                                        {testing ? (
                                            <>
                                                <Loader2 size={16} className="animate-spin" />
                                                Testing...
                                            </>
                                        ) : (
                                            'Test Only'
                                        )}
                                    </button>
                                </div>
                            </form>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </div>
    );
};
