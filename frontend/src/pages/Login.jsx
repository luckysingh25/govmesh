import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { 
  Moon, 
  Sun, 
  ShieldCheck, 
  Building2, 
  User, 
  KeyRound, 
  Lock, 
  CheckCircle2, 
  ArrowRight,
  BadgeAlert,
  UserCheck,
  AlertTriangle
} from 'lucide-react';
import { useAuth } from '../auth/AuthContext';
import { useTheme } from '../theme/ThemeContext';
import { GovEmblem, TricolorBar } from '../components/common/GovEmblem';

const DEMO_PERSONAS = [
  {
    category: 'officials',
    id: 'admin',
    name: 'State Administrator',
    designation: 'Director of e-Governance (GAD)',
    email: 'admin@govmesh.example',
    role: 'admin',
    badge: 'STATE ADMIN',
    color: '#1E3A8A', // Deep Navy
    icon: Building2,
    description: 'Full federated control, multi-protocol execution, system health monitoring, and audit trails.',
    access: 'All 4 Department Connectors · System Governance · Audit Logs'
  },
  {
    category: 'officials',
    id: 'steward',
    name: 'Chief Data Steward',
    designation: 'Interoperability & Schema Governance Cell',
    email: 'steward@govmesh.example',
    role: 'data_steward',
    badge: 'DATA STEWARD',
    color: '#047857', // Forest Emerald
    icon: ShieldCheck,
    description: 'Schema evolution oversight, N-gram semantic mapping approvals, and breaking-change impact analysis.',
    access: 'Schema Registry · Mapping Approvals · Impact Analyzer · DPDP Compliance'
  },
  {
    category: 'citizens',
    id: 'cit1001',
    name: 'Aarav Sharma (CIT-1001)',
    designation: 'Golden Path Citizen',
    email: 'citizen1001@govmesh.example',
    role: 'citizen',
    badge: 'GOLDEN PATH',
    color: '#059669',
    icon: User,
    description: 'All 4 records consistent, active, and tax-cleared. Executes clean concurrent federation.',
    access: 'Identity (Aadhaar/REST) · Municipality (JSON-RPC) · Property (SOAP) · Tax (REST)'
  },
  {
    category: 'citizens',
    id: 'cit1006',
    name: 'Kabir Jain (CIT-1006)',
    designation: 'Deterministic Conflict Test',
    email: 'citizen1006@govmesh.example',
    role: 'citizen',
    badge: 'NAME MISMATCH',
    color: '#4F46E5',
    icon: BadgeAlert,
    description: 'Property owner name differs ("Kabir A. Jain" vs "Kabir Jain"). Proves cross-system audit rules.',
    access: 'Conflict Detection Rule · Human Advisory Flag · Integrity Gate'
  }
];

