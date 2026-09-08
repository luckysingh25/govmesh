import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
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

import './index.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="service-request" element={<ServiceRequest />} />
          <Route path="tracking" element={<AppTracking />} />
          <Route path="systems" element={<Systems />} />
          <Route path="workflow" element={<Workflow />} />
          <Route path="consent" element={<ConsentPolicy />} />
          <Route path="audit" element={<AuditActivity />} />
          <Route path="health" element={<Health />} />
          <Route path="intelligence" element={<Intelligence />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
