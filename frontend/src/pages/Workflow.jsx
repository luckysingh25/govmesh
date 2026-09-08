import React from 'react';
import { Card } from '../components/ui/Card';
import { CheckCircle2, CircleDashed, Clock, Server, FileText, CheckCircle } from 'lucide-react';

export const Workflow = () => {
  return (
    <div className="flex-col gap-6 flex fade-in">
      <Card title="GovMesh Orchestration Flow">
        <p className="text-muted mb-8 max-w-3xl">
          GovMesh orchestrates complex citizen requests across multiple legacy systems concurrently, handling failures gracefully and unifying responses.
        </p>
        
        <div className="timeline">
          <div className="timeline-item">
            <div className="timeline-dot success">
              <CheckCircle size={16} className="text-success" />
            </div>
            <div className="ml-8">
              <h4 className="font-bold text-lg mb-1">Citizen Submits Request</h4>
              <p className="text-muted text-sm mb-2">Frontend portal sends POST request to GovMesh API Gateway</p>
              <div className="bg-slate-900/50 p-3 rounded text-xs font-mono border border-slate-800 inline-block text-slate-300">
                POST /api/v1/service-requests
              </div>
            </div>
          </div>
          
          <div className="timeline-item">
            <div className="timeline-dot success">
              <CheckCircle size={16} className="text-success" />
            </div>
            <div className="ml-8">
              <h4 className="font-bold text-lg mb-1">Policy & Consent Evaluation</h4>
              <p className="text-muted text-sm mb-2">Policy Engine verifies if citizen has granted necessary access.</p>
              <span className="badge badge-success">Access Allowed</span>
            </div>
          </div>

          <div className="timeline-item">
            <div className="timeline-dot success">
              <Server size={14} className="text-success" />
            </div>
            <div className="ml-8">
              <h4 className="font-bold text-lg mb-3">Parallel Data Retrieval</h4>
              <p className="text-muted text-sm mb-4">Orchestrator spawns concurrent fetch requests to department connectors.</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-3 border border-success/30 bg-success/5 rounded-lg flex items-center gap-3">
                  <CheckCircle2 size={18} className="text-success" />
                  <div>
                    <div className="font-medium text-sm">Identity Connector</div>
                    <div className="text-xs text-muted">REST API • 45ms</div>
                  </div>
                </div>
                <div className="p-3 border border-success/30 bg-success/5 rounded-lg flex items-center gap-3">
                  <CheckCircle2 size={18} className="text-success" />
                  <div>
                    <div className="font-medium text-sm">Property Connector</div>
                    <div className="text-xs text-muted">SOAP/XML • 120ms</div>
                  </div>
                </div>
                <div className="p-3 border border-success/30 bg-success/5 rounded-lg flex items-center gap-3">
                  <CheckCircle2 size={18} className="text-success" />
                  <div>
                    <div className="font-medium text-sm">Tax Connector</div>
                    <div className="text-xs text-muted">gRPC • 65ms</div>
                  </div>
                </div>
                <div className="p-3 border border-warning/30 bg-warning/5 rounded-lg flex items-center gap-3">
                  <Clock size={18} className="text-warning" />
                  <div>
                    <div className="font-medium text-sm">Municipality Connector</div>
                    <div className="text-xs text-muted">Legacy Polling • 850ms</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="timeline-item">
            <div className="timeline-dot success">
              <FileText size={14} className="text-success" />
            </div>
            <div className="ml-8">
              <h4 className="font-bold text-lg mb-1">Data Normalization & Response</h4>
              <p className="text-muted text-sm mb-2">GovMesh normalizes the disparate responses into a single JSON graph.</p>
              <div className="bg-slate-900/50 p-3 rounded text-xs font-mono border border-slate-800 text-slate-300 max-w-lg overflow-hidden whitespace-nowrap overflow-ellipsis">
                {"{ overall_status: 'completed', citizen: {...}, identity: {...} }"}
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};
