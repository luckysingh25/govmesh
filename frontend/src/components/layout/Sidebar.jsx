import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../auth/AuthContext';
import { GovEmblem } from '../common/GovEmblem';
import { NAVIGATION_CONFIG } from '../../config/navigation';

export const Sidebar = () => {
  const { user } = useAuth();
  const userRole = user?.role || 'citizen';

  return (
    <aside className="sidebar" aria-label="Official Navigation Sidebar">
      {/* Official Government Emblem & Brand Header */}
      <div className="sidebar-header">
        <div className="gov-sidebar-brand">
          <div className="emblem-wrapper" title="National Ashoka Capital Seal">
            <GovEmblem size={34} className="text-gov-gold" />
          </div>
          <div className="brand-text-stack">
            <span className="brand-title">GovMesh</span>
            <span className="brand-marathi">शासकीय डेटा विनिमय</span>
          </div>
        </div>

        {/* Official Authority Seal Strip */}
        <div className="sidebar-authority-strip">
          <div className="authority-tricolor-line">
            <span className="tricolor-saffron" />
            <span className="tricolor-white" />
            <span className="tricolor-green" />
          </div>
          <div className="authority-label">
            <span>महाराष्ट्र शासन • GOVT OF MAHARASHTRA</span>
          </div>
        </div>
      </div>

      {/* Structured Departmental Navigation */}
      <nav className="sidebar-nav">
        {NAVIGATION_CONFIG.map((section, idx) => {
          const visibleItems = section.items.filter(
            item => !item.roles || item.roles.includes(userRole)
          );

          if (visibleItems.length === 0) return null;

          return (
            <div key={idx} className="nav-group">
              <div className="nav-group-title">{section.title}</div>
              <div className="nav-group-items">
                {visibleItems.map((item) => (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    end={item.path === '/'}
                    className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                    title={item.description}
                  >
                    <item.icon size={18} className="nav-item-icon" />
                    <span className="nav-item-label">{item.label}</span>
                  </NavLink>
                ))}
              </div>
            </div>
          );
        })}
      </nav>

      {/* Official Footer in Sidebar - Exact Matching Height & Level with Workspace Footer */}
      <div className="sidebar-footer">
        <div className="system-release">
          <div className="flex items-center gap-1.5">
            <span className="release-dot" />
            <span className="release-name">GovNet Engine v2.6</span>
          </div>
          <span className="sih-id">PS: SIH26129</span>
        </div>
      </div>
    </aside>
  );
};

