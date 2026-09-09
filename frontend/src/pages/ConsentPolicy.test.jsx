import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { ConsentPolicy } from './ConsentPolicy';

const api = vi.hoisted(() => ({ checkActiveConsent:vi.fn(), fetchServiceDefinitions:vi.fn(), grantConsent:vi.fn(), revokeConsent:vi.fn() }));
vi.mock('../services/api', () => api);
vi.mock('../auth/AuthContext', () => ({ useAuth: () => ({ user:{ role:'citizen', citizen_id:'CIT-1001' } }) }));

describe('Consent selection state', () => {
  it('clears state and ignores a stale response after the service changes', async () => {
    let resolveOld;
    api.checkActiveConsent.mockReturnValue(new Promise(resolve => { resolveOld = resolve; }));
    api.fetchServiceDefinitions.mockResolvedValue([
      { id:'business_registration', label:'Business Registration', departments:[{id:'identity',reason:'Identity'}] },
      { id:'tax_clearance', label:'Tax Clearance', departments:[{id:'tax',reason:'Tax'}] },
    ]);
    render(<ConsentPolicy />);
    await waitFor(() => expect(screen.getByText('Tax Clearance')).toBeTruthy());
    fireEvent.change(screen.getByLabelText('Service Type'), { target:{ value:'tax_clearance' } });
    resolveOld({ id:99, citizen_id:'CIT-1001', service_type:'business_registration', departments:['identity'], expires_at:new Date().toISOString() });
    await Promise.resolve();
    expect(screen.queryByText('Consent Active')).toBeNull();
  });
});
