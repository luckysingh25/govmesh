import React, { useState, useEffect, useCallback } from 'react';
import { Card } from '../components/ui/Card';
import { StatusBadge } from '../components/ui/StatusBadge';
import { fetchWorkflowByRequest, fetchUnifiedTimeline } from '../services/api';
import {
  CheckCircle2, CircleDashed, Clock, XCircle, RefreshCw,
  Loader2, Search, ArrowRight, Shield, Server, FileText, Activity, GitMerge
} from 'lucide-react';

const STEP_META = {
  identity: {
    label: 'Identity Verification',
    protocol: 'REST API',
    icon: Shield,
    description: 'Verifies citizen identity via the national ID database.',
  },
  property: {
    label: 'Property Registry',
    protocol: 'SOAP/XML',
    icon: Server,
    description: 'Fetches property ownership records from the land registry.',
  },
  municipality: {
    label: 'Municipality Records',
    protocol: 'API-Key REST',
    icon: FileText,
    description: 'Retrieves municipal residency and ward information.',
  },
  tax: {
    label: 'Tax Department',
    protocol: 'Async Polling',
    icon: Clock,
    description: 'Queries tax compliance status and outstanding amounts.',
  },
};

const STATUS_CONFIG = {
  pending: { icon: CircleDashed, color: 'var(--text-secondary)', borderColor: 'var(--border)' },
  running: { icon: Loader2, color: 'var(--accent)', borderColor: 'var(--accent)', animate: true },
  success: { icon: CheckCircle2, color: 'var(--success)', borderColor: 'var(--success)' },
  failed: { icon: XCircle, color: 'var(--error)', borderColor: 'var(--error)' },
  retrying: { icon: RefreshCw, color: 'var(--warning)', borderColor: 'var(--warning)', animate: true },
};

const StepCard = ({ step }) => {
  const meta = STEP_META[step.step_name] || { label: step.step_name, protocol: 'Unknown', icon: Server, description: '' };
  const cfg = STATUS_CONFIG[step.status] || STATUS_CONFIG.pending;
  const IconComponent = cfg.icon;
  const StepIcon = meta.icon;

  return (
    <div
      className="card card-hover"
      style={{
        borderLeft: `3px solid ${cfg.borderColor}`,
        transition: 'all 0.3s ease',
      }}
    >
      <div className="flex items-center gap-3 mb-3">
        <div
          style={{
            width: 36, height: 36, borderRadius: '50%',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            background: `${cfg.borderColor}15`,
          }}
        >
          <IconComponent size={18} style={{ color: cfg.color }} className={cfg.animate ? 'spin' : ''} />
        </div>
        <div style={{ flex: 1 }}>
          <div className="flex items-center gap-2">
            <StepIcon size={14} className="text-muted" />
            <span className="font-medium">{meta.label}</span>
          </div>
          <div className="text-xs text-muted">{meta.protocol}</div>
        </div>
        <StatusBadge status={step.status} />
      </div>

      <p className="text-xs text-muted mb-3">{meta.description}</p>

      <div className="flex gap-4 flex-wrap text-xs">
        {step.attempt_count > 0 && (
          <span className="text-muted">
            Attempt <strong style={{ color: step.attempt_count > 1 ? 'var(--warning)' : 'var(--text-primary)' }}>
              {step.attempt_count}
            </strong>/{step.max_retries}
          </span>
        )}
        {step.duration_ms != null && (
          <span className="text-muted">
            Duration: <strong className="text-primary">{step.duration_ms}ms</strong>
          </span>
        )}
        {step.started_at && (
          <span className="text-muted">
            Started: {new Date(step.started_at).toLocaleTimeString()}
          </span>
        )}
        {step.completed_at && (
          <span className="text-muted">
            Completed: {new Date(step.completed_at).toLocaleTimeString()}
          </span>
        )}
      </div>

      {step.error_message && (
        <div
          className="mt-2 text-xs"
          style={{
            padding: '0.5rem 0.75rem',
            background: 'var(--error-bg)',
            border: '1px solid rgba(239, 68, 68, 0.2)',
            borderRadius: 6,
            color: 'var(--error)',
          }}
        >
          {step.error_message}
        </div>
      )}
    </div>
  );
};

