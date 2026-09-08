import React from 'react';
import { Card } from '../components/ui/Card';
import { StatusBadge } from '../components/ui/StatusBadge';

export const AppTracking = () => {
  const applications = [
    { id: 'APP-1092', type: 'Business Registration', applicant: 'Rajesh Kumar', date: '2026-09-08', status: 'Approved', dept: 'Multiple' },
    { id: 'APP-1091', type: 'Property Transfer', applicant: 'Priya Sharma', date: '2026-09-07', status: 'Pending Verification', dept: 'Property Reg.' },
    { id: 'APP-1090', type: 'Tax Clearance', applicant: 'Amit Patel', date: '2026-09-07', status: 'Approved', dept: 'Tax Dept.' },
    { id: 'APP-1089', type: 'Trade License', applicant: 'Neha Gupta', date: '2026-09-06', status: 'Denied (Consent Revoked)', dept: 'Municipality' },
    { id: 'APP-1088', type: 'Building Plan Approval', applicant: 'Sanjay Singh', date: '2026-09-05', status: 'In Process', dept: 'Municipality' },
    { id: 'APP-1087', type: 'Business Registration', applicant: 'Meera Reddy', date: '2026-09-05', status: 'Approved', dept: 'Multiple' },
  ];

  return (
    <div className="flex-col gap-6 flex fade-in">
      <div className="flex justify-between items-center">
        <p className="text-muted">Track and manage citizen service applications across all departments.</p>
        <div className="flex gap-2">
          <input type="text" placeholder="Search applications..." className="form-input py-2 text-sm w-64" />
          <button className="btn btn-primary">Filter</button>
        </div>
      </div>

      <Card>
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>App ID</th>
                <th>Type</th>
                <th>Applicant</th>
                <th>Submission Date</th>
                <th>Department</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {applications.map(app => (
                <tr key={app.id}>
                  <td className="font-mono text-xs">{app.id}</td>
                  <td className="font-medium">{app.type}</td>
                  <td>{app.applicant}</td>
                  <td className="text-muted text-sm">{app.date}</td>
                  <td><span className="badge badge-neutral">{app.dept}</span></td>
                  <td><StatusBadge status={app.status} /></td>
                  <td><button className="text-accent hover:text-accent-hover text-sm font-medium transition-colors cursor-pointer">View</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};
