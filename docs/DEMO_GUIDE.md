# GovMesh Deterministic Demo Guide

> 🏆 **Jury Members & Evaluators:** For a complete, step-by-step scoring flow with 1-click test procedures, see the **[SIH 2026 Judges & Evaluator Testing Guide](../JUDGES_TESTING_GUIDE.md)**.

## Before the Demo

1. Start all services using either:
   - **One-Click**: Run `start_all.bat` (or `.\start_all.ps1`) from the repository root.
   - **Manual**: Follow the multi-terminal commands in [SETUP.md](SETUP.md).
2. Confirm health on ports 8000, 8101, 8102, 8103, and 8104.
3. Open `http://localhost:3000`.

---

## ⚡ Fast-Track Evaluator 1-Click Demo Hub

In the web interface (`http://localhost:3000`), a dedicated **Evaluator Demo Hub** banner is pinned to the top of every screen. Evaluators and jury members can run complete, deterministic live verification scenarios with a single click:

| Preset Button | Scenario Tested | What Evaluators See |
| :--- | :--- | :--- |
| 🟢 **Golden Path (`CIT-1001`)** | Asha Verma — Full Success | All 4 departments (REST, SOAP, Async) respond concurrently; clean advisory score; 100% verified status. |
| 🔴 **Zero-Trust Denial** | Consent Gate Enforcement | Immediate `403 Forbidden` response without contacting any external departmental server. Zero network leaks. |
| 🟡 **Graceful Degradation (`CIT-1003`)** | Omar Das — Missing Property | Property service returns absent; gateway returns clean partial result with explainable advisory `DEPARTMENT_RESULTS_UNAVAILABLE`. **Zero fake data generation.** |
| 🟠 **Name Conflict (`CIT-1006`)** | Kabir Jain — Discrepancy | Cross-system discrepancy detected between Identity (`Kabir Jain`) and Property (`Kabir A. Jain`). Triggers deterministic advisory code `CROSS_SYSTEM_NAME_MISMATCH`. |
| 🟣 **Schema Evolution (v1 $\rightarrow$ v2)** | Breaking Upstream Change | Simulates Property System field rename (`ownerName` $\rightarrow$ `propertyOwnerName`). Interactive Data Steward panel for real-time review and approval. |

---

## Detailed Step-by-Step Walkthrough

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
2. Open **App Tracking** (`/tracking`): view the request's propagated `X-Correlation-ID`.
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
- **Stored snapshots**: PostgreSQL stores bounded normalized execution snapshots and synthetic raw payload evidence with workflow, consent, mapping, lineage, and audit metadata. This prototype does not yet implement automated retention deletion.
- **Security**: Role and ownership checks, PBKDF2-SHA256 password hashes, short-lived signed tokens, and explicitly enabled demo controls.
