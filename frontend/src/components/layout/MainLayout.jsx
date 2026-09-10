import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Bell, UserCircle, LogOut } from 'lucide-react';
import { useAuth } from '../../auth/AuthContext';

export const MainLayout = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  
  // Format pathname to title
  const title = location.pathname === '/' 
    ? 'Dashboard Overview' 
    : location.pathname.substring(1)
        .split('-')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-wrapper">
        <header className="topbar">
          <h1 className="page-title">{title}</h1>
          <div className="topbar-actions">
            <button className="btn btn-outline" style={{ padding: '0.5rem', borderRadius: '50%' }}>
              <Bell size={20} />
            </button>
            <div className="flex items-center gap-2 text-sm text-muted">
              <UserCircle size={24} className="text-primary" />
              <span>{user?.email} · {user?.role}</span>
              <button className="btn btn-outline" onClick={logout}><LogOut size={15} /> Logout</button>
            </div>
          </div>
        </header>
        <main className="main-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
