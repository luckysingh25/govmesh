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
