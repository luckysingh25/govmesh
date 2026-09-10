import React from 'react';

const ServiceRequestForm = ({ onSubmit, isLoading, citizenId, setCitizenId, serviceType, setServiceType, definitions = [] }) => {

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!citizenId.trim() || !serviceType.trim()) return;
    onSubmit(citizenId, serviceType);
  };

  return (
    <div className="form-container fade-in">
      <h2>Submit Service Request</h2>
      <p className="subtitle">Enter citizen details to fetch data across departments.</p>
      
      <form onSubmit={handleSubmit} className="gov-form">
        <div className="form-group">
          <label htmlFor="citizenId">Citizen ID</label>
          <input
            type="text"
            id="citizenId"
            value={citizenId}
            onChange={(e) => setCitizenId(e.target.value)}
            placeholder="e.g. CIT-1001"
            required
            disabled={isLoading}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="serviceType">Service Type</label>
          <select
            id="serviceType"
            value={serviceType}
            onChange={(e) => setServiceType(e.target.value)}
            required
            disabled={isLoading}
          >
            {definitions.map(item => <option key={item.id} value={item.id}>{item.label}</option>)}
          </select>
        </div>
        
        <button type="submit" className="btn-primary" disabled={isLoading}>
          {isLoading ? (
            <span className="spinner-text">
              <span className="spinner"></span> Processing...
            </span>
          ) : (
            'Execute Actual Request'
          )}
        </button>
      </form>
    </div>
  );
};

export default ServiceRequestForm;
