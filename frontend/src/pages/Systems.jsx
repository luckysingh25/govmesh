import React from 'react';
import { Card } from '../components/ui/Card';
import { Server, Database, Globe, Lock } from 'lucide-react';

const SystemCard = ({ name, type, icon: Icon, status, uptime, latency, protocol }) => (
  <Card className="hover:border-accent/50 transition-colors">
    <div className="flex justify-between items-start mb-4">
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg bg-slate-800 ${status === 'Online' ? 'text-emerald-400' : 'text-amber-400'}`}>
          <Icon size={20} />
        </div>
        <div>
          <h3 className="font-semibold text-lg">{name}</h3>
          <span className="text-xs text-muted">{type}</span>
        </div>
      </div>
      <div className={`w-3 h-3 rounded-full ${status === 'Online' ? 'bg-emerald-500' : 'bg-amber-500'}`}></div>
    </div>
    
    <div className="grid grid-cols-2 gap-4 mt-6">
      <div>
        <div className="text-xs text-muted uppercase tracking-wider mb-1">Status</div>
        <div className={`font-medium ${status === 'Online' ? 'text-success' : 'text-warning'}`}>{status}</div>
      </div>
      <div>
        <div className="text-xs text-muted uppercase tracking-wider mb-1">Protocol</div>
        <div className="font-mono text-sm">{protocol}</div>
      </div>
      <div>
        <div className="text-xs text-muted uppercase tracking-wider mb-1">Uptime</div>
        <div className="font-medium">{uptime}</div>
      </div>
      <div>
        <div className="text-xs text-muted uppercase tracking-wider mb-1">Latency</div>
        <div className="font-mono text-sm">{latency}</div>
      </div>
    </div>
    <div className="mt-6 pt-4 border-t border-glass-border flex justify-between items-center">
      <button className="text-xs text-accent hover:text-accent-hover font-medium">View Logs</button>
      <button className="text-xs text-accent hover:text-accent-hover font-medium">Configure</button>
    </div>
  </Card>
);

export const Systems = () => {
  const [systems, setSystems] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    import('../services/api').then(({ fetchSystemsMonitoring }) => {
      fetchSystemsMonitoring()
        .then(data => {
          setSystems(data);
          setLoading(false);
        })
        .catch(err => {
          console.error(err);
          setError(err.message);
          setLoading(false);
        });
    });
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-muted fade-in">Loading systems health...</div>;
  }

  if (error) {
    return <div className="p-8 text-center text-error fade-in">Failed to load systems: {error}</div>;
  }

  return (
    <div className="flex-col gap-6 flex fade-in">
      <p className="text-muted max-w-3xl">
        GovMesh connects to disparate legacy government systems, standardizing their diverse protocols (REST, SOAP, XML, legacy databases) into a unified internal data graph.
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {systems.map((sys, idx) => (
          <SystemCard 
            key={idx}
            name={sys.name} 
            type={sys.system_type} 
            icon={sys.name.includes("Identity") ? Database : sys.name.includes("Property") ? Server : sys.name.includes("Municipality") ? Globe : Lock} 
            status={sys.status} 
            uptime={`${sys.uptime_percent}%`} 
            latency={`${sys.latency_ms}ms`} 
            protocol={sys.protocol} 
          />
        ))}
      </div>
    </div>
  );
};
