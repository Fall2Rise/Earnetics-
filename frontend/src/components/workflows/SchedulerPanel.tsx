import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  SchedulerJob,
  SchedulerJobResult,
  ScheduleType,
  createJob,
  deleteJob,
  listJobs,
  runDueJobs,
  runJob,
} from '../../api/schedulerApi';

type FormState = {
  jobId: string;
  handler: string;
  scheduleType: ScheduleType;
  scheduleValue: string;
  startAt: string;
  payload: string;
};

const handlerPresets: Array<{ value: string; label: string; payload: Record<string, unknown> }> = [
  {
    value: 'revenue.launch_product',
    label: 'Launch Product Pipeline',
    payload: {
      opportunity: {
        keyword: 'AI automation blueprint',
        trend_score: 0.85,
        market_size: '$1.2B',
      },
    },
  },
  {
    value: 'revenue.affiliate_cycle',
    label: 'Affiliate Cycle (Business)',
    payload: { category: 'business' },
  },
  {
    value: 'revenue.dropshipping_cycle',
    label: 'Dropshipping Cycle',
    payload: {},
  },
  {
    value: 'log_payload',
    label: 'Log Payload (Test)',
    payload: { test: true },
  },
];

const defaultForm: FormState = {
  jobId: '',
  handler: handlerPresets[0].value,
  scheduleType: 'interval',
  scheduleValue: '86400',
  startAt: '',
  payload: JSON.stringify(handlerPresets[0].payload, null, 2),
};

