import React, { useState } from 'react';

const ServiceRequestForm = ({ onSubmit, isLoading }) => {
  const [citizenId, setCitizenId] = useState('CIT-1001');
  const [serviceType, setServiceType] = useState('business_registration');

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
            <option value="business_registration">Business Registration</option>
            <option value="property_transfer">Property Transfer</option>
            <option value="tax_clearance">Tax Clearance Certificate</option>
          </select>
        </div>
        
        <button type="submit" className="btn-primary" disabled={isLoading}>
          {isLoading ? (
            <span className="spinner-text">
              <span className="spinner"></span> Processing...
            </span>
          ) : (
            'Process Request'
          )}
        </button>
      </form>
    </div>
  );
};

export default ServiceRequestForm;
