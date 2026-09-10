import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/Card';
import { StatusBadge } from '../components/ui/StatusBadge';
import { fetchServiceRequests, fetchWorkflowByRequest } from '../services/api';
import { ChevronDown, ChevronUp, Clock, CheckCircle2, XCircle, RefreshCw, Loader2, CircleDashed } from 'lucide-react';

const STEP_ICONS = {
  pending: <CircleDashed size={16} className="text-muted" />,
  running: <Loader2 size={16} className="text-accent spin" />,
  success: <CheckCircle2 size={16} className="text-success" />,
  failed: <XCircle size={16} className="text-error" />,
  retrying: <RefreshCw size={16} className="text-warning" />,
};

const STEP_LABELS = {
  identity: 'Identity Verification',
  property: 'Property Registry',
  municipality: 'Municipality Records',
  tax: 'Tax Department',
};

const WorkflowTimeline = ({ requestId }) => {
  const [workflow, setWorkflow] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const data = await fetchWorkflowByRequest(requestId);
        if (active) setWorkflow(data);
      } catch {
        if (active) setWorkflow(null);
      } finally {
        if (active) setLoading(false);
      }
    };
    load();

    // Poll while running
    const interval = setInterval(async () => {
      try {
        const data = await fetchWorkflowByRequest(requestId);
        if (active) {
          setWorkflow(data);
          if (data && !['pending', 'running'].includes(data.status)) {
            clearInterval(interval);
          }
        }
      } catch { /* ignore */ }
    }, 3000);

    return () => { active = false; clearInterval(interval); };
  }, [requestId]);

  if (loading) return <div className="text-muted text-sm" style={{ padding: '1rem 0' }}>Loading workflow...</div>;
  if (!workflow) return <div className="text-muted text-sm" style={{ padding: '1rem 0' }}>No workflow found</div>;

  return (
    <div className="workflow-timeline-inline fade-in" style={{ marginTop: '0.75rem' }}>
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xs text-muted">Workflow:</span>
        <StatusBadge status={workflow.status} />
        <span className="text-xs font-mono text-muted">{workflow.workflow_id}</span>
      </div>
      <div className="step-pipeline">
        {workflow.steps.map((step, idx) => (
          <div key={idx} className="pipeline-step">
            <div className="pipeline-step-header">
              {STEP_ICONS[step.status] || STEP_ICONS.pending}
              <span className="text-sm font-medium">{STEP_LABELS[step.step_name] || step.step_name}</span>
              <StatusBadge status={step.status} className="text-xs" />
            </div>
            {step.attempt_count > 1 && (
              <span className="text-xs text-warning" style={{ marginLeft: '2rem' }}>
                Attempt {step.attempt_count}/{step.max_retries}
              </span>
            )}
            {step.error_message && (
              <span className="text-xs text-error" style={{ marginLeft: '2rem', display: 'block' }}>
                {step.error_message}
              </span>
            )}
            {step.duration_ms != null && (
              <span className="text-xs text-muted" style={{ marginLeft: '2rem' }}>
                {step.duration_ms}ms
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export const AppTracking = () => {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedRow, setExpandedRow] = useState(null);
  const [search, setSearch] = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        const data = await fetchServiceRequests();
        setApplications(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, []);

  const filtered = applications.filter(app =>
    app.request_id.toLowerCase().includes(search.toLowerCase()) ||
    app.citizen_id.toLowerCase().includes(search.toLowerCase()) ||
    app.service_type.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="flex-col gap-6 flex fade-in">
      <div className="flex justify-between items-center">
        <p className="text-muted">Track and manage citizen service applications across all departments.</p>
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Search applications..."
            className="form-input py-2 text-sm w-64"
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
      </div>

      <Card>
        {loading ? (
          <div className="flex items-center justify-center gap-2" style={{ padding: '3rem 0' }}>
            <Loader2 size={20} className="spin text-accent" />
            <span className="text-muted">Loading applications...</span>
          </div>
        ) : error ? (
          <div className="text-error text-sm" style={{ padding: '2rem', textAlign: 'center' }}>{error}</div>
        ) : filtered.length === 0 ? (
          <div className="empty-state">
            <p>No applications found. Submit a service request to get started.</p>
          </div>
        ) : (
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Request ID</th>
                  <th>Type</th>
                  <th>Citizen ID</th>
                  <th>Created</th>
                  <th>Status</th>
                  <th>Workflow</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(app => (
                  <React.Fragment key={app.request_id}>
                    <tr
                      onClick={() => setExpandedRow(expandedRow === app.request_id ? null : app.request_id)}
                      style={{ cursor: 'pointer' }}
                    >
                      <td className="font-mono text-xs">{app.request_id}</td>
                      <td className="font-medium">{app.service_type.replace(/_/g, ' ')}</td>
                      <td className="text-muted text-sm">{app.citizen_id}</td>
                      <td className="text-muted text-sm">{new Date(app.created_at).toLocaleString()}</td>
                      <td><StatusBadge status={app.status} /></td>
                      <td>
                        {app.workflow_id
                          ? <span className="font-mono text-xs text-accent">{app.workflow_id}</span>
                          : <span className="text-muted text-xs">—</span>
                        }
                      </td>
                      <td>
                        {app.workflow_id && (
                          expandedRow === app.request_id
                            ? <ChevronUp size={16} className="text-muted" />
                            : <ChevronDown size={16} className="text-muted" />
                        )}
                      </td>
                    </tr>
                    {expandedRow === app.request_id && app.workflow_id && (
                      <tr>
                        <td colSpan={7} style={{ background: 'var(--surface-subtle)', borderTop: 'none' }}>
                          <WorkflowTimeline requestId={app.request_id} />
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
};
