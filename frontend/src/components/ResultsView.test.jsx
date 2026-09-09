import React from 'react';
import '@testing-library/jest-dom/vitest';
import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import ResultsView from './ResultsView';


const baseResult = {
  request_id: 'REQ-1',
  correlation_id: 'CORR-1',
  overall_status: 'completed',
  citizen: { citizen_id: 'CIT-1001', name: 'Aarav Sharma' },
  identity: { status: 'success', data: { full_name: 'Aarav Sharma' } },
  property: { status: 'not_required', data: {} },
  municipality: { status: 'not_required', data: {} },
  tax: { status: 'not_required', data: {} },
};


describe('ResultsView', () => {
  it('renders warning and info advisory findings with the disclaimer', () => {
    render(<ResultsView result={{
      ...baseResult,
      insights: [
        { rule_id: 'CROSS_SYSTEM_NAME_MISMATCH', severity: 'warning', message: 'Names differ.' },
        { rule_id: 'TAX_CLEARANCE_NOT_CONFIRMED', severity: 'info', message: 'Tax is pending.' },
      ],
    }} />);

    expect(screen.getByText('CROSS_SYSTEM_NAME_MISMATCH')).toBeInTheDocument();
    expect(screen.getByText('TAX_CLEARANCE_NOT_CONFIRMED')).toBeInTheDocument();
    expect(screen.getByText('Advisory only — verify with the responsible department before taking action.')).toBeInTheDocument();
  });

  it('renders a healthy empty state', () => {
    render(<ResultsView result={{ ...baseResult, insights: [] }} />);

    expect(screen.getByText(/No advisory issues were detected/)).toBeInTheDocument();
  });

  it('handles missing optional citizen and department values without null text', () => {
    render(<ResultsView result={{
      ...baseResult,
      citizen: {},
      identity: { status: 'failed', data: { full_name: null }, error: null },
      insights: [],
    }} />);

    expect(screen.getByText('Citizen details are unavailable.')).toBeInTheDocument();
    expect(screen.getByText('Department result: failed.')).toBeInTheDocument();
    expect(screen.queryByText('null')).not.toBeInTheDocument();
  });
});
