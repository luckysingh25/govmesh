import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/Card';
import { StatusBadge } from '../components/ui/StatusBadge';
import {
  fetchSchemas, fetchSuggestions, approveSuggestion,
  rejectSuggestion, fetchImpactAnalysis, triggerDemoScenario
} from '../services/api';
import { BrainCircuit, Play, Check, X, AlertTriangle, Layers, GitMerge } from 'lucide-react';

export const Intelligence = () => {
  const [schemas, setSchemas] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [approvedSuggestions, setApprovedSuggestions] = useState([]);
  const [activeTab, setActiveTab] = useState('pending');
  const [impacts, setImpacts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [demoLoading, setDemoLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(null);
  const [toastMessage, setToastMessage] = useState(null);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const loadData = async () => {
    setLoading(true);
    try {
      const [sData, sugData, appData, iData] = await Promise.all([
        fetchSchemas(),
        fetchSuggestions('pending'),
        fetchSuggestions('approved'),
        fetchImpactAnalysis()
      ]);
      setSchemas(sData);
      setSuggestions(sugData);
      setApprovedSuggestions(appData);
      setImpacts(iData);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleTriggerDemo = async () => {
    setDemoLoading(true);
    try {
      await triggerDemoScenario();
      showToast('Demo scenario triggered successfully!');
      await loadData();
    } catch (e) {
      console.error(e);
      showToast('Failed to trigger demo scenario.');
    } finally {
      setDemoLoading(false);
    }
  };

  const handleApprove = async (id) => {
    const item = suggestions.find(s => s.id === id);
    setActionLoading(id);
    // Optimistic UI update
    setSuggestions(prev => prev.filter(s => s.id !== id));
    if (item) {
      setApprovedSuggestions(prev => [{ ...item, status: 'approved' }, ...prev]);
    }
    showToast(`Approved mapping for ${item?.source_field?.field_name || 'field'}`);

    try {
      await approveSuggestion(id);
      loadData();
    } catch (e) {
      console.error(e);
      showToast('Error approving suggestion.');
      loadData();
    } finally {
      setActionLoading(null);
    }
  };

  const handleReject = async (id) => {
    const item = suggestions.find(s => s.id === id);
    setActionLoading(id);
    // Optimistic UI update
    setSuggestions(prev => prev.filter(s => s.id !== id));
    showToast(`Rejected mapping for ${item?.source_field?.field_name || 'field'}`);

    try {
      await rejectSuggestion(id);
      loadData();
    } catch (e) {
      console.error(e);
      showToast('Error rejecting suggestion.');
      loadData();
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <div className="flex-col gap-6 flex fade-in">
      <div className="flex justify-between items-center mb-2">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2 mb-2">
            <BrainCircuit className="text-accent" /> Interoperability Intelligence
          </h1>
          <p className="text-muted">Rule-based schema versioning, field mapping suggestions, and impact analysis.</p>
        </div>
        <button
          className="btn btn-primary"
          onClick={handleTriggerDemo}
          disabled={demoLoading}
        >
          {demoLoading ? <span className="spin">↻</span> : <Play size={16} />}
          Trigger Upgrade Demo
        </button>
      </div>

      {toastMessage && (
        <div style={{
          padding: '0.75rem 1rem',
          background: 'rgba(56, 189, 248, 0.15)',
          border: '1px solid rgba(56, 189, 248, 0.4)',
          borderRadius: 8,
          color: 'var(--text-primary)',
          fontSize: '0.875rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          <Check size={16} className="text-accent" />
          <span>{toastMessage}</span>
        </div>
      )}

      <div className="dept-grid">
        <Card title="Mapping Approvals" className="flex-1">
          {/* Tabs for Pending vs Approved */}
          <div className="flex gap-2 mb-4 border-b border-border pb-2">
            <button
              className={`btn btn-sm ${activeTab === 'pending' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ padding: '0.25rem 0.75rem', fontSize: '0.75rem' }}
              onClick={() => setActiveTab('pending')}
            >
              Pending ({suggestions.length})
            </button>
            <button
              className={`btn btn-sm ${activeTab === 'approved' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ padding: '0.25rem 0.75rem', fontSize: '0.75rem' }}
              onClick={() => setActiveTab('approved')}
            >
              Approved ({approvedSuggestions.length})
            </button>
          </div>

          <div className="flex flex-col gap-4 mt-2">
            {activeTab === 'pending' ? (
              suggestions.length === 0 ? (
                <p className="text-muted text-sm text-center py-4">No pending suggestions. All mappings are reviewed!</p>
              ) : (
                suggestions.map(sug => (
                  <div key={sug.id} style={{ padding: '1rem', background: 'rgba(15,23,42,0.4)', borderRadius: 8, border: '1px solid var(--border)' }}>
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <div className="text-xs text-muted mb-1 font-mono">ID: {sug.source_field_id}</div>
                        <div className="font-medium flex items-center gap-2">
                          {sug.source_field?.field_name || `Field ${sug.source_field_id}`}
                          <GitMerge size={14} className="text-muted" />
                          <span className="text-accent">{sug.target_field}</span>
                        </div>
                      </div>
                      <StatusBadge status={sug.mapping_type} />
                    </div>
                    
                    <div className="flex items-center justify-between mt-4">
                      <div className="text-xs">
                        Confidence: <strong className={sug.confidence_score > 0.8 ? 'text-success' : 'text-warning'}>
                          {(sug.confidence_score * 100).toFixed(0)}%
                        </strong>
                      </div>
                      <div className="flex gap-2">
                        <button
                          className="btn btn-secondary text-error"
                          style={{ padding: '0.25rem 0.5rem' }}
                          disabled={actionLoading === sug.id}
                          onClick={() => handleReject(sug.id)}
                        >
                          <X size={14} /> Reject
                        </button>
                        <button
                          className="btn btn-primary"
                          style={{ padding: '0.25rem 0.5rem' }}
                          disabled={actionLoading === sug.id}
                          onClick={() => handleApprove(sug.id)}
                        >
                          {actionLoading === sug.id ? <span className="spin">↻</span> : <Check size={14} />} Approve
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              )
            ) : (
              approvedSuggestions.length === 0 ? (
                <p className="text-muted text-sm text-center py-4">No approved mappings yet.</p>
              ) : (
                approvedSuggestions.map(sug => (
                  <div key={sug.id} style={{ padding: '1rem', background: 'rgba(34, 197, 94, 0.05)', borderRadius: 8, border: '1px solid rgba(34, 197, 94, 0.2)' }}>
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <div className="text-xs text-muted mb-1 font-mono">ID: {sug.source_field_id}</div>
                        <div className="font-medium flex items-center gap-2">
                          {sug.source_field?.field_name || `Field ${sug.source_field_id}`}
                          <GitMerge size={14} className="text-muted" />
                          <span className="text-accent">{sug.target_field}</span>
                        </div>
                      </div>
                      <span className="badge badge-success flex items-center gap-1" style={{ fontSize: '0.7rem', padding: '0.2rem 0.5rem' }}>
                        <Check size={12} /> APPROVED
                      </span>
                    </div>
                    <div className="text-xs text-muted mt-2">
                      Confidence: <strong>{(sug.confidence_score * 100).toFixed(0)}%</strong> • Type: <span className="font-mono">{sug.mapping_type}</span>
                    </div>
                  </div>
                ))
              )
            )}
          </div>
        </Card>

        <Card title="Impact Analysis" className="flex-1">
          <div className="flex flex-col gap-4 mt-2">
            {impacts.length === 0 ? (
              <p className="text-muted text-sm text-center py-4">No breaking changes detected.</p>
            ) : (
              impacts.map(imp => (
                <div key={imp.id} style={{ padding: '1rem', background: 'rgba(239, 68, 68, 0.05)', borderRadius: 8, border: '1px solid rgba(239, 68, 68, 0.2)' }}>
                  <div className="flex justify-between items-center mb-3">
                    <h4 className="font-medium text-error flex items-center gap-2">
                      <AlertTriangle size={16} /> Schema Version {imp.new_version}
                    </h4>
                    <span className="text-xs font-mono">{imp.system_name}</span>
                  </div>
                  <p className="text-sm mb-3">{imp.analysis_result?.impact_summary}</p>
                  
                  {imp.analysis_result?.affected_workflows?.map((wf, idx) => (
                    <div key={idx} className="text-xs p-2 mt-2 rounded bg-slate-800/50">
                      <strong>Affected:</strong> {wf.workflow} ({wf.step})<br/>
                      <span className="text-muted">{wf.detail}</span>
                    </div>
                  ))}
                </div>
              ))
            )}
          </div>
        </Card>
      </div>

      <Card title="Ingested Schemas">
        <div className="table-container mt-4">
          <table className="table">
            <thead>
              <tr>
                <th>System Name</th>
                <th>Version</th>
                <th>Status</th>
                <th>Fields</th>
                <th>Ingested At</th>
              </tr>
            </thead>
            <tbody>
              {schemas.length === 0 && (
                <tr><td colSpan="5" className="text-center py-4 text-muted">No schemas ingested yet.</td></tr>
              )}
              {schemas.map(s => (
                <tr key={s.id}>
                  <td className="font-medium">{s.system_name}</td>
                  <td><span className="text-xs font-mono">v{s.version}</span></td>
                  <td><StatusBadge status={s.status} /></td>
                  <td className="text-sm text-muted">{s.fields?.length || 0} fields</td>
                  <td className="text-sm text-muted">{new Date(s.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};
