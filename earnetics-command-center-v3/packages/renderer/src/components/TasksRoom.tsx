import React, { useEffect, useState } from 'react';

export const TasksRoom: React.FC = () => {
    const [tasks, setTasks] = useState<any[]>([]);
    const [department, setDepartment] = useState<string>('');

    const fetchTasks = async () => {
        try {
            let url = 'http://localhost:8000/api/tasks';
            if (department) url += `?department=${department}`;
            const res = await fetch(url);
            const data = await res.json();
            setTasks(data.tasks || []);
        } catch (e) {
            console.error('Failed to fetch tasks', e);
        }
    };

    useEffect(() => {
        fetchTasks();
    }, [department]);

    return (
        <div className="p-4 bg-slate-900 text-white h-full overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold">Task Engine</h2>
                <select
                    value={department}
                    onChange={(e) => setDepartment(e.target.value)}
                    className="bg-slate-800 border border-slate-600 rounded px-2 py-1"
                >
                    <option value="">All Departments</option>
                    <option value="marketing">Marketing</option>
                    <option value="sales">Sales</option>
                    <option value="product">Product</option>
                    <option value="operations">Operations</option>
                    <option value="finance">Finance</option>
                </select>
            </div>

            <div className="space-y-4">
                {tasks.map((task) => (
                    <div key={task.id} className="bg-slate-800 p-4 rounded border border-slate-700 flex justify-between items-start">
                        <div>
                            <div className="flex items-center gap-2">
                                <span className={`px-2 py-0.5 text-xs rounded uppercase ${task.priority === 'critical' ? 'bg-red-900 text-red-200' :
                                        task.priority === 'high' ? 'bg-orange-900 text-orange-200' :
                                            'bg-slate-600 text-slate-200'
                                    }`}>
                                    {task.priority}
                                </span>
                                <h3 className="font-bold">{task.title}</h3>
                            </div>
                            <p className="text-sm text-slate-400 mt-1">{task.description}</p>
                            <div className="mt-2 text-xs text-slate-500">
                                Dept: {task.department} | Agent: {task.assigned_agent || 'Unassigned'} | Status: {task.status}
                            </div>
                        </div>
                        <div className="text-right text-xs text-slate-600">
                            ID: {task.id}
                        </div>
                    </div>
                ))}
                {tasks.length === 0 && (
                    <div className="text-center text-slate-500 py-10">No tasks found.</div>
                )}
            </div>
        </div>
    );
};
