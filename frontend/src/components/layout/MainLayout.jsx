import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { UserCircle, LogOut, Moon, Sun, Shield, Lock } from 'lucide-react';
import { useAuth } from '../../auth/AuthContext';
import { useTheme } from '../../theme/ThemeContext';
import { DemoHub } from '../DemoHub';
import { getPageMeta } from '../../config/navigation';

const ROLE_DESIGNATIONS = {
  admin: { title: 'State Administrator', dept: 'Mantralaya IT & GAD', badgeClass: 'badge-admin' },
  data_steward: { title: 'Chief Data Steward', dept: 'Schema Governance Cell', badgeClass: 'badge-steward' },
  civic_employee: { title: 'Civic Revenue Officer', dept: 'Municipal Services PMC/MCGM', badgeClass: 'badge-officer' },
  citizen: { title: 'Citizen Applicant', dept: 'Public Portal Direct Access', badgeClass: 'badge-citizen' }
};

export const MainLayout = () => {
  const { user, logout } = useAuth();
  const { isLight, toggleTheme } = useTheme();
  const location = useLocation();

  const pageMeta = getPageMeta(location.pathname);
  const title = pageMeta.title;

  const userRole = user?.role || 'citizen';
  const roleInfo = ROLE_DESIGNATIONS[userRole] || ROLE_DESIGNATIONS.citizen;

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-wrapper">
        {/* Executive Workstation Header */}
        <header className="topbar">
          <div className="topbar-title-section">
            <div className="gov-breadcrumb">
              <span>GovMesh Portal</span>
              <span className="breadcrumb-sep">/</span>
              <span className="breadcrumb-active">{title}</span>
            </div>
            <h1 className="page-title">{title}</h1>
          </div>

          <div className="topbar-actions">
            {/* GovNet Security Clearance Badge */}
            <div className="gov-security-badge" title="Zero-Trust Encrypted Gateway">
              <Lock size={13} className="text-emerald-500" />
              <span>CONFIDENTIAL · GOVNET</span>
            </div>

            <button
              className="btn btn-outline theme-toggle"
              onClick={toggleTheme}
              aria-label={`Switch to ${isLight ? 'dark' : 'light'} mode`}
              title={`Switch to ${isLight ? 'dark' : 'light'} mode`}
            >
              {isLight ? <Moon size={16} /> : <Sun size={16} />}
              <span>{isLight ? 'Dark' : 'Light'}</span>
            </button>

            {/* Official Designation Profile Card */}
            <div className="gov-user-profile">
              <div className="user-avatar-wrap">
                <UserCircle size={24} className="text-gov-navy" />
              </div>
              <div className="user-details">
                <div className="flex items-center gap-1.5">
                  <span className="user-name">{roleInfo.title}</span>
                  <span className={`gov-role-badge ${roleInfo.badgeClass}`}>
                    {userRole.toUpperCase()}
                  </span>
                </div>
                <span className="user-dept">{user?.email}</span>
              </div>
              <button
                className="btn btn-outline btn-logout"
                onClick={logout}
                title="End Secure GovNet Session"
              >
                <LogOut size={13} />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </header>

        {/* 1-Click SIH 2026 Evaluator Suite */}
        <DemoHub />

        {/* Core Workspace Canvas */}
        <main className="main-content">
          <Outlet />
        </main>

        {/* Fixed Bottom Footer - Level with Sidebar */}
        <footer className="gov-workspace-footer">
          <div className="footer-content">
            <div className="footer-left">
              <span className="footer-bold">GovMesh — शासकीय एकात्मिक डेटा विनिमय मंच</span>
              <span className="footer-sub">
                Smart India Hackathon 2026 · PS SIH26129 (Govt of Maharashtra)
              </span>
            </div>
            <div className="footer-right">
              <span className="compliance-tag">
                <Shield size={12} className="text-emerald-500" />
                DPDP Act 2023 Statutory Zero-Trust Gateway
              </span>
              <span className="compliance-sep">•</span>
              <span>NIC &amp; MeitY GIGW Compliant</span>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
};
