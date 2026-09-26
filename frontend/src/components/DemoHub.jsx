import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  Play, 
  ShieldCheck, 
  ShieldAlert, 
  AlertTriangle, 
  GitCompare, 
  Cpu, 
  ChevronDown, 
  ChevronUp, 
  Sparkles,
  ExternalLink,
  CheckCircle2,
  Layers
} from 'lucide-react';
import { checkActiveConsent, grantConsent, revokeConsent } from '../services/api';

export const DemoHub = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [isOpen, setIsOpen] = useState(true);
  const [isRunning, setIsRunning] = useState(false);
  const [activeMessage, setActiveMessage] = useState(null);

  const runScenario = async (scenarioKey) => {
    setIsRunning(true);
    setActiveMessage(null);

    try {
      if (scenarioKey === 'golden') {
        setActiveMessage({
          title: 'Scenario 1: Golden Path (CIT-1001)',
          description: 'Granting consent and executing concurrent queries across Identity, Municipality, Property, and Tax.',
          badge: 'success'
        });
        // Ensure consent is granted
        const existing = await checkActiveConsent('CIT-1001', 'business_registration').catch(() => null);
        if (!existing) {
          await grantConsent('CIT-1001', 'business_registration', ['identity', 'municipality', 'property', 'tax'], 24).catch(() => {});
        }
        navigate('/service-request?citizen=CIT-1001&service=business_registration&scenario=healthy_consistent&autoSubmit=true&evaluatorNote=Golden+Path%3A+All+4+departments+succeed+concurrently+via+asyncio.gather');
      } 
      else if (scenarioKey === 'denial') {
        setActiveMessage({
          title: 'Scenario 2: Zero-Trust Policy Gate Denial',
          description: 'Revoking consent to demonstrate DPDP Act 2023 zero-trust policy gate halting unauthorized queries before hitting any external service.',
          badge: 'error'
        });
        // Check and revoke consent
        const existing = await checkActiveConsent('CIT-1001', 'business_registration').catch(() => null);
        if (existing?.id) {
          await revokeConsent(existing.id).catch(() => {});
        }
        navigate('/service-request?citizen=CIT-1001&service=business_registration&scenario=healthy_consistent&autoSubmit=true&evaluatorNote=DPDP+Act+2023+Enforcement%3A+Policy+gate+immediately+denies+request+with+zero+external+network+calls');
      } 
      else if (scenarioKey === 'degradation') {
        setActiveMessage({
          title: 'Scenario 3: Graceful Degradation (CIT-1003)',
          description: 'Property record absent. GovMesh returns clean partial records with ZERO fake citizen data fabrication.',
          badge: 'warning'
        });
        const existing = await checkActiveConsent('CIT-1003', 'property_transfer').catch(() => null);
        if (!existing) {
          await grantConsent('CIT-1003', 'property_transfer', ['identity', 'municipality', 'property', 'tax'], 24).catch(() => {});
        }
        navigate('/service-request?citizen=CIT-1003&service=property_transfer&scenario=property_missing&autoSubmit=true&evaluatorNote=Graceful+Degradation%3A+Property+registry+absent.+Clean+partial+response+with+ZERO+fake+data+fabrication');
      } 
      else if (scenarioKey === 'conflict') {
        setActiveMessage({
          title: 'Scenario 4: Deterministic Mismatch (CIT-1006)',
          description: 'Property owner differs ("Kabir A. Jain" vs "Kabir Jain"). Deterministic rules engine flags the discrepancy without opaque AI hallucination.',
          badge: 'warning'
        });
        const existing = await checkActiveConsent('CIT-1006', 'business_registration').catch(() => null);
        if (!existing) {
          await grantConsent('CIT-1006', 'business_registration', ['identity', 'municipality', 'property', 'tax'], 24).catch(() => {});
        }
        navigate('/service-request?citizen=CIT-1006&service=business_registration&scenario=owner_name_mismatch&autoSubmit=true&evaluatorNote=Explainable+Advisory%3A+Deterministic+cross-system+rule+flags+name+discrepancy+(Kabir+A.+Jain+vs+Kabir+Jain)');
      } 
      else if (scenarioKey === 'schema') {
        setActiveMessage({
          title: 'Scenario 5: Schema Evolution & Governance',
          description: 'Navigating to Intelligence Engine. Demonstrates Property v1 -> v2 upgrade, breaking change detection, and human Data Steward approval.',
          badge: 'info'
        });
        navigate('/intelligence');
      }
    } catch (err) {
      console.error('Demo runner error:', err);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <aside className="demo-hub-container" aria-label="SIH 2026 Evaluator Demo Hub">
      <div className="demo-hub-header">
        <div className="demo-hub-title-group">
          <span className="demo-badge-sih">SIH 2026 EVALUATION SUITE</span>
          <span className="demo-badge-ps">PS: SIH26129 · Govt of Maharashtra</span>
          <span className="demo-badge-subtle">1-Click Live Scenarios</span>
        </div>
        <button 
          className="demo-toggle-btn"
          onClick={() => setIsOpen(!isOpen)}
          aria-expanded={isOpen}
          title={isOpen ? 'Collapse Evaluator Hub' : 'Expand Evaluator Hub'}
        >
          {isOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          <span>{isOpen ? 'Hide Scenarios' : 'Show 1-Click Scenarios'}</span>
        </button>
      </div>

      {isOpen && (
        <div className="demo-hub-body">
          <div className="demo-actions-grid">
            <button 
              className="demo-btn demo-btn-golden" 
              onClick={() => runScenario('golden')}
              disabled={isRunning}
              title="Demo CIT-1001: All 4 microservices succeed in parallel"
            >
              <ShieldCheck size={15} className="text-emerald-400 shrink-0" />
              <span>1. Golden Path (CIT-1001)</span>
            </button>

            <button 
              className="demo-btn demo-btn-denial" 
              onClick={() => runScenario('denial')}
              disabled={isRunning}
              title="Demo Policy Gate Denial: Zero-trust consent gate halts query"
            >
              <ShieldAlert size={15} className="text-rose-400 shrink-0" />
              <span>2. Zero-Trust Denial</span>
            </button>

            <button 
              className="demo-btn demo-btn-degradation" 
              onClick={() => runScenario('degradation')}
              disabled={isRunning}
              title="Demo CIT-1003: Property absent, graceful degradation with zero fake data"
            >
              <AlertTriangle size={15} className="text-amber-400 shrink-0" />
              <span>3. Degradation (CIT-1003)</span>
            </button>

            <button 
              className="demo-btn demo-btn-conflict" 
              onClick={() => runScenario('conflict')}
              disabled={isRunning}
              title="Demo CIT-1006: Name mismatch cross-system advisory"
            >
              <GitCompare size={15} className="text-indigo-400 shrink-0" />
              <span>4. Name Conflict (CIT-1006)</span>
            </button>

            <button 
              className="demo-btn demo-btn-schema" 
              onClick={() => runScenario('schema')}
              disabled={isRunning}
              title="Demo Schema Evolution: Upgrades Property v1 to v2 with Data Steward approval"
            >
              <Cpu size={15} className="text-cyan-400 shrink-0" />
              <span>5. Schema Evolution (v1→v2)</span>
            </button>
          </div>

          {activeMessage && (
            <div className={`demo-active-toast toast-${activeMessage.badge} fade-in`}>
              <div className="toast-header">
                <strong>{activeMessage.title}</strong>
              </div>
              <p className="toast-desc">{activeMessage.description}</p>
            </div>
          )}
        </div>
      )}
    </aside>
  );
};

export default DemoHub;
