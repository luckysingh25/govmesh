import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { ServiceRequest } from './ServiceRequest';

const api = vi.hoisted(() => ({
  fetchServiceDefinitions: vi.fn(), fetchDemoScenarios: vi.fn(), submitServiceRequest: vi.fn(), resumeWorkflow: vi.fn(),
}));
vi.mock('../services/api', () => api);
vi.mock('../auth/AuthContext', () => ({ useAuth: () => ({ user: { role:'citizen', citizen_id:'CIT-1001' } }) }));

describe('ServiceRequest scenarios', () => {
  beforeEach(() => {
    api.fetchServiceDefinitions.mockResolvedValue([{ id:'business_registration', label:'Business Registration', description:'demo', departments:[] }]);
    api.fetchDemoScenarios.mockResolvedValue([{ scenario_name:'healthy_consistent', citizen_id:'CIT-1001', service_type:'business_registration', explanation:'Healthy fictional records', expected_overall_status:'success', selectable:true }]);
    api.submitServiceRequest.mockReset();
  });

  it('prefills a selectable scenario without granting consent or fabricating an actual result', async () => {
    render(<ServiceRequest />);
    await waitFor(() => expect(screen.getByText(/healthy consistent/i)).toBeTruthy());
    fireEvent.change(screen.getByLabelText('Scenario selector'), { target:{ value:'healthy_consistent' } });
    expect(screen.getByText('Expected scenario')).toBeTruthy();
    expect(screen.getByText(/Healthy fictional records/)).toBeTruthy();
    expect(screen.getByText('No Active Request')).toBeTruthy();
    expect(api.submitServiceRequest).not.toHaveBeenCalled();
  });
});
