import React from 'react';
import { GovEmblem, TricolorBar } from './GovEmblem';
import { Shield, Lock, Eye, Globe } from 'lucide-react';

export const GovTopBanner = () => {
  return (
    <div className="gov-top-banner">
      <TricolorBar />
      <div className="gov-top-inner">
        <div className="gov-branding">
          <GovEmblem size={28} className="text-gov-gold" />
          <div className="gov-title-stack">
            <span className="gov-state-title">महाराष्ट्र शासन • GOVERNMENT OF MAHARASHTRA</span>
            <span className="gov-sub-title">General Administration Dept (GAD) • Smart Automation (SIH26129)</span>
          </div>
        </div>

        <div className="gov-meta-badges">
          <span className="gov-security-pill">
            <Lock size={12} className="text-emerald-500" />
            <span>GOVNET SECURE · ZERO-TRUST</span>
          </span>
          <span className="gov-compliance-pill">
            <Shield size={12} className="text-amber-500" />
            <span>DPDP ACT 2023 COMPLIANT</span>
          </span>
          <div className="gov-lang-indicator">
            <Globe size={13} />
            <span>मराठी / ENG</span>
          </div>
        </div>
      </div>
    </div>
  );
};
