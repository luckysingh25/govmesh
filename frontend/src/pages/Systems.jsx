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
  return (
    <div className="flex-col gap-6 flex fade-in">
      <p className="text-muted max-w-3xl">
        GovMesh connects to disparate legacy government systems, standardizing their diverse protocols (REST, SOAP, XML, legacy databases) into a unified internal data graph.
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        <SystemCard 
          name="National Identity DB" 
          type="Core Registry" 
          icon={Database} 
          status="Online" 
          uptime="99.99%" 
          latency="45ms" 
          protocol="REST / JSON" 
        />
        <SystemCard 
          name="State Property Records" 
          type="State Dept" 
          icon={Server} 
          status="Online" 
          uptime="99.95%" 
          latency="120ms" 
          protocol="SOAP / XML" 
        />
        <SystemCard 
          name="City Municipality" 
          type="Local Gov" 
          icon={Globe} 
          status="Degraded" 
          uptime="98.50%" 
          latency="850ms" 
          protocol="Legacy API" 
        />
        <SystemCard 
          name="Central Tax Authority" 
          type="Federal Dept" 
          icon={Lock} 
          status="Online" 
          uptime="99.99%" 
          latency="65ms" 
          protocol="gRPC" 
        />
      </div>
    </div>
  );
};
