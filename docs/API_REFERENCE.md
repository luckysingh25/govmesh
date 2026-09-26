# GovMesh — REST API Contract & Specification

**Base Gateway URL:** `http://localhost:8000/api/v1`  
**Interactive Swagger UI:** `http://localhost:8000/docs`  
**OpenAPI Specification:** `http://localhost:8000/openapi.json`  

---

## 1. Global Request Headers

Every request processed by GovMesh accepts and propagates the following headers:

| Header | Type | Description |
| :--- | :--- | :--- |
| `Authorization` | `string` | `Bearer <JWT_ACCESS_TOKEN>` required for protected endpoints. |
| `X-Correlation-ID` | `string (UUID)` | Unique trace ID for end-to-end distributed transaction tracing. If omitted, the gateway auto-generates one. |
| `Content-Type` | `string` | `application/json` |

---

## 2. Authentication & Authorization Endpoints

### 2.1 User Login
`POST /auth/login`
Authenticates a user and issues a signed, short-lived JWT token.

* **Request Content-Type:** `application/x-www-form-urlencoded`
* **Request Body:**
  ```text
  username=admin@govmesh.gov.in&password=Admin@123
  ```
* **Success Response (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
    "token_type": "bearer",
    "role": "admin",
    "citizen_id": null
  }
  ```

### 2.2 Get Current Session
`GET /auth/me`
* **Headers:** `Authorization: Bearer <TOKEN>`
* **Success Response (200 OK):** Returns current user email, role, and citizen binding.

---

## 3. Service Requests & Execution Endpoints

### 3.1 Submit Service Request
`POST /service-requests`
Initiates a multi-department federated query.

* **Request Body:**
  ```json
  {
    "citizen_id": "CIT-1001",
    "service_type": "business_registration"
  }
  ```
* **Response: Policy Approval (200 OK):**
  ```json
  {
    "request_id": "REQ-7F9B1E4A",
    "correlation_id": "4b12bb79-a7a4-45ba-9fcc-d2834d362810",
    "overall_status": "success",
    "policy_decision": "approved",
    "citizen": {
      "citizen_id": "CIT-1001",
      "name": "Asha Verma",
      "address": "42 Civil Lines, Nagpur, MH"
    },
    "identity": {
      "status": "success",
      "protocol": "REST / Bearer",
      "duration_ms": 32,
      "data": { "verification_status": "verified" }
    },
    "property": {
      "status": "success",
      "protocol": "SOAP 1.2 / XML",
      "duration_ms": 54,
      "data": { "property_id": "PROP-4011", "owner_name": "Asha Verma" }
    },
    "municipality": {
      "status": "success",
      "protocol": "REST / X-API-Key",
      "duration_ms": 28,
      "data": { "registration_status": "active" }
    },
    "tax": {
      "status": "success",
      "protocol": "Async 2-Phase",
      "duration_ms": 85,
      "data": { "clearance_status": "cleared", "outstanding_amount": 0.0 }
    },
    "insights": []
  }
  ```
* **Response: Policy Denial (200 OK / overall_status: denied):**
  ```json
  {
    "request_id": "REQ-2A849BC1",
    "overall_status": "denied",
    "policy_decision": "denied",
    "detail": "Citizen consent for business_registration has not been granted or has expired."
  }
  ```

### 3.2 List Service Requests
`GET /service-requests`
Returns the recent execution history. Citizens see only their own requests; officers see organization-wide requests.

### 3.3 Service Metrics
`GET /service-requests/metrics`
Returns aggregate statistics for requests processed today, completion rates, average duration in ms, and active citizens.

---

## 4. Consent Management Endpoints (DPDP Act 2023)

### 4.1 Grant Purpose-Bound Consent
`POST /consent`
* **Request Body:**
  ```json
  {
    "citizen_id": "CIT-1001",
    "service_type": "business_registration",
    "departments": ["identity", "municipality", "property", "tax"],
    "ttl_hours": 24
  }
  ```
* **Response (200 OK):** Returns created consent receipt with cryptographic hash and expiry timestamp.

### 4.2 Check Active Consent
`GET /consent/{citizen_id}/{service_type}`
Returns the active consent record or 404 if not found/expired.

### 4.3 Revoke Consent
`DELETE /consent/{consent_id}`
Immediately invalidates consent, causing future requests for this scope to be blocked at the policy gate.

---

## 5. Schema Evolution & Intelligence Endpoints

### 5.1 Ingest System Schema
`POST /intelligence/schemas/ingest`
*(Requires role: `admin` or `data_steward`)*
* Ingests a new JSON or XML schema from an external department, creates an incremented version, and triggers impact analysis.

### 5.2 List Mapping Suggestions
`GET /intelligence/suggestions?status=pending`
Returns AI-assisted heuristic mapping suggestions with confidence scores and match types (`EXACT`, `SEMANTIC`, `TRANSFORMATION-REQUIRED`).

### 5.3 Approve Mapping Suggestion
`POST /intelligence/suggestions/{id}/approve`
*(Requires role: `admin` or `data_steward`)*
Applies human governance to activate a proposed field mapping. Logs the event to the immutable audit trail.

### 5.4 Trigger Property v2 Upgrade Demo
`POST /intelligence/demo/trigger-upgrade`
Simulates the Property Department upgrading to v2 (renaming `ownerName` $\rightarrow$ `propertyOwnerName`), generating broken mapping impact and a high-confidence mapping proposal.

---

## 6. Systems Monitoring & Audit Trail

### 6.1 Real-Time Microservice Health
`GET /systems`
Pings all 4 external microservices (8101, 8102, 8103, 8104) and returns reachability, response latency in ms, and uptime status.

### 6.2 Audit Logs & Data Lineage
`GET /audit?limit=50`
Returns chronologically ordered audit events with actor emails, timestamps, and target actions.

`GET /audit/lineage/{request_id}`
Returns exact field-level data provenance mapping every returned attribute back to its originating department database field.
