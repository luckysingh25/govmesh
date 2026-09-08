import React from 'react';
import { Card } from '../components/ui/Card';
import { StatusBadge } from '../components/ui/StatusBadge';

export const AuditActivity = () => {
  const auditLogs = [
    { id: 'EVT-9001', time: '10 mins ago', type: 'Policy Decision', actor: 'System Engine', target: 'CIT-1001', detail: 'Consent verified — access allowed', outcome: 'allow' },
    { id: 'EVT-9000', time: '10 mins ago', type: 'Consent Granted', actor: 'Citizen (CIT-1001)', target: 'GovMesh Core', detail: 'Granted access to Identity, Property, Tax, Municipality', outcome: 'success' },
    { id: 'EVT-8999', time: '45 mins ago', type: 'Policy Decision', actor: 'System Engine', target: 'CIT-4592', detail: 'No active consent found', outcome: 'deny' },
    { id: 'EVT-8998', time: '2 hours ago', type: 'System Error', actor: 'Municipality Connector', target: 'Legacy DB', detail: 'Connection timeout after 5000ms', outcome: 'error' },
    { id: 'EVT-8997', time: '3 hours ago', type: 'Consent Revoked', actor: 'Citizen (CIT-3301)', target: 'GovMesh Core', detail: 'Revoked access manually via portal', outcome: 'success' },
  ];

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
                <th>Event ID</th>
                <th>Time</th>
                <th>Type</th>
                <th>Actor</th>
                <th>Target</th>
                <th>Detail</th>
                <th>Outcome</th>
              </tr>
            </thead>
            <tbody>
              {auditLogs.map(log => (
                <tr key={log.id}>
                  <td className="font-mono text-xs">{log.id}</td>
                  <td className="text-muted text-sm">{log.time}</td>
                  <td className="font-medium">{log.type}</td>
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
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};
