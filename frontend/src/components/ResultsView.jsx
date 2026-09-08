import React from 'react';

const DepartmentCard = ({ name, data, icon }) => {
  if (!data) return null;
  
  const isSuccess = data.status === 'success';
  const displayData = data.data || {};
  
  return (
    <div className={`dept-card ${isSuccess ? 'success' : 'error'}`}>
      <div className="dept-header">
        <span className="dept-icon">{icon}</span>
        <h3>{name}</h3>
        <span className={`status-badge ${isSuccess ? 'success' : 'error'}`}>
          {isSuccess ? 'Success' : 'Failed'}
        </span>
      </div>
      
      <div className="dept-content">
        {isSuccess ? (
          <ul className="data-list">
            {Object.entries(displayData).map(([key, value]) => (
              <li key={key}>
                <span className="data-label">{key}:</span>
                <span className="data-value">{String(value)}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="error-text">{data.error}</p>
        )}
      </div>
    </div>
  );
};

const ResultsView = ({ result }) => {
  if (!result) return null;

  return (
    <div className="results-container fade-in">
      <div className="results-header">
        <h2>Service Request Status</h2>
        <div className="meta-info">
          <span><strong>Request ID:</strong> {result.request_id}</span>
          <span><strong>Correlation ID:</strong> {result.correlation_id}</span>
          {result.consent_id && <span><strong>Consent ID:</strong> {result.consent_id}</span>}
          {result.policy_decision && <span className="text-xs text-muted"><strong>Policy:</strong> {result.policy_decision}</span>}
          <span className={`badge ${result.overall_status === 'denied' ? 'badge-error' : 'badge-success'} mt-1`}>{result.overall_status.toUpperCase()}</span>
        </div>
      </div>
      
      <div className="citizen-info">
        <h3>Citizen Identity</h3>
        <div className="citizen-grid">
          <div><strong>ID:</strong> {result.citizen.citizen_id}</div>
          <div><strong>Name:</strong> {result.citizen.name}</div>
          <div className="full-width"><strong>Address:</strong> {result.citizen.address}</div>
        </div>
      </div>

      <div className="departments-grid">
        <DepartmentCard name="Identity" data={result.identity} icon="👤" />
        <DepartmentCard name="Property" data={result.property} icon="🏠" />
        <DepartmentCard name="Municipality" data={result.municipality} icon="🏛️" />
        <DepartmentCard name="Tax" data={result.tax} icon="💰" />
      </div>
    </div>
  );
};

export default ResultsView;
