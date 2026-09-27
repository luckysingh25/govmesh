import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Activity, Users, CheckCircle, Clock, ShieldCheck, FileText, ArrowRight, BrainCircuit, Server, History } from 'lucide-react';
import { fetchRequestMetrics, fetchServiceRequests, fetchSystemsMonitoring } from '../services/api';
import { useAuth } from '../auth/AuthContext';

export const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [requests, setRequests] = useState([]);
  const [systems, setSystems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState(null);

  const isCitizen = user?.role === 'citizen';
  const isSteward = user?.role === 'data_steward';

  useEffect(() => {
    const loadData = async () => {
      try {
        const [reqs, sys, aggregate] = await Promise.all([
          fetchServiceRequests(),
          fetchSystemsMonitoring(),
          fetchRequestMetrics()
        ]);
        setRequests(reqs);
        setSystems(sys);
        setMetrics(aggregate);
      } catch (e) {
        console.error("Failed to load dashboard data", e);
      } finally {
        setLoading(false);
      }
    };
    
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  const today = new Date().toDateString();
  const todaysRequests = requests.filter(r => new Date(r.created_at).toDateString() === today);
  const totalRequests = metrics?.total_requests ?? todaysRequests.length;
  const completedRequests = todaysRequests.filter(r => r.status === 'completed' || r.status === 'success');
  const completionRate = metrics?.completion_rate ?? (totalRequests > 0 ? Math.round((completedRequests.length / totalRequests) * 100) : 0);
  
  const durations = completedRequests.map(r => r.duration_ms).filter(Number.isFinite);
  const avgTimeStr = metrics?.average_duration_ms != null ? `${(metrics.average_duration_ms / 1000).toFixed(2)}s` : durations.length
    ? `${(durations.reduce((sum, value) => sum + value, 0) / durations.length / 1000).toFixed(2)}s`
    : 'Not available';

  const activeCitizens = metrics?.active_citizens ?? new Set(todaysRequests.map(r => r.citizen_id)).size;

  // Filter personal requests for citizen
  const citizenRequests = isCitizen && user?.citizen_id
    ? requests.filter(r => r.citizen_id === user.citizen_id)
    : requests;

  return (
    <div className="flex-col gap-6 flex fade-in">
      {/* Role-Specific Hero Header */}
      {isCitizen ? (
        <div className="p-6 rounded-2xl bg-gradient-to-r from-blue-900/30 via-indigo-900/20 to-purple-900/20 border border-blue-500/20 relative overflow-hidden">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="px-2.5 py-0.5 rounded text-[11px] font-bold bg-blue-500/20 text-blue-400 border border-blue-500/30">
                  CITIZEN SERVICE PORTAL
                </span>
                <span className="text-xs text-[var(--text-muted)]">Aadhaar Linked: {user?.citizen_id || 'CIT-1001'}</span>
              </div>
              <h2 className="text-xl font-bold text-[var(--text-primary)]">
                Welcome, {user?.email}
              </h2>
              <p className="text-xs text-[var(--text-secondary)] mt-1">
                Secure cross-departmental service hub compliant with Digital Personal Data Protection (DPDP) Act 2023.
              </p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => navigate('/service-request')}
                className="btn btn-primary text-xs flex items-center gap-2"
              >
                <FileText size={15} /> Apply for Unified Service
              </button>
              <button
                onClick={() => navigate('/consent')}
                className="btn btn-secondary text-xs flex items-center gap-2"
              >
                <ShieldCheck size={15} /> Manage Consent
              </button>
            </div>
          </div>
        </div>
      ) : isSteward ? (
        <div className="p-6 rounded-2xl bg-gradient-to-r from-purple-900/30 via-indigo-900/20 to-blue-900/20 border border-purple-500/20 relative overflow-hidden">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="px-2.5 py-0.5 rounded text-[11px] font-bold bg-purple-500/20 text-purple-400 border border-purple-500/30">
                  DATA STEWARDSHIP & GOVERNANCE
                </span>
                <span className="text-xs text-[var(--text-muted)]">State Mesh Authority</span>
              </div>
              <h2 className="text-xl font-bold text-[var(--text-primary)]">
                Schema Evolution & Interoperability Center
              </h2>
              <p className="text-xs text-[var(--text-secondary)] mt-1">
                Govern cross-departmental schema drifts, approve semantic mappings, and audit immutable transaction lineage.
              </p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => navigate('/intelligence')}
                className="btn btn-primary text-xs flex items-center gap-2"
              >
                <BrainCircuit size={15} /> Schema Intelligence
              </button>
              <button
                onClick={() => navigate('/audit')}
                className="btn btn-secondary text-xs flex items-center gap-2"
              >
                <History size={15} /> Audit Ledger
              </button>
            </div>
          </div>
        </div>
      ) : null}

      {/* KPI Cards: Dynamic for Citizen vs Operations */}
      {isCitizen ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-500/10 rounded-lg text-blue-400"><FileText size={24} /></div>
              <div>
                <div className="text-muted text-sm">My Total Applications</div>
                <div className="text-2xl font-bold">{citizenRequests.length}</div>
              </div>
            </div>
          </Card>
          <Card>
            <div className="flex items-center gap-4">
              <div className="p-3 bg-emerald-500/10 rounded-lg text-emerald-400"><CheckCircle size={24} /></div>
              <div>
                <div className="text-muted text-sm">Completed Approvals</div>
                <div className="text-2xl font-bold">
                  {citizenRequests.filter(r => r.status === 'completed' || r.status === 'success').length}
                </div>
              </div>
            </div>
          </Card>
          <Card>
            <div className="flex items-center gap-4">
              <div className="p-3 bg-indigo-500/10 rounded-lg text-indigo-400"><ShieldCheck size={24} /></div>
              <div>
                <div className="text-muted text-sm">DPDP Statutory Rights</div>
                <div className="text-2xl font-bold text-emerald-400">Protected</div>
              </div>
            </div>
          </Card>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-500/10 rounded-lg text-blue-400"><Activity size={24} /></div>
              <div>
                <div className="text-muted text-sm">Requests Today</div>
                <div className="text-2xl font-bold">{totalRequests}</div>
              </div>
            </div>
          </Card>
          <Card>
            <div className="flex items-center gap-4">
              <div className="p-3 bg-emerald-500/10 rounded-lg text-emerald-400"><CheckCircle size={24} /></div>
              <div>
                <div className="text-muted text-sm">Completion Rate</div>
                <div className="text-2xl font-bold">{completionRate}%</div>
              </div>
            </div>
          </Card>
          <Card>
            <div className="flex items-center gap-4">
              <div className="p-3 bg-amber-500/10 rounded-lg text-amber-400"><Clock size={24} /></div>
              <div>
                <div className="text-muted text-sm">Avg Processing Time</div>
                <div className="text-2xl font-bold">{avgTimeStr}</div>
              </div>
            </div>
          </Card>
          <Card>
            <div className="flex items-center gap-4">
              <div className="p-3 bg-purple-500/10 rounded-lg text-purple-400"><Users size={24} /></div>
              <div>
                <div className="text-muted text-sm">Active Citizens</div>
                <div className="text-2xl font-bold">{activeCitizens}</div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card
          title={isCitizen ? "My Applications" : "Recent Interoperability Activity"}
          className="lg:col-span-2"
        >
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Request ID</th>
                  <th>Service</th>
                  {!isCitizen && <th>Citizen ID</th>}
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {loading && (isCitizen ? citizenRequests : requests).length === 0 ? (
                  <tr><td colSpan={isCitizen ? 4 : 5} className="text-center py-6 text-muted">Loading transactions...</td></tr>
                ) : (isCitizen ? citizenRequests : requests).length === 0 ? (
                  <tr>
                    <td colSpan={isCitizen ? 4 : 5} className="text-center py-6 text-muted">
                      {isCitizen
                        ? "You have not submitted any service applications yet."
                        : "No recent interoperability applications."}
                    </td>
                  </tr>
                ) : (
                  (isCitizen ? citizenRequests : requests).slice(0, 5).map(r => (
                    <tr key={r.request_id}>
                      <td className="font-mono text-xs font-semibold text-[var(--accent)]">{r.request_id}</td>
                      <td>{r.service_type?.replace(/_/g, ' ') || 'General Service'}</td>
                      {!isCitizen && <td className="font-mono text-xs">{r.citizen_id}</td>}
                      <td><StatusBadge status={r.status} /></td>
                      <td>
                        <button
                          onClick={() => navigate('/tracking')}
                          className="text-xs text-[var(--accent)] hover:underline flex items-center gap-1"
                        >
                          Track <ArrowRight size={12} />
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Card>

        {isCitizen ? (
          <Card title="DPDP Statutory Rights">
            <div className="flex flex-col gap-3 text-xs leading-relaxed text-[var(--text-secondary)]">
              <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                <strong>Right to Consent:</strong> No government department can access your data without your express, time-bounded statutory consent.
              </div>
              <div className="p-3 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-400">
                <strong>Right to Revoke:</strong> You can revoke consent at any time from the Consent Ledger. Revocations take effect immediately.
              </div>
              <div className="p-3 rounded-lg bg-[var(--surface-subtle)] border border-[var(--border)]">
                <strong>Purpose Limitation:</strong> Data retrieved is restricted to the specific service applied for and is not shared across unrelated silos.
              </div>
            </div>
          </Card>
        ) : (
          <Card title="Federated Nodes">
            <div className="flex-col gap-3 flex mt-1">
              {loading && systems.length === 0 ? (
                <div className="text-center py-4 text-muted">Loading department nodes...</div>
              ) : systems.length === 0 ? (
                <div className="text-center py-4 text-muted">No systems registered.</div>
              ) : (
                systems.map(sys => (
                  <div key={sys.name} className="flex items-center justify-between p-3 rounded-lg" style={{ background: 'var(--surface-subtle)', border: '1px solid var(--border)' }}>
                    <div>
                      <div className="font-medium text-xs text-[var(--text-primary)]">{sys.name}</div>
                      <div className="text-[11px] text-muted">
                        Protocol: <span className="font-mono text-[var(--text-primary)]">{sys.protocol || 'REST'}</span> · Uptime: {sys.uptime_percent == null ? '100%' : `${sys.uptime_percent}%`}
                      </div>
                    </div>
                    <div className={`w-2.5 h-2.5 rounded-full ${sys.status === 'Online' ? 'bg-emerald-500 shadow-sm shadow-emerald-500/50' : sys.status === 'Offline' ? 'bg-rose-500' : 'bg-amber-500'}`}></div>
                  </div>
                ))
              )}
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};