export const Login = () => {
  const { user, login } = useAuth();
  const { isLight, toggleTheme } = useTheme();

  const [activeTab, setActiveTab] = useState('officials');
  const [selectedPersona, setSelectedPersona] = useState(DEMO_PERSONAS[0]);
  const [email, setEmail] = useState(DEMO_PERSONAS[0].email);
  const [password, setPassword] = useState('GovMesh@2026!');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  if (user) return <Navigate to="/" replace />;

  const handleSelectPersona = (persona) => {
    setSelectedPersona(persona);
    setEmail(persona.email);
    setPassword('GovMesh@2026!');
    setError('');
  };

  const handleQuickLogin = async (persona) => {
    setSelectedPersona(persona);
    setEmail(persona.email);
    setPassword('GovMesh@2026!');
    setError('');
    setLoading(true);
    try {
      await login(persona.email, 'GovMesh@2026!');
    } catch (err) {
      setError(err.message || 'Login failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const submit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');
    try {
      await login(email, password);
    } catch (err) {
      setError(err.message || 'Authentication failed. Please verify your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const filteredPersonas = DEMO_PERSONAS.filter(p => p.category === activeTab);

  return (
    <div className="gov-login-viewport">
      <TricolorBar />

      {/* Top Government Navigation Bar */}
      <header className="gov-auth-topbar">
        <div className="gov-auth-brand">
          <GovEmblem size={34} className="text-gov-gold" />
          <div className="gov-brand-text">
            <div className="gov-brand-state">महाराष्ट्र शासन • GOVERNMENT OF MAHARASHTRA</div>
            <div className="gov-brand-sub">General Administration Dept (GAD) • Mantralaya, Mumbai</div>
          </div>
        </div>

        <div className="gov-topbar-controls">
          <div className="gov-sih-tag">
            <span className="sih-pill">SIH 2026</span>
            <span className="ps-pill">PS: SIH26129</span>
          </div>

          <button
            type="button"
            className="btn btn-outline theme-toggle"
            onClick={toggleTheme}
            aria-label={`Switch to ${isLight ? 'dark' : 'light'} mode`}
          >
            {isLight ? <Moon size={16} /> : <Sun size={16} />}
            <span>{isLight ? 'Dark' : 'Light'}</span>
          </button>
        </div>
      </header>

      {/* Main Login Workspace */}
      <main className="gov-login-container">
        <div className="gov-login-hero">
          <div className="gov-mesh-badge">
            <GovEmblem size={20} />
            <span>GovMesh National Interoperability Architecture</span>
          </div>
          <h1 className="gov-hero-heading">
            Federated Civic Data Exchange &amp; Zero-Trust Interoperability Platform
          </h1>
          <p className="gov-hero-sub">
            Seamless multi-protocol orchestration across State Identity, Municipal Corporation, 
            Property Registration (IGR), and Revenue Services under statutory DPDP Act 2023 compliance.
          </p>
        </div>

        <div className="gov-login-split">
          {/* Left Column: Interactive Role & Persona Selector */}
          <section className="gov-role-selector-card">
            <div className="role-selector-header">
              <div>
                <h2 className="text-lg font-bold flex items-center gap-2">
                  <UserCheck size={20} className="text-gov-navy" />
                  Select Demonstration Persona
                </h2>
                <p className="text-xs text-muted">
                  Choose a verified departmental role or citizen scenario for 1-click evaluation.
                </p>
              </div>

              {/* Persona Tabs */}
              <div className="gov-role-tabs">
                <button
                  type="button"
                  className={`gov-role-tab ${activeTab === 'officials' ? 'active' : ''}`}
                  onClick={() => setActiveTab('officials')}
                >
                  Government Officials ({DEMO_PERSONAS.filter(p => p.category === 'officials').length})
                </button>
                <button
                  type="button"
                  className={`gov-role-tab ${activeTab === 'citizens' ? 'active' : ''}`}
                  onClick={() => setActiveTab('citizens')}
                >
                  Citizen Scenarios ({DEMO_PERSONAS.filter(p => p.category === 'citizens').length})
                </button>
              </div>
            </div>

            {/* Persona Grid */}
            <div className="persona-grid">
              {filteredPersonas.map((persona) => {
                const IconComponent = persona.icon;
                const isSelected = selectedPersona.id === persona.id;

                return (
                  <div
                    key={persona.id}
                    className={`persona-card ${isSelected ? 'selected' : ''}`}
                    onClick={() => handleSelectPersona(persona)}
                  >
                    <div className="persona-card-top">
                      <div className="persona-avatar">
                        <IconComponent size={20} />
                      </div>
                      <div className="persona-info">
                        <div className="flex items-center justify-between">
                          <span className="persona-name">{persona.name}</span>
                          <span className={`gov-role-badge badge-${persona.role}`}>
                            {persona.badge}
                          </span>
                        </div>
                        <span className="persona-desig">{persona.designation}</span>
                      </div>
                    </div>

                    <p className="persona-desc">{persona.description}</p>

                    <div className="persona-footer">
                      <span className="persona-email">{persona.email}</span>
                      <button
                        type="button"
                        className="btn-quick-login"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleQuickLogin(persona);
                        }}
                        disabled={loading}
                      >
                        <span>Sign In</span>
                        <ArrowRight size={13} />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </section>

          {/* Right Column: Official Parichay / SSO Sign-In Panel */}
          <section className="gov-signin-box">
            <div className="signin-box-header">
              <div className="flex items-center gap-2">
                <Lock size={18} className="text-gov-saffron" />
                <span className="font-semibold text-sm">Official GovNet Authentication</span>
              </div>
              <span className="gov-sec-chip">Level 4 · 256-Bit</span>
            </div>

            <div className="selected-role-preview">
              <span className="text-xs text-muted block mb-1">Active Selected Identity:</span>
              <div className="flex items-center gap-2">
                <div className="role-avatar-circle">
                  <CheckCircle2 size={16} className="text-emerald-500" />
                </div>
                <div>
                  <div className="font-bold text-sm">{selectedPersona.name}</div>
                  <div className="text-xs text-muted">{selectedPersona.designation}</div>
                </div>
              </div>
            </div>

            <form className="signin-form" onSubmit={submit}>
              <div className="form-group">
                <label className="form-label" htmlFor="email">
                  Official Email / Gov ID
                </label>
                <div className="input-with-icon">
                  <User size={16} className="input-icon" />
                  <input
                    id="email"
                    className="form-input"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="user@govmesh.example"
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <div className="flex justify-between items-center mb-1">
                  <label className="form-label" htmlFor="password">
                    Security Passcode
                  </label>
                  <button
                    type="button"
                    className="text-xs text-muted hover:underline"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? 'Hide' : 'Show'}
                  </button>
                </div>
                <div className="input-with-icon">
                  <KeyRound size={16} className="input-icon" />
                  <input
                    id="password"
                    className="form-input"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                </div>
              </div>

              {error && (
                <div className="gov-auth-error">
                  <AlertTriangle size={16} />
                  <span>{error}</span>
                </div>
              )}

              <button
                type="submit"
                className="btn btn-gov-primary w-full"
                disabled={loading}
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="spin">↻</span> Authenticating with GovNet…
                  </span>
                ) : (
                  <span className="flex items-center justify-center gap-2">
                    <Lock size={16} />
                    Sign In as {selectedPersona.badge}
                  </span>
                )}
              </button>

              <div className="gov-auth-notice">
                <ShieldCheck size={14} className="text-muted shrink-0 mt-0.5" />
                <p className="text-xs text-muted leading-relaxed">
                  Protected under Section 43A of Information Technology Act 2000 &amp; DPDP Act 2023. 
                  Demonstration environment seeded with deterministic fixtures for SIH 2026.
                </p>
              </div>
            </form>
          </section>
        </div>
      </main>

      {/* Official Government Portal Footer */}
      <footer className="gov-portal-footer">
        <div className="gov-footer-inner">
          <div className="gov-footer-text">
            <span>Government of Maharashtra • General Administration Department (IT)</span>
            <span className="footer-sep">•</span>
            <span>Smart India Hackathon 2026 (Problem Statement: SIH26129)</span>
            <span className="footer-sep">•</span>
            <span>National Informatics Centre (NIC) &amp; MeitY Interoperability Standards</span>
          </div>
          <div className="gov-footer-compliance">
            <span>ISO 27001 Certified Architecture</span>
            <span className="footer-sep">•</span>
            <span>DPDP Act 2023 Zero-Trust Enforcement</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