export const SchedulerPanel: React.FC = () => {
  const [jobs, setJobs] = useState<SchedulerJob[]>([]);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [running, setRunning] = useState(false);
  const [form, setForm] = useState<FormState>(defaultForm);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const loadJobs = useCallback(async (abortSignal?: AbortSignal) => {
    setLoading(true);
    try {
      const data = await listJobs(abortSignal);
      if (abortSignal?.aborted) return; // Don't update state if request was cancelled
      setJobs(data);
      setError(null);
    } catch (err) {
      if (abortSignal?.aborted) return; // Ignore errors from cancelled requests
      setError(err instanceof Error ? err.message : 'Failed to load jobs');
    } finally {
      if (!abortSignal?.aborted) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    const abortController = new AbortController();
    void loadJobs(abortController.signal);
    return () => {
      abortController.abort(); // Cancel request on unmount
    };
  }, [loadJobs]);

  const handleChange = (key: keyof FormState) => (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const value = event.target.value;
    setForm((prev) => ({ ...prev, [key]: value }));
    if (key === 'handler') {
      const preset = handlerPresets.find((item) => item.value === value);
      if (preset) {
        setForm((prev) => ({
          ...prev,
          handler: value,
          payload: JSON.stringify(preset.payload, null, 2),
        }));
      }
    }
  };

  const displayJobs = useMemo(
    () =>
      jobs.map((job) => ({
        ...job,
        payload: JSON.stringify(job.payload, null, 0),
      })),
    [jobs],
  );

  const resetForm = () => {
    setForm(defaultForm);
  };

  const handleCreateJob = async (event: React.FormEvent) => {
    event.preventDefault();
    setCreating(true);
    setSuccessMessage(null);
    try {
      const parsedPayload = form.payload ? JSON.parse(form.payload) : {};
      await createJob({
        job_id: form.jobId || `${form.handler}-${Date.now()}`,
        handler: form.handler,
        payload: parsedPayload,
        schedule_type: form.scheduleType,
        schedule_value: form.scheduleValue,
        start_at: form.startAt || undefined,
      });
      setSuccessMessage('Job saved successfully.');
      setError(null);
      resetForm();
      await loadJobs();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create job');
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteJob = async (jobId: string) => {
    if (!confirm(`Are you sure you want to delete job "${jobId}"?`)) {
      return;
    }
    setError(null);
    setSuccessMessage(null);
    try {
      await deleteJob(jobId);
      setSuccessMessage(`Job "${jobId}" deleted successfully.`);
      await loadJobs();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete job');
    }
  };

  const handleRunJob = async (jobId: string) => {
    setRunning(true);
    try {
      const result = await runJob(jobId);
      if (result.status === 'error') {
        throw new Error(result.message ?? 'Job run failed');
      }
      setSuccessMessage(`Job ${jobId} completed successfully.`);
      setError(null);
      await loadJobs();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to run job');
    } finally {
      setRunning(false);
    }
  };

  const handleRunDueJobs = async () => {
    setRunning(true);
    setSuccessMessage(null);
    setError(null);
    try {
      const results = await runDueJobs();
      const errors = results.filter((result) => result.status === 'error');
      if (errors.length) {
        const messages = errors.map((item) => `${item.job_id}: ${item.message ?? 'Failed'}`).join(', ');
        throw new Error(messages);
      }
      setSuccessMessage(`Successfully ran ${results.length} due job(s).`);
      await loadJobs(); // Refresh job list after running
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to run due jobs');
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="scheduler-panel">
      <header className="panel-header">
        <div>
          <h3>⏰ Automation Scheduler</h3>
          <span className="scheduler-panel__subtitle">Schedule recurring revenue jobs, product launches, and automated workflows</span>
        </div>
        <div className="panel-header__actions">
          <button type="button" className="refresh-button" onClick={() => void loadJobs()} disabled={loading}>
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
          <button type="button" className="primary-button" onClick={() => void handleRunDueJobs()} disabled={running}>
            {running ? 'Running...' : 'Run Due Jobs'}
          </button>
        </div>
      </header>

      {error && <p className="panel-error">{error}</p>}
      {successMessage && <p className="panel-success">{successMessage}</p>}

      <div className="scheduler-panel__info">
        <p className="text-sm text-indigo-200/80 mb-4 p-3 rounded-lg bg-indigo-900/20 border border-indigo-500/20">
          <strong>💡 How it works:</strong> Create scheduled jobs that run automatically at specified intervals. 
          Jobs can launch products, run revenue cycles, execute affiliate campaigns, and more. 
          Use interval (seconds), cron (time-based), or once (single execution) scheduling.
        </p>
      </div>

      <section className="scheduler-form">
        <form onSubmit={handleCreateJob} className="scheduler-form__grid">
          <label>
            Job ID (optional)
            <input value={form.jobId} onChange={handleChange('jobId')} placeholder="auto-generated if blank" />
          </label>

          <label>
            Handler
            <select value={form.handler} onChange={handleChange('handler')}>
              {handlerPresets.map((preset) => (
                <option key={preset.value} value={preset.value}>
                  {preset.label}
                </option>
              ))}
            </select>
          </label>

          <label>
            Schedule Type
            <select value={form.scheduleType} onChange={handleChange('scheduleType')}>
              <option value="interval">Interval (seconds)</option>
              <option value="cron">Cron (minute hour *)</option>
              <option value="once">Once (ISO timestamp)</option>
            </select>
          </label>

          <label>
            Schedule Value
            <input value={form.scheduleValue} onChange={handleChange('scheduleValue')} placeholder="e.g. 86400" required />
          </label>

          <label>
            Start At (optional ISO)
            <input value={form.startAt} onChange={handleChange('startAt')} placeholder="2025-01-01T08:00:00" />
          </label>

          <label className="scheduler-form__payload">
            Payload (JSON)
            <textarea value={form.payload} onChange={handleChange('payload')} rows={6} />
          </label>

          <button type="submit" className="primary-button" disabled={creating}>
            {creating ? 'Saving...' : 'Save Job'}
          </button>
        </form>
      </section>

      <section className="scheduler-jobs">
        <header>
          <h4>Scheduled Jobs</h4>
        </header>
        {jobs.length === 0 ? (
          <p className="panel-empty">No jobs scheduled yet. Create one using the form above.</p>
        ) : (
          <div className="scheduler-table">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Handler</th>
                  <th>Schedule</th>
                  <th>Next Run</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {displayJobs.map((job) => (
                  <tr key={job.id}>
                    <td>{job.id}</td>
                    <td>{job.handler}</td>
                    <td>
                      <span className="badge">
                        {job.schedule_type} • {job.schedule_value}
                      </span>
                    </td>
                    <td>{new Date(job.next_run).toLocaleString()}</td>
                    <td>{job.status}</td>
                    <td className="scheduler-table__actions">
                      <button type="button" className="refresh-button" onClick={() => void handleRunJob(job.id)} disabled={running}>
                        Run
                      </button>
                      <button type="button" className="refresh-button" onClick={() => void handleDeleteJob(job.id)}>
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
};
