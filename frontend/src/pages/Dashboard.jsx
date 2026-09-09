import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/Card';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Activity, Users, CheckCircle, Clock } from 'lucide-react';
import { fetchServiceRequests, fetchSystemsMonitoring } from '../services/api';

export const Dashboard = () => {
  const [requests, setRequests] = useState([]);
  const [systems, setSystems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [reqs, sys] = await Promise.all([
          fetchServiceRequests(),
          fetchSystemsMonitoring()
        ]);
        setRequests(reqs);
        setSystems(sys);
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
  const totalRequests = todaysRequests.length;
  const completedRequests = todaysRequests.filter(r => r.status === 'completed' || r.status === 'success');
  const completionRate = totalRequests > 0 ? Math.round((completedRequests.length / totalRequests) * 100) : 0;
  
  const durations = completedRequests.map(r => r.duration_ms).filter(Number.isFinite);
  const avgTimeStr = durations.length
    ? `${(durations.reduce((sum, value) => sum + value, 0) / durations.length / 1000).toFixed(2)}s`
    : 'Not available';

  // Active citizens: unique citizen IDs
  const activeCitizens = new Set(todaysRequests.map(r => r.citizen_id)).size;
  return (
    <div className="flex-col gap-6 flex fade-in">
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

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-4">
        <Card title="Recent Activity" className="lg:col-span-2">
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Request ID</th>
                  <th>Service</th>
                  <th>Citizen</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {loading && requests.length === 0 ? (
                  <tr><td colSpan="4" className="text-center py-4 text-muted">Loading activity...</td></tr>
                ) : requests.length === 0 ? (
                  <tr><td colSpan="4" className="text-center py-4 text-muted">No recent applications.</td></tr>
                ) : (
                  requests.slice(0, 5).map(r => (
                    <tr key={r.request_id}>
                      <td className="font-mono text-xs">{r.request_id}</td>
                      <td>{r.service_type.replace(/_/g, ' ')}</td>
                      <td>{r.citizen_id}</td>
                      <td><StatusBadge status={r.status} /></td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Card>

        <Card title="System Status">
          <div className="flex-col gap-4 flex mt-2">
            {loading && systems.length === 0 ? (
              <div className="text-center py-4 text-muted">Loading systems...</div>
            ) : systems.length === 0 ? (
              <div className="text-center py-4 text-muted">No systems registered.</div>
            ) : (
              systems.map(sys => (
                <div key={sys.name} className="flex items-center justify-between p-3 rounded-lg bg-slate-800/50 border border-slate-700/50">
                  <div>
                    <div className="font-medium">{sys.name}</div>
                    <div className="text-xs text-muted">Uptime: {sys.uptime_percent == null ? 'Not measured' : `${sys.uptime_percent}%`}</div>
                  </div>
                  <div className={`w-3 h-3 rounded-full ${sys.status === 'Online' ? 'bg-emerald-500' : sys.status === 'Offline' ? 'bg-error' : 'bg-amber-500'}`}></div>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};
