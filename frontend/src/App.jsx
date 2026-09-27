import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { MainLayout } from './components/layout/MainLayout';

// Pages
import { Dashboard } from './pages/Dashboard';
import { ServiceRequest } from './pages/ServiceRequest';
import { AppTracking } from './pages/AppTracking';
import { Systems } from './pages/Systems';
import { Workflow } from './pages/Workflow';
import { ConsentPolicy } from './pages/ConsentPolicy';
import { AuditActivity } from './pages/AuditActivity';
import { Health } from './pages/Health';
import { Intelligence } from './pages/Intelligence';
import { Login } from './pages/Login';
import { AuthProvider, useAuth } from './auth/AuthContext';

import './index.css';

import { AccessDenied } from './components/common/AccessDenied';

const Protected = ({ children, allowedRoles }) => {
  const { user, loading } = useAuth();
  if (loading) return <div className="empty-state">Checking secure session…</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <AccessDenied allowedRoles={allowedRoles} />;
  }
  return children;
};

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Protected><MainLayout /></Protected>}>
            <Route index element={<Dashboard />} />
            <Route path="service-request" element={<Protected allowedRoles={['citizen', 'admin']}><ServiceRequest /></Protected>} />
            <Route path="tracking" element={<AppTracking />} />
            <Route path="systems" element={<Protected allowedRoles={['admin', 'data_steward']}><Systems /></Protected>} />
            <Route path="workflow" element={<Protected allowedRoles={['admin']}><Workflow /></Protected>} />
            <Route path="consent" element={<Protected allowedRoles={['citizen', 'admin']}><ConsentPolicy /></Protected>} />
            <Route path="audit" element={<Protected allowedRoles={['admin', 'data_steward']}><AuditActivity /></Protected>} />
            <Route path="health" element={<Protected allowedRoles={['admin']}><Health /></Protected>} />
            <Route path="intelligence" element={<Protected allowedRoles={['admin', 'data_steward']}><Intelligence /></Protected>} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
