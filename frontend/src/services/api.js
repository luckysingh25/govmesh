const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';
const TOKEN_KEY = 'govmesh_access_token';

export const getStoredToken = () => sessionStorage.getItem(TOKEN_KEY);
export const clearStoredToken = () => sessionStorage.removeItem(TOKEN_KEY);

const apiFetch = (url, options = {}) => {
  const token = getStoredToken();
  const headers = new Headers(options.headers || {});
  if (token) headers.set('Authorization', `Bearer ${token}`);
  return fetch(url, { ...options, headers });
};

export const login = async (email, password) => {
  const form = new URLSearchParams({ username: email, password });
  const response = await fetch(`${API_BASE_URL}/auth/login`, { method: 'POST', body: form });
  if (!response.ok) throw new Error('Incorrect email or password');
  const data = await response.json();
  sessionStorage.setItem(TOKEN_KEY, data.access_token);
  return data;
};

export const fetchCurrentUser = async () => {
  const response = await apiFetch(`${API_BASE_URL}/auth/me`);
  if (!response.ok) throw new Error('Session expired');
  return response.json();
};

export const submitServiceRequest = async (citizenId, serviceType) => {
  const correlationId = crypto.randomUUID();
  const response = await apiFetch(`${API_BASE_URL}/service-requests`, {
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

export const grantConsent = async (citizenId, serviceType, departments, ttlHours = 24) => {
  const response = await apiFetch(`${API_BASE_URL}/consent`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      citizen_id: citizenId,
      service_type: serviceType,
      departments: departments,
      ttl_hours: ttlHours
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to grant consent.');
  }
  return response.json();
};

export const revokeConsent = async (consentId) => {
  const response = await apiFetch(`${API_BASE_URL}/consent/${consentId}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to revoke consent.');
  }
  return response.json();
};

export const checkActiveConsent = async (citizenId, serviceType) => {
  const response = await apiFetch(`${API_BASE_URL}/consent/${citizenId}/${serviceType}`);
  if (response.status === 404) return null;
  if (!response.ok) {
    throw new Error('Failed to check consent status.');
  }
  return response.json();
};

export const checkHealth = async () => {
  // health is usually at /health, not /api/v1/health
  const response = await apiFetch('/health');
  if (!response.ok) {
    throw new Error('Health check failed');
  }
  return response.json();
};

export const fetchSystems = async () => {
  const response = await apiFetch(`${API_BASE_URL}/systems`);
  if (!response.ok) {
    throw new Error('Failed to fetch systems.');
  }
  return response.json();
};

export const fetchSystemsMonitoring = async () => {
  const response = await apiFetch(`${API_BASE_URL}/systems/monitoring`);
  if (!response.ok) {
    throw new Error('Failed to fetch monitoring metrics.');
  }
  return response.json();
};

// ── Workflow APIs ────────────────────────────────────────────────────

export const fetchServiceRequests = async () => {
  const response = await apiFetch(`${API_BASE_URL}/service-requests`);
  if (!response.ok) {
    throw new Error('Failed to fetch service requests.');
  }
  return response.json();
};

export const fetchWorkflowStatus = async (workflowId) => {
  const response = await apiFetch(`${API_BASE_URL}/workflows/${workflowId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch workflow status.');
  }
  return response.json();
};

export const fetchWorkflowTimeline = async (workflowId) => {
  const response = await apiFetch(`${API_BASE_URL}/workflows/${workflowId}/timeline`);
  if (!response.ok) {
    throw new Error('Failed to fetch workflow timeline.');
  }
  return response.json();
};

export const fetchWorkflowByRequest = async (requestId) => {
  const response = await apiFetch(`${API_BASE_URL}/workflows/by-request/${requestId}`);
  if (response.status === 404) return null;
  if (!response.ok) {
    throw new Error('Failed to fetch workflow for request.');
  }
  return response.json();
};

export const startWorkflow = async (serviceRequestId) => {
  const response = await apiFetch(`${API_BASE_URL}/workflows/start`, {
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
  const response = await apiFetch(`${API_BASE_URL}/audit?limit=${limit}`);
  if (!response.ok) {
    throw new Error('Failed to fetch audit logs.');
  }
  return response.json();
};

export const fetchAuditLogsByCorrelation = async (correlationId) => {
  const response = await apiFetch(`${API_BASE_URL}/audit/correlation/${correlationId}`);
  if (response.status === 404) return [];
  if (!response.ok) {
    throw new Error('Failed to fetch audit logs for correlation ID.');
  }
  return response.json();
};

export const fetchLineage = async (correlationId) => {
  const response = await apiFetch(`${API_BASE_URL}/lineage/${correlationId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch data lineage.');
  }
  return response.json();
};

export const fetchUnifiedTimeline = async (requestId) => {
  const response = await apiFetch(`${API_BASE_URL}/timeline/${requestId}`);
  if (response.status === 404) return null;
  if (!response.ok) {
    throw new Error('Failed to fetch unified timeline.');
  }
  return response.json();
};

// ── Intelligence APIs ─────────────────────────────────────────────

export const fetchSchemas = async () => {
  const response = await apiFetch(`${API_BASE_URL}/intelligence/schemas`);
  if (!response.ok) throw new Error('Failed to fetch schemas.');
  return response.json();
};

export const fetchSuggestions = async (status = 'pending') => {
  const response = await apiFetch(`${API_BASE_URL}/intelligence/suggestions?status=${status}`);
  if (!response.ok) throw new Error('Failed to fetch suggestions.');
  return response.json();
};

export const approveSuggestion = async (suggestionId) => {
  const response = await apiFetch(`${API_BASE_URL}/intelligence/suggestions/${suggestionId}/approve`, {
    method: 'POST'
  });
  if (!response.ok) throw new Error('Failed to approve suggestion.');
  return response.json();
};

export const rejectSuggestion = async (suggestionId) => {
  const response = await apiFetch(`${API_BASE_URL}/intelligence/suggestions/${suggestionId}/reject`, {
    method: 'POST'
  });
  if (!response.ok) throw new Error('Failed to reject suggestion.');
  return response.json();
};

export const fetchImpactAnalysis = async () => {
  const response = await apiFetch(`${API_BASE_URL}/intelligence/impact`);
  if (!response.ok) throw new Error('Failed to fetch impact analysis.');
  return response.json();
};

export const triggerDemoScenario = async () => {
  const response = await apiFetch(`${API_BASE_URL}/intelligence/demo/trigger`, { method: 'POST' });
  if (!response.ok) throw new Error('Failed to trigger demo scenario.');
  return response.json();
};

export const fetchRequestMetrics = async () => {
  const response = await apiFetch(`${API_BASE_URL}/service-requests/metrics`);
  if (!response.ok) throw new Error('Failed to fetch dashboard aggregates.');
  return response.json();
};

export const fetchServiceDefinitions = async () => {
  const response = await apiFetch(`${API_BASE_URL}/service-requests/definitions`);
  if (!response.ok) throw new Error('Failed to load canonical service definitions.');
  return response.json();
};

export const fetchDemoScenarios = async () => {
  const response = await apiFetch(`${API_BASE_URL}/service-requests/demo/scenarios`);
  if (!response.ok) throw new Error('Failed to load fictional scenarios.');
  return response.json();
};

export const resumeWorkflow = async (requestId) => {
  const response = await apiFetch(`${API_BASE_URL}/workflows/by-request/${requestId}/resume`, { method: 'POST' });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Unable to resume workflow.');
  }
  return response.json();
};

export const setPropertySchema = async (version) => {
  const response = await apiFetch(`${API_BASE_URL}/intelligence/demo/property/schema/${version}`, { method: 'PUT' });
  if (!response.ok) throw new Error('Property schema control is unavailable.');
  return response.json();
};

export const setPropertyAvailability = async (available) => {
  const response = await apiFetch(`${API_BASE_URL}/intelligence/demo/property/availability/${available}`, { method: 'PUT' });
  if (!response.ok) throw new Error('Property availability control is unavailable.');
  return response.json();
};
