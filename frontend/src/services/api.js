const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export const submitServiceRequest = async (citizenId, serviceType) => {
  const correlationId = crypto.randomUUID();
  const response = await fetch(`${API_BASE_URL}/service-requests`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Correlation-ID': correlationId,
    },
    body: JSON.stringify({
      citizen_id: citizenId,
      service_type: serviceType,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'An error occurred while submitting the request.');
  }

  return response.json();
};

export const grantConsent = async (citizenId, serviceType, departments) => {
  const response = await fetch(`${API_BASE_URL}/consent`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      citizen_id: citizenId,
      service_type: serviceType,
      departments: departments,
      ttl_hours: 24
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to grant consent.');
  }
  return response.json();
};

export const revokeConsent = async (consentId) => {
  const response = await fetch(`${API_BASE_URL}/consent/${consentId}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to revoke consent.');
  }
  return response.json();
};

export const checkActiveConsent = async (citizenId, serviceType) => {
  const response = await fetch(`${API_BASE_URL}/consent/${citizenId}/${serviceType}`);
  if (response.status === 404) return null;
  if (!response.ok) {
    throw new Error('Failed to check consent status.');
  }
  return response.json();
};

export const checkHealth = async () => {
  // health is usually at /health, not /api/v1/health
  const response = await fetch('/health');
  if (!response.ok) {
    throw new Error('Health check failed');
  }
  return response.json();
};

export const fetchSystems = async () => {
  const response = await fetch(`${API_BASE_URL}/systems`);
  if (!response.ok) {
    throw new Error('Failed to fetch systems.');
  }
  return response.json();
};

export const fetchSystemsMonitoring = async () => {
  const response = await fetch(`${API_BASE_URL}/systems/monitoring`);
  if (!response.ok) {
    throw new Error('Failed to fetch monitoring metrics.');
  }
  return response.json();
};

// ── Workflow APIs ────────────────────────────────────────────────────

export const fetchServiceRequests = async () => {
  const response = await fetch(`${API_BASE_URL}/service-requests`);
  if (!response.ok) {
    throw new Error('Failed to fetch service requests.');
  }
  return response.json();
};

export const fetchWorkflowStatus = async (workflowId) => {
  const response = await fetch(`${API_BASE_URL}/workflows/${workflowId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch workflow status.');
  }
  return response.json();
};

export const fetchWorkflowTimeline = async (workflowId) => {
  const response = await fetch(`${API_BASE_URL}/workflows/${workflowId}/timeline`);
  if (!response.ok) {
    throw new Error('Failed to fetch workflow timeline.');
  }
  return response.json();
};

export const fetchWorkflowByRequest = async (requestId) => {
  const response = await fetch(`${API_BASE_URL}/workflows/by-request/${requestId}`);
  if (response.status === 404) return null;
  if (!response.ok) {
    throw new Error('Failed to fetch workflow for request.');
  }
  return response.json();
};

export const startWorkflow = async (serviceRequestId) => {
  const response = await fetch(`${API_BASE_URL}/workflows/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ service_request_id: serviceRequestId }),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to start workflow.');
  }
  return response.json();
};

// ── Audit & Lineage APIs ─────────────────────────────────────────────

export const fetchGlobalAuditLogs = async (limit = 50) => {
  const response = await fetch(`${API_BASE_URL}/audit?limit=${limit}`);
  if (!response.ok) {
    throw new Error('Failed to fetch audit logs.');
  }
  return response.json();
};

export const fetchAuditLogsByCorrelation = async (correlationId) => {
  const response = await fetch(`${API_BASE_URL}/audit/correlation/${correlationId}`);
  if (response.status === 404) return [];
  if (!response.ok) {
    throw new Error('Failed to fetch audit logs for correlation ID.');
  }
  return response.json();
};

export const fetchLineage = async (correlationId) => {
  const response = await fetch(`${API_BASE_URL}/lineage/${correlationId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch data lineage.');
  }
  return response.json();
};

export const fetchUnifiedTimeline = async (requestId) => {
  const response = await fetch(`${API_BASE_URL}/timeline/${requestId}`);
  if (response.status === 404) return null;
  if (!response.ok) {
    throw new Error('Failed to fetch unified timeline.');
  }
  return response.json();
};

// ── Intelligence APIs ─────────────────────────────────────────────

export const fetchSchemas = async () => {
  const response = await fetch(`${API_BASE_URL}/intelligence/schemas`);
  if (!response.ok) throw new Error('Failed to fetch schemas.');
  return response.json();
};

export const fetchSuggestions = async () => {
  const response = await fetch(`${API_BASE_URL}/intelligence/suggestions`);
  if (!response.ok) throw new Error('Failed to fetch suggestions.');
  return response.json();
};

export const approveSuggestion = async (suggestionId) => {
  const response = await fetch(`${API_BASE_URL}/intelligence/suggestions/${suggestionId}/approve`, { method: 'POST' });
  if (!response.ok) throw new Error('Failed to approve suggestion.');
  return response.json();
};

export const rejectSuggestion = async (suggestionId) => {
  const response = await fetch(`${API_BASE_URL}/intelligence/suggestions/${suggestionId}/reject`, { method: 'POST' });
  if (!response.ok) throw new Error('Failed to reject suggestion.');
  return response.json();
};

export const fetchImpactAnalysis = async () => {
  const response = await fetch(`${API_BASE_URL}/intelligence/impact`);
  if (!response.ok) throw new Error('Failed to fetch impact analysis.');
  return response.json();
};

export const triggerDemoScenario = async () => {
  const response = await fetch(`${API_BASE_URL}/intelligence/demo/trigger`, { method: 'POST' });
  if (!response.ok) throw new Error('Failed to trigger demo scenario.');
  return response.json();
};