export const Workflow = () => {
  const [requestId, setRequestId] = useState('');
  const [workflow, setWorkflow] = useState(null);
  const [timeline, setTimeline] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const lookupWorkflow = useCallback(async () => {
    if (!requestId.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const wf = await fetchWorkflowByRequest(requestId.trim());
      if (!wf) {
        setError('No workflow found for this request ID.');
        setWorkflow(null);
        setTimeline(null);
        return;
      }
      setWorkflow(wf);

      const tl = await fetchUnifiedTimeline(requestId.trim());
      setTimeline(tl);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [requestId]);

  // Auto-poll while workflow is active
  useEffect(() => {
    if (!workflow || !['pending', 'running'].includes(workflow.status)) return;

    const interval = setInterval(async () => {
      try {
        const wf = await fetchWorkflowByRequest(requestId.trim());
        if (wf) {
          setWorkflow(wf);
          const tl = await fetchUnifiedTimeline(requestId.trim());
          setTimeline(tl);
          if (!['pending', 'running'].includes(wf.status)) {
            clearInterval(interval);
          }
        }
      } catch { /* ignore */ }
    }, 3000);

    return () => clearInterval(interval);
  }, [workflow?.status, requestId]);

  const isActive = workflow && ['pending', 'running'].includes(workflow.status);

  return (
    <div className="flex-col gap-6 flex fade-in">
      {/* Search bar */}
      <Card title="Workflow Lookup">
        <p className="text-muted text-sm mb-4">
          Enter a service request ID to view its workflow pipeline and live step statuses.
        </p>
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="e.g. REQ-A1B2C3D4"
            className="form-input text-sm"
            value={requestId}
            onChange={e => setRequestId(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && lookupWorkflow()}
            style={{ maxWidth: 320 }}
          />
          <button
            className="btn btn-primary"
            onClick={lookupWorkflow}
            disabled={loading || !requestId.trim()}
          >
            {loading ? <Loader2 size={16} className="spin" /> : <Search size={16} />}
            Lookup
          </button>
        </div>
        {error && <p className="text-error text-sm mt-2">{error}</p>}
      </Card>

      {/* Workflow header */}
      {workflow && (
        <Card>
          <div className="flex items-center justify-between mb-4">
            <div>
              <div className="flex items-center gap-3">
                <h3 className="card-title" style={{ marginBottom: 0 }}>
                  Business Registration Pipeline
                </h3>
                <StatusBadge status={workflow.status} />
                {isActive && (
                  <span className="text-xs text-accent flex items-center gap-1">
                    <Loader2 size={12} className="spin" /> Live
                  </span>
                )}
              </div>
              <p className="text-muted text-sm mt-1">
                Workflow <span className="font-mono">{workflow.workflow_id}</span>
                {' · '}Request <span className="font-mono">{workflow.service_request_id}</span>
                {' · '}Citizen <span className="font-mono">{workflow.citizen_id}</span>
              </p>
            </div>
            <div className="text-xs text-muted text-right">
              <div>Created: {new Date(workflow.created_at).toLocaleString()}</div>
              {workflow.completed_at && (
                <div>Completed: {new Date(workflow.completed_at).toLocaleString()}</div>
              )}
            </div>
          </div>

          {/* Progress bar */}
          <div style={{ display: 'flex', gap: 4, marginBottom: '1.5rem' }}>
            {workflow.steps.map((step, idx) => {
              const color =
                step.status === 'success' ? 'var(--success)' :
                step.status === 'failed' ? 'var(--error)' :
                step.status === 'running' ? 'var(--accent)' :
                step.status === 'retrying' ? 'var(--warning)' :
                'var(--border)';
              return (
                <div
                  key={idx}
                  style={{
                    flex: 1, height: 6, borderRadius: 3,
                    background: color,
                    transition: 'background 0.5s ease',
                  }}
                />
              );
            })}
          </div>

          {/* Step pipeline */}
          <div className="dept-grid">
            {workflow.steps.map((step, idx) => (
              <React.Fragment key={idx}>
                <StepCard step={step} />
              </React.Fragment>
            ))}
          </div>
        </Card>
      )}

      {timeline && timeline.timeline && (
        <Card title="Unified Application Timeline">
          <p className="text-sm text-muted mb-4">Combines workflow execution, data lineage mappings, and audit events.</p>
          <div className="timeline">
            {timeline.timeline.map((entry, idx) => {
              if (entry.type === 'workflow_step') {
                const step = entry.data;
                const meta = STEP_META[step.step_name] || { label: step.step_name };
                const cfg = STATUS_CONFIG[step.status] || STATUS_CONFIG.pending;
                const dotClass = step.status === 'success' ? 'success' : step.status === 'failed' ? 'error' : '';
                const IconComponent = cfg.icon;

                return (
                  <div className="timeline-item" key={idx}>
                    <div className={`timeline-dot ${dotClass}`}>
                      <IconComponent size={12} style={{ color: cfg.color }} className={cfg.animate ? 'spin' : ''} />
                    </div>
                    <div className="ml-8">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-medium text-sm">Workflow: {meta.label}</h4>
                        <StatusBadge status={step.status} />
                      </div>
                      <div className="flex gap-4 text-xs text-muted flex-wrap">
                        {step.attempt_count > 0 && <span>Attempts: {step.attempt_count}</span>}
                        {step.duration_ms != null && <span>Duration: {step.duration_ms}ms</span>}
                        {entry.timestamp && <span>Time: {new Date(entry.timestamp).toLocaleTimeString()}</span>}
                      </div>
                      {step.error_message && (
                        <div className="text-xs text-error mt-1">{step.error_message}</div>
                      )}
                    </div>
                  </div>
                );
              } else if (entry.type === 'audit_event') {
                const log = entry.data;
                const isSuccess = log.outcome === 'success' || log.outcome === 'allow';
                return (
                  <div className="timeline-item" key={idx}>
                    <div className={`timeline-dot ${isSuccess ? 'success' : 'error'}`} style={{ background: isSuccess ? 'var(--success-bg)' : 'var(--error-bg)' }}>
                      <Activity size={12} style={{ color: isSuccess ? 'var(--success)' : 'var(--error)' }} />
                    </div>
                    <div className="ml-8">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-medium text-sm text-muted">Audit: {log.event_type}</h4>
                      </div>
                      <div className="text-xs text-muted">
                        <span className="font-medium">{log.actor}</span> → {log.target}
                      </div>
                      <div className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>
                        {log.detail}
                      </div>
                    </div>
                  </div>
                );
              } else if (entry.type === 'data_lineage') {
                const lin = entry.data;
                return (
                  <div className="timeline-item" key={idx}>
                    <div className="timeline-dot" style={{ background: 'rgba(99, 102, 241, 0.1)', borderColor: 'var(--accent)' }}>
                      <GitMerge size={12} className="text-accent" />
                    </div>
                    <div className="ml-8">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-medium text-sm text-accent">Data Mapped: {lin.destination_field}</h4>
                      </div>
                      <div className="text-xs text-muted font-mono flex items-center gap-2 mt-1">
                        <span>{lin.source_system}.{lin.source_field}</span>
                        <ArrowRight size={12} />
                        <span>{lin.destination_system}.{lin.destination_field}</span>
                      </div>
                      {lin.transformation && (
                        <div className="text-xs text-muted mt-1 italic">Transformation: {lin.transformation}</div>
                      )}
                    </div>
                  </div>
                );
              }
              return null;
            })}
          </div>
        </Card>
      )}

      {/* Empty state */}
      {!workflow && !loading && (
        <Card title="GovMesh Orchestration Pipeline">
          <p className="text-muted mb-6" style={{ maxWidth: 600 }}>
            GovMesh orchestrates synthetic citizen requests across multiple department simulators
            sequentially, with explicit resume or targeted retry controls after a failure.
          </p>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
            {['Identity', 'Property', 'Municipality', 'Tax'].map((dept, idx) => (
              <React.Fragment key={dept}>
                <div
                  className="card"
                  style={{
                    padding: '0.75rem 1.25rem',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    fontSize: '0.875rem',
                    fontWeight: 500,
                  }}
                >
                  <Server size={14} className="text-accent" />
                  {dept}
                </div>
                {idx < 3 && <ArrowRight size={16} className="text-muted" />}
              </React.Fragment>
            ))}
          </div>
          <p className="text-muted text-xs mt-4">
            Enter a request ID above to see the live workflow execution for that application.
          </p>
        </Card>
      )}
    </div>
  );
};
