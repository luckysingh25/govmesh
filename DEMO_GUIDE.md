# GovMesh Deterministic Demo Guide

## Before the Demo

1. Start all services using either:
   - **One-Click**: Run `start_all.bat` (or `.\start_all.ps1`) from the repository root.
   - **Manual**: Follow the multi-terminal commands in [SETUP.md](SETUP.md).
2. Confirm health on ports 8000, 8101, 8102, 8103, and 8104.
3. Open `http://localhost:3000`.

---

## Recommended Presentation Sequence

### 1. Consent Policy Gate
1. Navigate to **Service Request** (`/service-request`).
2. Submit a request for `CIT-1001` *before* granting consent.
3. Show that the policy gate immediately returns a clean denial without contacting any external department.
4. Go to **Consent & Policy** (`/consent`), grant consent for `CIT-1001` on `business_registration`, and resubmit.

---

### 2. Healthy Interoperability
- Use `CIT-1001` (Asha Verma).
- All 4 departments succeed concurrently (Identity REST, Municipality REST, Property SOAP, Tax Async).
- The Advisory Insights section confirms clean, consistent records across all departments.

---

### 3. Explainable Cross-System Advisory Scenarios
Demonstrate deterministic cross-system edge cases using pre-seeded fixtures:

| Citizen ID | Name | Demonstration & Outcome |
| :--- | :--- | :--- |
| `CIT-1002` | Nila Rao | Tax status is `DUE` (outstanding `14,500.5`); triggers `TAX_CLEARANCE_NOT_CONFIRMED`. |
| `CIT-1003` | Omar Das | Property record absent; partial result with `DEPARTMENT_RESULTS_UNAVAILABLE`. |
| `CIT-1004` | Leela Sen | Municipal record absent; partial result without fake data generation. |
| `CIT-1005` | Ishan Kapoor | Identity record absent; fails gracefully. |
| `CIT-1006` | Kabir Jain | Property owner differs (`Kabir A. Jain` vs `Kabir Jain`); triggers `CROSS_SYSTEM_NAME_MISMATCH`. |
| `CIT-1007` | Mira Bose | Municipal address differs; triggers `CROSS_SYSTEM_ADDRESS_MISMATCH`. |
| `CIT-1008` | Tara Mehta | Asynchronous tax job still processing; returns clean pending state. |

Explain that all rules are deterministic, explainable integration validations—not black-box AI decisions.

---

### 4. Multi-Protocol Legacy Adaptation
Show how GovMesh federates heterogeneous government protocols into one unified response:
- **Identity & Municipality**: JSON REST with Bearer / API Key headers.
- **Property**: Legacy SOAP/XML with envelope parsing.
- **Tax**: Asynchronous job submission and polling.

---

### 5. Live Monitoring, Lineage & Unified Timeline
1. Open **Systems & Depts** (`/systems`): displays live reachability and latency for all 4 microservices.
2. Open **App Tracking** (`/tracking`): view the request's immutable `X-Correlation-ID`.
3. Open **Audit Activity** (`/audit`): inspect field-level data lineage (e.g. `Identity DB.full_name` $\rightarrow$ `GovMesh Response.citizen.name`).
4. Click on any application to view the chronological **Unified Timeline** combining audit events and workflow step transitions.

---

### 6. Interoperability Intelligence & Schema Evolution
1. Open **Intelligence Mapping** (`/intelligence`).
2. Click **Trigger Upgrade Demo**:
   - Demonstrates Property System upgrading from Version 1 (`ownerName`) to Version 2 (`propertyOwnerName`).
3. Show **Impact Analysis**:
   - Flags breaking change: `Affected: Business Registration (Property System Integration) — Field mapping for ['ownerName'] is now broken`.
4. Show **Mapping Approvals**:
   - View newly suggested field mapping for `propertyOwnerName -> citizen.name` (95% confidence).
   - Click **Approve** to demonstrate real-time human governance, and switch to the **Approved** tab to see the verified active mapping.

---

## Technical Architecture Highlights

- **Concurrency**: Connector queries run in parallel via `asyncio.gather` with batched database transactions.
- **Graceful Degradation**: Microservice failure isolates the step without halting the entire platform or generating hallucinated citizen records.
- **Data Sovereignty**: PostgreSQL stores workflow orchestration, consent, mapping, and audit metadata—not permanent centralized copies of departmental databases.
- **Security**: Strict role-based access control (RBAC), bcrypt-hashed passwords, and isolated demo endpoints.
