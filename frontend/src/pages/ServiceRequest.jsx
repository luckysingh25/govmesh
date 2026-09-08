import React, { useState } from 'react';
import ServiceRequestForm from '../components/ServiceRequestForm';
import ResultsView from '../components/ResultsView';
import { submitServiceRequest } from '../services/api';
import { ShieldAlert } from 'lucide-react';

export const ServiceRequest = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleRequestSubmit = async (citizenId, serviceType) => {
    setIsLoading(true);
    setError(null);
    setResult(null);
    
    try {
      const data = await submitServiceRequest(citizenId, serviceType);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start fade-in">
      <div className="flex-col gap-6 flex">
        <ServiceRequestForm onSubmit={handleRequestSubmit} isLoading={isLoading} />
        
        {error && (
          <div className="error-banner fade-in flex items-center gap-2">
            <ShieldAlert size={18} />
            <div>
              <strong>Error: </strong> {error}
            </div>
          </div>
        )}
      </div>
      
      <div className="right-panel">
        {result ? (
          <ResultsView result={result} />
        ) : (
          <div className="empty-state">
            <div className="empty-icon">📊</div>
            <h3>No Active Request</h3>
            <p>Submit a citizen service request to fetch unified department data.</p>
          </div>
        )}
      </div>
    </div>
  );
};
