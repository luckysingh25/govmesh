import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/Card';
import { StatusBadge } from '../components/ui/StatusBadge';
import { fetchGlobalAuditLogs } from '../services/api';
import { formatDistanceToNow } from 'date-fns';

export const AuditActivity = () => {
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadLogs = async () => {
      try {
        const data = await fetchGlobalAuditLogs(50);
        setAuditLogs(data);
      } catch (error) {
        console.error('Failed to load audit logs:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadLogs();
    
    // Auto-refresh every 10 seconds
    const interval = setInterval(loadLogs, 10000);
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="flex-col gap-6 flex fade-in">
      <Card title="Security & Audit Logs">
        <p className="text-muted mb-6 max-w-3xl">
          Immutable audit trail of all policy decisions, consent modifications, and system access events.
        </p>

        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Log ID</th>
                <th>Correlation ID</th>
                <th>Time</th>
                <th>Type</th>
                <th>Actor</th>
                <th>Target</th>
                <th>Detail</th>
                <th>Outcome</th>
              </tr>
            </thead>
            <tbody>
              {loading && auditLogs.length === 0 ? (
                <tr>
                  <td colSpan="8" className="text-center py-8 text-muted">Loading audit logs...</td>
                </tr>
              ) : (
                auditLogs.map(log => (
                  <tr key={log.id}>
                    <td className="font-mono text-xs text-muted">LOG-{log.id}</td>
                    <td className="font-mono text-xs">{log.correlation_id?.substring(0, 8) || '-'}</td>
                    <td className="text-muted text-sm">{formatDistanceToNow(new Date(log.created_at), { addSuffix: true })}</td>
                    <td className="font-medium">{log.event_type}</td>
                    <td className="text-sm">{log.actor}</td>
                    <td className="text-sm">{log.target}</td>
                    <td className="text-sm text-muted">{log.detail}</td>
                    <td>
                    <StatusBadge status={
                      log.outcome === 'allow' || log.outcome === 'success' ? 'success' :
                      log.outcome === 'deny' || log.outcome === 'error' ? 'error' : 'warning'
                    } />
                  </td>
                </tr>
              ))
            )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};
