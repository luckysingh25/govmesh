import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldAlert, ArrowLeft, LogOut, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../../auth/AuthContext';

export const AccessDenied = ({ allowedRoles = [] }) => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const roleLabels = {
    admin: 'Platform Administrator',
    data_steward: 'Data Steward (Schema Governance)',
    citizen: 'Citizen / Service Consumer',
  };

  return (
    <div className="flex items-center justify-center p-6 min-h-[60vh] fade-in">
      <div className="max-w-xl w-full bg-[var(--card-bg)] border border-[var(--border)] rounded-2xl p-8 shadow-2xl relative overflow-hidden">
        {/* Top security tricolor strip */}
        <div className="absolute top-0 left-0 right-0 h-1 flex">
          <span className="flex-1 bg-[#ff9933]" />
          <span className="flex-1 bg-[#ffffff]" />
          <span className="flex-1 bg-[#138808]" />
        </div>

        <div className="flex items-center gap-4 mb-6">
          <div className="w-14 h-14 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-500">
            <ShieldAlert size={32} />
          </div>
          <div>
            <span className="text-xs font-bold tracking-wider text-amber-500 uppercase">
              RBAC Authorization Gate
            </span>
            <h2 className="text-xl font-bold text-[var(--text-primary)]">
              Restricted Government Resource
            </h2>
          </div>
        </div>

        <p className="text-sm text-[var(--text-secondary)] leading-relaxed mb-6">
          Under the <strong>Maharashtra Data Mesh Governance & Security Framework</strong>, access to this module is strictly partitioned by role to maintain regulatory segregation of duties.
        </p>

        <div className="bg-[var(--surface-subtle)] border border-[var(--border)] rounded-xl p-4 mb-6 space-y-3">
          <div className="flex items-center justify-between text-xs">
            <span className="text-[var(--text-secondary)]">Your Current Persona:</span>
            <span className="font-semibold text-[var(--text-primary)] px-2.5 py-1 rounded bg-[var(--card-bg)] border border-[var(--border)]">
              {roleLabels[user?.role] || user?.role} ({user?.email})
            </span>
          </div>

          <div className="flex items-center justify-between text-xs">
            <span className="text-[var(--text-secondary)]">Required Role(s):</span>
            <span className="font-semibold text-amber-400">
              {allowedRoles.map(r => roleLabels[r] || r).join(' or ')}
            </span>
          </div>
        </div>

        <div className="border-t border-[var(--border)] pt-5 flex items-center justify-between gap-4">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 px-4 py-2.5 text-xs font-medium text-[var(--text-primary)] bg-[var(--surface-subtle)] hover:bg-[var(--surface-hover)] border border-[var(--border)] rounded-lg transition-all"
          >
            <ArrowLeft size={14} /> Back to My Dashboard
          </button>

          <button
            onClick={() => {
              logout();
              navigate('/login');
            }}
            className="flex items-center gap-2 px-4 py-2.5 text-xs font-medium text-amber-400 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 rounded-lg transition-all"
          >
            <LogOut size={14} /> Switch Authorized Role
          </button>
        </div>
      </div>
    </div>
  );
};
