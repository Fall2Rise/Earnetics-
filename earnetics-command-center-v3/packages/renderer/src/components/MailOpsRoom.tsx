import React, { useEffect, useState } from 'react';
import { useSystemStore } from '../stores/systemStore';

export const MailOpsRoom: React.FC = () => {
    const [campaigns, setCampaigns] = useState<any[]>([]);
    const [subscribers, setSubscribers] = useState<any[]>([]);
    const mailPaused = useSystemStore((state) => state.mailPaused);
    const toggleMailPaused = useSystemStore((state) => state.toggleMailPaused);

    const fetchData = async () => {
        try {
            const cRes = await fetch('http://localhost:8000/api/mailops/campaigns');
            const cData = await cRes.json();
            setCampaigns(cData.campaigns || []);

            const sRes = await fetch('http://localhost:8000/api/mailops/subscribers');
            const sData = await sRes.json();
            setSubscribers(sData.subscribers || []);
        } catch (e) {
            console.error('Failed to fetch mailops data', e);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const sendCampaign = async (id: number) => {
        try {
            await fetch(`http://localhost:8000/api/mailops/campaigns/${id}/send`, { method: 'POST' });
            fetchData();
        } catch (e) {
            alert('Failed to send campaign');
        }
    };

    return (
        <div className="p-4 bg-slate-900 text-white h-full overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold">MailOps Command</h2>
                <button
                    onClick={toggleMailPaused}
                    className={`px-4 py-2 rounded ${mailPaused ? 'bg-red-600' : 'bg-green-600'}`}
                >
                    {mailPaused ? 'RESUME SENDING' : 'PAUSE SENDING'}
                </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-slate-800 p-4 rounded border border-slate-700">
                    <h3 className="font-bold mb-4">Recent Campaigns</h3>
                    {campaigns.map((c) => (
                        <div key={c.id} className="mb-4 p-3 bg-slate-700 rounded">
                            <div className="flex justify-between">
                                <span className="font-bold">{c.subject}</span>
                                <span className={`text-xs px-2 py-1 rounded ${c.status === 'completed' ? 'bg-green-900' : 'bg-yellow-900'}`}>
                                    {c.status}
                                </span>
                            </div>
                            <div className="mt-2 text-sm text-slate-400">
                                Sent: {c.stats?.sent || 0} | Failed: {c.stats?.failed || 0}
                            </div>
                            {c.status === 'draft' && (
                                <button
                                    onClick={() => sendCampaign(c.id)}
                                    className="mt-2 text-xs bg-blue-600 px-2 py-1 rounded hover:bg-blue-500"
                                >
                                    Send Now
                                </button>
                            )}
                        </div>
                    ))}
                </div>

                <div className="bg-slate-800 p-4 rounded border border-slate-700">
                    <h3 className="font-bold mb-4">Subscribers ({subscribers.length})</h3>
                    <div className="max-h-96 overflow-y-auto">
                        {subscribers.map((s) => (
                            <div key={s.email} className="mb-2 p-2 bg-slate-700 rounded flex justify-between text-sm">
                                <span>{s.email}</span>
                                <span className={s.status === 'active' ? 'text-green-400' : 'text-red-400'}>{s.status}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};
