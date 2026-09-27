# 🏛️ GovMesh — SIH 2026 Judges & Evaluator Testing Guide

> **Smart India Hackathon 2026** | **Problem Statement: SIH26129**  
> **Sponsoring Authority:** Government of Maharashtra (General Administration Department / DIT)  
> **Topic:** *System Integration and Interoperability Among Government Digital Platforms*  
> **Team:** The Code Blooded  
> **Solution:** GovMesh — Consent-Aware Federated Interoperability Mesh  

---

## 📋 Executive Summary for the Jury

State governments operate dozens of siloed digital platforms across contrasting technologies—modern JSON REST APIs, 20-year-old SOAP/XML land registries, and asynchronous tax engines. Citizens applying for composite services (e.g., Business Registration or Property Transfer) are forced to repeatedly submit the same documents and visit multiple departments.

**GovMesh is NOT another citizen portal.**  
GovMesh is the **governed interoperability middleware beneath state portals like Aaple Sarkar (MahaOnline)**. It federates data across departmental registries (Identity, Municipality, Land Records, Tax) through non-invasive adapters—**preserving 100% departmental data sovereignty with zero centralized citizen data duplication.**

---

## ⚡ 60-Second Quick Start

### Option A: Test on Live Cloud (Zero Setup)
GovMesh is deployed live for instant evaluation:
* **Live Web Portal:** **[https://govmesh-frontend.onrender.com](https://govmesh-frontend.onrender.com)**
* **Interactive OpenAPI / Swagger Docs:** **[https://govmesh-backend.onrender.com/docs](https://govmesh-backend.onrender.com/docs)**
* **Health & Federation Monitor:** **[https://govmesh-backend.onrender.com/health](https://govmesh-backend.onrender.com/health)**

---

### Option B: Local Evaluation
From the repository root on Windows:
```powershell
.\start_all.ps1
```
*(Or on Linux/macOS, follow the terminal commands in [`docs/SETUP.md`](docs/SETUP.md))*

This launches all 6 isolated services locally:
* **Frontend Portal (React 18 + Vite):** [http://localhost:3000](http://localhost:3000)
* **GovMesh Core Gateway (FastAPI / Python 3.11):** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Identity Registry Service (Port 8101):** REST API (Aadhaar/National ID)
* **Municipality System (Port 8102):** API-Key REST (Residency & Ward)
* **Property Registry (Port 8103):** SOAP 1.2 / XML Land Records
* **Tax Department (Port 8104):** Asynchronous Two-Phase Job Queue

---

## 🔐 Verified Login Credentials

Both the Live Portal ([https://govmesh-frontend.onrender.com/login](https://govmesh-frontend.onrender.com/login)) and Local Portal ([http://localhost:3000/login](http://localhost:3000/login)) include **1-Click Verified Demonstration Personas**:

| Persona | Role | Email | Password | Access & Responsibilities |
| :--- | :--- | :--- | :--- | :--- |
| 🏛️ **State Administrator** | `admin` | `admin@govmesh.example` | `GovMesh@2026!` | Full federation command center, system telemetry, multi-protocol execution, immutable audit ledger. |
| 🛡️ **Chief Data Steward** | `data_steward` | `steward@govmesh.example` | `GovMesh@2026!` | Schema Evolution Cell, N-gram semantic mapping approvals, breaking change impact analysis. |
| 👤 **Aarav Sharma (CIT-1001)** | `citizen` | `citizen1001@govmesh.example` | `GovMesh@2026!` | Golden Path applicant with complete, verified records across all 4 departmental registries. |
| 👤 **Kabir Jain (CIT-1006)** | `citizen` | `citizen1006@govmesh.example` | `GovMesh@2026!` | Deterministic Conflict applicant proving cross-system discrepancy detection. |

---

## 🧪 5 Deterministic Live Tests for Evaluators

When logged in, the **SIH 2026 Evaluation Hub** is accessible at the top of every page. You can execute all 5 scenarios with a single click or test them manually.

---

### Test 1: Multi-Protocol Legacy Federation (Golden Path)
* **Evaluator Goal:** Verify concurrent multi-protocol aggregation without citizen data replication.
* **1-Click Action:** Click **"1. Golden Path (CIT-1001)"** in the Evaluator Hub.
* **Under the Hood:**
  1. GovMesh checks DPDP statutory consent for `CIT-1001`.
  2. Dispatches parallel queries across all 4 departments via `asyncio.gather`:
     - **Identity:** REST / Bearer Token &rarr; JSON
     - **Municipality:** REST / X-API-Key &rarr; JSON
     - **Property:** Legacy SOAP 1.2 with XML Envelope parsing &rarr; Normalized Output
     - **Tax:** Asynchronous Two-Phase Job submission &rarr; Polling
  3. Returns a unified composite citizen record.
* **What to Inspect:**
  - Open **"How this result was produced"** under the Property card: view the raw, captured SOAP 1.2 XML response and adapter field mapping.
  - Notice the **Execution Duration**: parallel queries complete in ~150–250ms rather than sequentially accumulating latencies.

---

### Test 2: DPDP Act 2023 Zero-Trust Consent Gate
* **Evaluator Goal:** Verify that unauthorized queries are strictly blocked before contacting any external departmental database.
* **1-Click Action:** Click **"2. Policy Denial (DPDP)"** in the Evaluator Hub.
* **Under the Hood:**
  1. Revokes consent for `CIT-1001`.
  2. Gateway policy gate halts execution immediately with `403 Forbidden` (`CONSENT_NOT_GRANTED`).
* **What to Inspect:**
  - Notice that **zero network calls** reach any external microservice.
  - Open **Audit Ledger** (`/audit`): a tamper-evident audit record is logged with `policy_decision: DENIED` and actor correlation ID.

---

### Test 3: Graceful Degradation (CIT-1003) — Zero Fake Data
* **Evaluator Goal:** Verify how the platform handles absent records without black-box AI data hallucination.
* **1-Click Action:** Click **"3. Degradation (CIT-1003)"** in the Evaluator Hub.
* **Under the Hood:**
  1. `CIT-1003` (Omar Das) has no registered land property in the Property Registry.
  2. Property service returns absent.
* **What to Inspect:**
  - GovMesh returns a clean partial fulfillment response.
  - Generates an explainable advisory finding: `DEPARTMENT_RESULTS_UNAVAILABLE` for Property.
  - **Zero data fabrication:** GovMesh guarantees that synthetic/hallucinated citizen records are never invented.

---

### Test 4: Deterministic Cross-System Mismatch (CIT-1006)
* **Evaluator Goal:** Verify explainable rule-based discrepancy detection across disparate government databases.
* **1-Click Action:** Click **"4. Name Conflict (CIT-1006)"** in the Evaluator Hub.
* **Under the Hood:**
  1. Identity Registry reports citizen name as: `"Kabir Jain"`.
  2. Property Land Registry reports deed owner as: `"Kabir A. Jain"`.
  3. GovMesh deterministic reconciliation engine executes cross-departmental validation.
* **What to Inspect:**
  - Under **Advisory Insights**, view the alert: `CROSS_SYSTEM_NAME_MISMATCH`.
  - Explains the exact discrepancy: `"Property owner 'Kabir A. Jain' does not match Identity full name 'Kabir Jain'"`.
  - Proves that data inconsistencies are flagged deterministically for human review rather than silently coerced.

---

### Test 5: Autonomous Schema Evolution & Human Governance
* **Evaluator Goal:** Demonstrate how GovMesh handles upstream breaking API changes without breaking downstream services.
* **1-Click Action:** Click **"5. Schema Evolution (v1→v2)"** in the Evaluator Hub (navigates to **Schema Intelligence**).
* **Step-by-Step Flow:**
  1. Click **"Trigger Upgrade Demo"**:
     - Simulates the Property Registry deploying Version 2 (`ownerName` field renamed to `propertyOwnerName`).
  2. View **Impact Analysis**:
     - Live alert: `Affected: Business Registration — Field mapping for ['ownerName'] is now broken`.
  3. View **Mapping Approvals**:
     - GovMesh AI/similarity engine detects the rename and suggests a new N-gram mapping (`propertyOwnerName` &rarr; `citizen.name`) with a **95% heuristic match score**.
  4. Click **"Approve"**:
     - Demonstrates **Human-in-the-Loop Data Steward Governance**.
     - Switch to the **"Approved"** tab to verify that Version 2 mapping is now active.
  5. Subsequent property queries now seamlessly adapt to Version 2 without downtime or broken contracts!

---

## 📊 Platform Verification Matrix for Evaluators

| Section | Route | What Judges Can Verify |
| :--- | :--- | :--- |
| **Dashboard** | `/` | Real-time telemetry, today's requests, completion rates, and recent transaction traces. |
| **Service Request** | `/service-request` | Dynamic multi-protocol query executor with live inspection panels. |
| **Application Tracking** | `/tracking` | End-to-end execution status with propagated `X-Correlation-ID`. |
| **Connected Systems** | `/systems` | Live protocol indicators (REST, SOAP, Async), uptime metrics, and node latency. |
| **Workflow Orchestrator** | `/workflow` | Multi-step transaction pipeline visualizer with live step polling. |
| **Schema Intelligence** | `/intelligence` | Version registry, breaking change detector, and N-gram field mapping approval workflow. |
| **Consent Management** | `/consent` | DPDP Act 2023 statutory consent granting, duration expiry, and immediate revocation. |
| **Audit Ledger** | `/audit` | Immutable append-only audit trail with actor IDs, timestamps, and field-level lineage. |
| **System Health** | `/health` | Core API health, PostgreSQL database connection, and Redis circuit breaker telemetry. |

---

## 🧪 Automated Test Suite Execution

Judges can execute the comprehensive test suite directly via the terminal:

```bash
cd backend
.\venv\Scripts\python.exe -m pytest tests/ -v
```

* **Test Coverage:** 88 automated tests covering:
  - Multi-protocol adapter parsing (SOAP XML envelope, JSON-RPC, async jobs)
  - Zero-Trust policy gate and consent validation
  - Deterministic mismatch & advisory rules
  - N-gram schema evolution similarity matching
  - Immutable audit trail generation and X-Correlation-ID propagation

---

## 🏆 Key Architectural Differentiators (Why GovMesh Wins)

1. **Non-Invasive Architecture:** Connects to legacy departmental systems without requiring rewrites or migrations.
2. **True Protocol Federation:** Transparently translates REST, SOAP 1.2 XML, and Async Polling into standardized citizen schemas.
3. **Statutory DPDP Act 2023 Compliance:** Zero-Trust consent enforcement halts queries at the gateway with zero network leakage.
4. **Deterministic & Explainable:** Flagged discrepancies are rule-based and transparent—zero opaque AI hallucination.
5. **Schema Governance Engine:** Upstream field renames are autonomously matched and approved by human Data Stewards without downtime.
