import React from 'react';
import { Card } from './ui/Card';
import { Send, FileText, User } from 'lucide-react';

const ServiceRequestForm = ({ 
  onSubmit, 
  isLoading, 
  citizenId, 
  setCitizenId, 
  serviceType, 
  setServiceType, 
  definitions = [] 
}) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!citizenId.trim() || !serviceType.trim()) return;
    onSubmit(citizenId, serviceType);
  };

  return (
    <Card title="Submit Service Request">
      <p className="text-sm text-muted mb-4">
        Query federated registries across all departments under active DPDP Act 2023 policy gate.
      </p>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="form-group mb-0">
          <label className="form-label" htmlFor="citizenId">Citizen ID</label>
          <input
            type="text"
            id="citizenId"
            className="form-input"
            value={citizenId}
            onChange={(e) => setCitizenId(e.target.value)}
            placeholder="e.g. CIT-1001"
            required
            disabled={isLoading}
          />
        </div>

        <div className="form-group mb-0">
          <label className="form-label" htmlFor="serviceType">Service Type</label>
          <select
            id="serviceType"
            className="form-select"
            value={serviceType}
            onChange={(e) => setServiceType(e.target.value)}
            required
            disabled={isLoading}
          >
            {definitions.map((item) => (
              <option key={item.id} value={item.id}>
                {item.label}
              </option>
            ))}
          </select>
        </div>

        <button 
          type="submit" 
          className="btn btn-primary w-full mt-2" 
          disabled={isLoading}
        >
          {isLoading ? (
            <span className="flex items-center justify-center gap-2">
              <span className="spin">↻</span> Querying Federated Mesh…
            </span>
          ) : (
            <span className="flex items-center justify-center gap-2">
              <Send size={16} /> Execute Service Request
            </span>
          )}
        </button>
      </form>
    </Card>
  );
};

export default ServiceRequestForm;
