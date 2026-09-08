import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  FileText, 
  Activity, 
  Server, 
  GitMerge, 
  ShieldCheck, 
  History,
  BrainCircuit
} from 'lucide-react';

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/service-request', label: 'Service Request', icon: FileText },
  { path: '/tracking', label: 'App Tracking', icon: Activity },
  { path: '/systems', label: 'Systems & Depts', icon: Server },
  { path: '/workflow', label: 'Workflow Process', icon: GitMerge },
  { path: '/consent', label: 'Consent & Policy', icon: ShieldCheck },
  { path: '/audit', label: 'Audit Activity', icon: History },
  { path: '/health', label: 'System Health', icon: Activity },
  { path: '/intelligence', label: 'Intelligence Mapping', icon: BrainCircuit },
];

export const Sidebar = () => {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="logo">
          🏛️ GovMesh
        </div>
      </div>
      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <item.icon size={20} />
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
};
