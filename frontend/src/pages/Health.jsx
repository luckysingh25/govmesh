import React, { useEffect, useState } from 'react';
import { Card } from '../components/ui/Card';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Loader } from '../components/ui/Loader';
import { checkHealth } from '../services/api';
import { Activity, Server, Database } from 'lucide-react';

export const Health = () => {
  const [health, setHealth] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkHealth()
      .then(setHealth)
      .catch(err => setError(err.message))
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) return <Loader text="Checking system health..." />;
  if (error) return <div className="error-text">Failed to fetch health status: {error}</div>;
  if (!health) return null;

  const isOk = health.status === 'ok';

  return (
    <div className="flex-col gap-6 flex fade-in">
      <Card>
        <div className="flex items-center gap-6">
          <div className={`p-4 rounded-full ${isOk ? 'bg-success/20 text-success' : 'bg-error/20 text-error'}`}>
            <Activity size={32} />
          </div>
          <div>
            <h2 className="text-2xl font-bold mb-1">GovMesh API Core</h2>
            <div className="flex items-center gap-4 text-muted">
              <StatusBadge status={health.status} />
              <span>Version {health.service}</span>
              <span>Env: {health.environment}</span>
            </div>
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card title="Database (PostgreSQL)" action={<StatusBadge status={health.database.status} />}>
          <div className="flex items-start gap-4">
            <Database className="text-blue-400 mt-1" />
            <div className="w-full">
              <div className="flex justify-between mb-2">
                <span className="text-muted text-sm">Response Time</span>
                <span className="font-mono">{health.database.response_time_ms} ms</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2">
                <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${Math.min(100, health.database.response_time_ms)}%` }}></div>
              </div>
            </div>
          </div>
        </Card>
        
        <Card title="Cache (Redis)" action={<StatusBadge status={health.redis.status} />}>
          <div className="flex items-start gap-4">
            <Server className="text-red-400 mt-1" />
            <div className="w-full">
              <div className="flex justify-between mb-2">
                <span className="text-muted text-sm">Response Time</span>
                <span className="font-mono">{health.redis.response_time_ms} ms</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2">
                <div className="bg-red-500 h-2 rounded-full" style={{ width: `${Math.min(100, health.redis.response_time_ms)}%` }}></div>
              </div>
            </div>
          </div>
        </Card>
      </div>
      
      <Card title="Raw Diagnostics">
        <pre className="bg-slate-900/80 p-4 rounded-lg w-full text-sm font-mono text-muted overflow-auto">
          {JSON.stringify(health, null, 2)}
        </pre>
      </Card>
    </div>
  );
};
