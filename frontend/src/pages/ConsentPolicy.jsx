import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/Card';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Loader } from '../components/ui/Loader';
import { checkActiveConsent, grantConsent, revokeConsent } from '../services/api';
import { Shield, ShieldAlert, ShieldCheck } from 'lucide-react';

export const ConsentPolicy = () => {
  const [citizenId, setCitizenId] = useState('CIT-1001');
  const [serviceType, setServiceType] = useState('business_registration');
  const [consent, setConsent] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchConsent = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await checkActiveConsent(citizenId, serviceType);
      setConsent(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (citizenId && serviceType) fetchConsent();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleGrant = async () => {
    setIsLoading(true);
    try {
      await grantConsent(citizenId, serviceType, ["identity", "property", "municipality", "tax"]);
      await fetchConsent();
    } catch (err) {
      setError(err.message);
      setIsLoading(false);
    }
  };

  const handleRevoke = async () => {
    if (!consent) return;
    setIsLoading(true);
    try {
      await revokeConsent(consent.id);
      await fetchConsent();
    } catch (err) {
      setError(err.message);
      setIsLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start fade-in">
      <Card title="Citizen Consent Management">
        <p className="text-muted mb-6 text-sm">
          Simulate a citizen granting or revoking consent for the GovMesh system to access their data across departments.
        </p>
        
        <div className="flex-col gap-4 flex mb-6">
          <div className="form-group mb-0">
            <label className="form-label">Citizen ID</label>
            <input 
              className="form-input" 
              value={citizenId} 
              onChange={e => setCitizenId(e.target.value)} 
            />
          </div>
          <div className="form-group mb-0">
            <label className="form-label">Service Type</label>
            <select className="form-select" value={serviceType} onChange={e => setServiceType(e.target.value)}>
              <option value="business_registration">Business Registration</option>
              <option value="property_transfer">Property Transfer</option>
            </select>
          </div>
          <button className="btn btn-outline" onClick={fetchConsent} disabled={isLoading}>
            Check Current Status
          </button>
        </div>

        {error && <div className="error-text mb-4">{error}</div>}

        <div className="p-4 border border-glass-border rounded-lg bg-slate-900/50">
          <h4 className="font-semibold mb-4 flex items-center gap-2">
            <Shield size={18} /> Active Policy Rule
          </h4>
          <p className="text-sm text-muted mb-4">
            Service requests for <strong>{serviceType}</strong> require explicit citizen consent for departments: 
            <span className="text-primary font-mono ml-2">identity, property, municipality, tax</span>.
          </p>
          
          <div className="flex gap-4">
            <button 
              className="btn btn-primary flex-1" 
              onClick={handleGrant}
              disabled={isLoading || consent}
            >
              Grant Consent
            </button>
            <button 
              className="btn btn-danger flex-1" 
              onClick={handleRevoke}
              disabled={isLoading || !consent}
            >
              Revoke Access
            </button>
          </div>
        </div>
      </Card>

      <Card title="Current Status" className="h-full">
        {isLoading ? <Loader /> : (
          <div className="flex flex-col items-center justify-center h-full min-h-[300px] text-center">
            {consent ? (
              <>
                <ShieldCheck size={64} className="text-success mb-4" />
                <h3 className="text-xl font-bold mb-2 text-success">Consent Active</h3>
                <p className="text-muted mb-6 max-w-sm">
                  Citizen has granted access to their data for this service type.
                </p>
                <div className="text-left bg-slate-900/80 p-4 rounded-lg w-full text-sm font-mono text-muted overflow-auto">
                  <pre>{JSON.stringify(consent, null, 2)}</pre>
                </div>
              </>
            ) : (
              <>
                <ShieldAlert size={64} className="text-error mb-4" />
                <h3 className="text-xl font-bold mb-2 text-error">Access Denied</h3>
                <p className="text-muted max-w-sm">
                  No active consent found. Service requests will be blocked by the policy engine.
                </p>
              </>
            )}
          </div>
        )}
      </Card>
    </div>
  );
};
