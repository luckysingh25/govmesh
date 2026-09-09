import React, { useEffect, useMemo, useState } from 'react';
import ServiceRequestForm from '../components/ServiceRequestForm';
import ResultsView from '../components/ResultsView';
import { fetchDemoScenarios, fetchServiceDefinitions, resumeWorkflow, submitServiceRequest } from '../services/api';
import { ShieldAlert } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { useAuth } from '../auth/AuthContext';

export const ServiceRequest = () => {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [definitions, setDefinitions] = useState([]);
  const [scenarios, setScenarios] = useState([]);
  const [scenarioName, setScenarioName] = useState('');
  const [citizenId, setCitizenId] = useState(user?.citizen_id || 'CIT-1001');
  const [serviceType, setServiceType] = useState('business_registration');
  const [resumeLoading, setResumeLoading] = useState(false);

  useEffect(() => {
    Promise.all([fetchServiceDefinitions(), fetchDemoScenarios()]).then(([defs, demos]) => {
      setDefinitions(defs); setScenarios(demos);
      if (defs.length) setServiceType(defs[0].id);
    }).catch(err => setError(err.message));
  }, []);

  const scenario = useMemo(() => scenarios.find(item => item.scenario_name === scenarioName), [scenarios, scenarioName]);
  const chooseScenario = (name) => {
    setScenarioName(name); setResult(null); setError(null);
    const chosen = scenarios.find(item => item.scenario_name === name);
    if (chosen?.selectable) { setCitizenId(chosen.citizen_id); setServiceType(chosen.service_type); }
  };

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

  const handleResume = async () => {
    setResumeLoading(true); setError(null);
    try {
      const workflow = await resumeWorkflow(result.request_id);
      const byName = Object.fromEntries(workflow.steps.map(step => [step.step_name, { status: step.status, data: step.result_data, error: step.error_message, ...step }]));
      setResult(previous => ({
        ...previous,
        ...byName,
        overall_status: workflow.status,
        insights: workflow.insights || [],
      }));
    } catch (err) { setError(err.message); } finally { setResumeLoading(false); }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start fade-in">
      <div className="flex-col gap-6 flex">
        <Card title="Fictional demo scenario">
          <label className="form-label" htmlFor="scenario">Scenario selector</label>
          <select id="scenario" className="form-select" value={scenarioName} onChange={e => chooseScenario(e.target.value)}>
            <option value="">Choose a deterministic scenario</option>
            {scenarios.map(item => <option key={item.scenario_name} value={item.scenario_name} disabled={!item.selectable}>{item.scenario_name.replaceAll('_', ' ')} · {item.citizen_id}{item.selectable ? '' : ' (sign in as this citizen)'}</option>)}
          </select>
          {scenario && <div className="scenario-box"><strong>Expected scenario</strong><p>{scenario.explanation}</p><small>Expected overall status: {scenario.expected_overall_status}. This selection does not grant consent or create an actual result.</small></div>}
        </Card>
        <ServiceRequestForm onSubmit={handleRequestSubmit} isLoading={isLoading} citizenId={citizenId} setCitizenId={setCitizenId} serviceType={serviceType} setServiceType={setServiceType} definitions={definitions} />
        
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
        <h3 className="mb-4">Actual execution result</h3>
        {result ? (
          <ResultsView result={result} onResume={handleResume} resumeLoading={resumeLoading} />
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
