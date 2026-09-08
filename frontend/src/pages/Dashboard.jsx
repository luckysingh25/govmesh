import React from 'react';
import { Card } from '../components/ui/Card';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Activity, Users, CheckCircle, Clock } from 'lucide-react';

export const Dashboard = () => {
  return (
    <div className="flex-col gap-6 flex fade-in">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-500/10 rounded-lg text-blue-400"><Activity size={24} /></div>
            <div>
              <div className="text-muted text-sm">Total Requests Today</div>
              <div className="text-2xl font-bold">1,248</div>
            </div>
          </div>
        </Card>
        <Card>
          <div className="flex items-center gap-4">
            <div className="p-3 bg-emerald-500/10 rounded-lg text-emerald-400"><CheckCircle size={24} /></div>
            <div>
              <div className="text-muted text-sm">Completed Instantly</div>
              <div className="text-2xl font-bold">94%</div>
            </div>
          </div>
        </Card>
        <Card>
          <div className="flex items-center gap-4">
            <div className="p-3 bg-amber-500/10 rounded-lg text-amber-400"><Clock size={24} /></div>
            <div>
              <div className="text-muted text-sm">Avg Processing Time</div>
              <div className="text-2xl font-bold">1.2s</div>
            </div>
          </div>
        </Card>
        <Card>
          <div className="flex items-center gap-4">
            <div className="p-3 bg-purple-500/10 rounded-lg text-purple-400"><Users size={24} /></div>
            <div>
              <div className="text-muted text-sm">Active Citizens</div>
              <div className="text-2xl font-bold">8,432</div>
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
                {[
                  { id: 'REQ-A72B91', svc: 'Business Registration', cit: 'Rajesh Kumar', status: 'completed' },
                  { id: 'REQ-C94X12', svc: 'Property Transfer', cit: 'Priya Sharma', status: 'processing' },
                  { id: 'REQ-F11L09', svc: 'Tax Clearance', cit: 'Amit Patel', status: 'completed' },
                  { id: 'REQ-M33Q88', svc: 'Trade License', cit: 'Neha Gupta', status: 'denied' },
                ].map(r => (
                  <tr key={r.id}>
                    <td className="font-mono text-xs">{r.id}</td>
                    <td>{r.svc}</td>
                    <td>{r.cit}</td>
                    <td><StatusBadge status={r.status} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        <Card title="System Status">
          <div className="flex-col gap-4 flex mt-2">
            {[
              { name: 'Identity Service', uptime: '99.99%', status: 'Operational' },
              { name: 'Property Reg.', uptime: '99.95%', status: 'Operational' },
              { name: 'Municipality', uptime: '98.50%', status: 'Degraded' },
              { name: 'Tax Dept.', uptime: '99.99%', status: 'Operational' },
            ].map(sys => (
              <div key={sys.name} className="flex items-center justify-between p-3 rounded-lg bg-slate-800/50 border border-slate-700/50">
                <div>
                  <div className="font-medium">{sys.name}</div>
                  <div className="text-xs text-muted">Uptime: {sys.uptime}</div>
                </div>
                <div className={`w-3 h-3 rounded-full ${sys.status === 'Operational' ? 'bg-emerald-500' : 'bg-amber-500'}`}></div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};
