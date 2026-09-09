# GovMesh — Unified Interoperable Government Service Platform

GovMesh (SIH 26129) is a synthetic interoperability prototype for government-to-citizen service demonstrations. It coordinates dynamic consent gates, multi-protocol adapters (REST, SOAP/XML, Async Jobs), deterministic advisory rules, application-managed append-only audit records, and one constrained Property schema-recovery example.

---

## Architecture Overview

```
                           +------------------------+
                           |  Frontend Portal (UI)  |
                           |  http://localhost:3000 |
                           +-----------+------------+
                                       |
                                       v
                    +-------------------------------------+
                    |   GovMesh Backend Gateway (FastAPI) |
                    |        http://localhost:8000        |
                    +------------------+------------------+
                                       |
        +------------------+-----------+-----------+------------------+
        |                  |                       |                  |
        v                  v                       v                  v
+---------------+  +------------------+  +------------------+  +---------------+
| Identity Svc  |  | Municipality Svc |  |  Property Svc    |  |    Tax Svc    |
| (REST / 8101) |  |   (REST / 8102)  |  |  (SOAP / 8103)   |  | (Async / 8104)|
+---------------+  +------------------+  +------------------+  +---------------+
```

---

## Core Modules & Capabilities

1. **Dynamic Citizen Consent & Policy Gate** (`/consent`):
   - Fine-grained, department-scoped consent validation before any external service is queried.
   - Immediate policy denial if consent is absent, preventing unauthorized data queries.

2. **Multi-Protocol Protocol Adaptation** (`/service-request`):
   - Adapts to disparate legacy systems in parallel:
     - **Identity Service**: REST API with Bearer token authentication.
     - **Municipality Service**: REST API with X-API-Key authentication.
     - **Property Service**: Legacy SOAP protocol with XML Envelope request/response parsing.
     - **Tax Service**: Asynchronous two-step job submission and status polling.
   - Concurrent execution via `asyncio.gather` with batched database transactions.

3. **Deterministic Advisory Intelligence & Insights**:
   - Cross-system validation rules comparing normalized citizen records (e.g. `CROSS_SYSTEM_NAME_MISMATCH`, `CROSS_SYSTEM_ADDRESS_MISMATCH`, `TAX_CLEARANCE_NOT_CONFIRMED`).
   - Explainable rule-based insights without opaque black-box decisions.

4. **Interoperability Intelligence & Schema Evolution** (`/intelligence`):
   - Ingests and versions external department schemas (`v1` $\rightarrow$ `v2`).
   - Deterministic field-name mapping suggestions with heuristic match scores (`EXACT`, `SEMANTIC`, `TRANSFORMATION-REQUIRED`).
   - Human-in-the-loop governance: interactive **Pending** and **Approved** tabs for Data Stewards.
   - Breaking change impact analysis detecting renamed or removed fields across active services.

5. **Unified Timeline & Application-Managed Append-Only Audit Trail** (`/audit`, `/tracking`):
   - End-to-end `X-Correlation-ID` tracing across all microservice hops.
   - Field-level data lineage recording exact mappings (`Identity DB.full_name` $\rightarrow$ `GovMesh Response.citizen.name`).
   - Chronological unified timeline linking system events, policy decisions, and workflow step results.

---

## Port Allocation

| Component | Protocol | Local URL | Description |
| :--- | :--- | :--- | :--- |
| **Frontend Portal** | HTTP (Vite) | `http://localhost:3000` | Citizen & Admin unified dashboard |
| **Backend Core** | HTTP (FastAPI) | `http://localhost:8000` | REST API, OpenAPI docs at `/docs` |
| **Identity Service** | REST | `http://localhost:8101` | Simulated National Identity System |
| **Municipality Service** | REST | `http://localhost:8102` | Simulated Urban Municipal Registry |
| **Property Service** | SOAP / XML | `http://localhost:8103` | Simulated Land & Property Registry |
| **Tax Service** | Async REST | `http://localhost:8104` | Simulated Revenue & Tax Clearance |

---

## Quick Start Guide

For full installation and prerequisites, see [SETUP.md](SETUP.md).

### 1. One-Click Launch (Windows)

Double-click **`start_all.bat`** or run:

```powershell
.\start_all.ps1
```

### 2. Manual Commands (Windows PowerShell)

Open separate terminal windows for each process:

```powershell
# Terminal 1 — Identity Service
cd d:\govmesh\services\identity-service
..\..\backend\venv\Scripts\python.exe -m uvicorn app:app --reload --port 8101

# Terminal 2 — Municipality Service
cd d:\govmesh\services\municipality-service
..\..\backend\venv\Scripts\python.exe -m uvicorn app:app --reload --port 8102

# Terminal 3 — Property Service (SOAP)
cd d:\govmesh\services\property-service
..\..\backend\venv\Scripts\python.exe -m uvicorn app:app --reload --port 8103

# Terminal 4 — Tax Service (Async Job)
cd d:\govmesh\services\tax-service
..\..\backend\venv\Scripts\python.exe -m uvicorn app:app --reload --port 8104

# Terminal 5 — Backend Core Gateway
cd d:\govmesh\backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000

# Terminal 6 — Frontend Portal
cd d:\govmesh\frontend
npm run dev
```

---

## Test Suites

```powershell
# Run Backend Tests (88 Pytest test cases)
cd d:\govmesh\backend
.\venv\Scripts\python.exe -m pytest -q

# Run Frontend Tests (Vitest)
cd d:\govmesh\frontend
npm test

# Verify Production Build
npm run build
```

---

## Deterministic Demo Scenarios

Fictional test fixtures (`CIT-1001` to `CIT-1008`) demonstrate deterministic federated behavior:

| Citizen ID | Name | Scenario | System Behavior |
| :--- | :--- | :--- | :--- |
| `CIT-1001` | Asha Verma | Healthy & Consistent | Full consent, 4/4 departments pass, zero issues. |
| `CIT-1002` | Nila Rao | Tax Due | Flags `TAX_CLEARANCE_NOT_CONFIRMED` with outstanding amount. |
| `CIT-1003` | Omar Das | Missing Property | Graceful degradation; flags `DEPARTMENT_RESULTS_UNAVAILABLE`. |
| `CIT-1004` | Leela Sen | Missing Municipality | Graceful degradation without fake data generation. |
| `CIT-1005` | Ishan Kapoor | Missing Identity | Identity verification failure; no mock data fabricated. |
| `CIT-1006` | Kabir Jain | Name Mismatch | Flags `CROSS_SYSTEM_NAME_MISMATCH` across Property & Identity. |
| `CIT-1007` | Mira Bose | Address Mismatch | Flags `CROSS_SYSTEM_ADDRESS_MISMATCH` across Municipality & Identity. |
| `CIT-1008` | Tara Mehta | Pending Tax Job | Displays non-blocking pending status. |

For presentation flow, see [DEMO_GUIDE.md](DEMO_GUIDE.md).
