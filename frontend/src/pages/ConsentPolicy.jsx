import React, { useState, useEffect, useRef } from 'react';
import { Card } from '../components/ui/Card';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Loader } from '../components/ui/Loader';
import { checkActiveConsent, fetchServiceDefinitions, grantConsent, revokeConsent } from '../services/api';
import { Shield, ShieldAlert, ShieldCheck } from 'lucide-react';
import { useAuth } from '../auth/AuthContext';

export const ConsentPolicy = () => {
  const { user } = useAuth();
  const [citizenId, setCitizenId] = useState(user?.citizen_id || '');
  const [serviceType, setServiceType] = useState('business_registration');
  const [consent, setConsent] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [definitions, setDefinitions] = useState([]);
  const [ttlHours, setTtlHours] = useState(24);
  const [actionResult, setActionResult] = useState('');
  const requestSequence = useRef(0);
  const selectedDefinition = definitions.find(item => item.id === serviceType);

  const fetchConsent = async () => {
    const sequence = ++requestSequence.current;
    setIsLoading(true);
    setError(null);
    try {
      const data = await checkActiveConsent(citizenId, serviceType);
      if (sequence === requestSequence.current) setConsent(data);
    } catch (err) {
      if (sequence === requestSequence.current) setError(err.message);
    } finally {
      if (sequence === requestSequence.current) setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchServiceDefinitions().then(setDefinitions).catch(err => setError(err.message));
    if (citizenId && serviceType) fetchConsent();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleGrant = async () => {
    setIsLoading(true);
    try {
      const created = await grantConsent(citizenId, serviceType, selectedDefinition.departments.map(item => item.id), ttlHours);
      setActionResult(`Consent ${created.id} granted until ${new Date(created.expires_at).toLocaleString()}.`);
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
      const revoked = await revokeConsent(consent.id);
      setActionResult(`${revoked.message}. Future departmental access is blocked; records already retrieved are not erased.`);
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
          Review and control the exact departmental scope used for this fictional citizen. Revocation blocks subsequent access; it does not erase records already retrieved.
        </p>
        
        <div className="flex-col gap-4 flex mb-6">
          <div className="form-group mb-0">
            <label className="form-label" htmlFor="consent-citizen">Citizen ID</label>
            <input
              id="consent-citizen"
              className="form-input" 
              value={citizenId}
              onChange={e => setCitizenId(e.target.value)}
              readOnly={Boolean(user?.citizen_id)}
              placeholder="e.g. CIT-1001"
            />
          </div>
          <div className="form-group mb-0">
            <label className="form-label" htmlFor="consent-service">Service Type</label>
            <select id="consent-service" className="form-select" value={serviceType} onChange={e => { requestSequence.current += 1; setConsent(null); setActionResult(''); setServiceType(e.target.value); }}>
              {definitions.map(item => <option key={item.id} value={item.id}>{item.label}</option>)}
            </select>
          </div>
          <div className="form-group mb-0"><label className="form-label">Consent duration</label><select className="form-select" value={ttlHours} onChange={e => setTtlHours(Number(e.target.value))}><option value={1}>1 hour</option><option value={24}>24 hours</option><option value={168}>7 days</option></select></div>
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
            <strong>{selectedDefinition?.label || serviceType}</strong> requires only the following departments:
          </p>
          <ul className="scope-list">{selectedDefinition?.departments.map(item => <li key={item.id}><strong>{item.id}</strong><span>{item.reason}</span></li>)}</ul>
          <p className="text-xs text-muted mb-4">Expiry preview: {new Date(Date.now() + ttlHours * 3600000).toLocaleString()}</p>
          
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
        {actionResult && <div className="advisory-empty">{actionResult}</div>}
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
