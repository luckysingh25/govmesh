import React from 'react';

export const StatusBadge = ({ status, className = '' }) => {
  let badgeClass = 'badge-neutral';
  let label = status;

  if (typeof status === 'string') {
    const s = status.toLowerCase();
    if (s.includes('success') || s.includes('completed') || s.includes('allow') || s === 'ok') {
      badgeClass = 'badge-success';
    } else if (s.includes('fail') || s.includes('error') || s.includes('denied') || s.includes('revoke')) {
      badgeClass = 'badge-error';
    } else if (s.includes('partial') || s.includes('pending') || s.includes('process')) {
      badgeClass = 'badge-warning';
    }
  }

  return (
    <span className={`badge ${badgeClass} ${className}`}>
      {label}
    </span>
  );
};
