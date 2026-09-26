# GovMesh — Consent-Aware Government Interoperability Mesh

[![SIH 2026](https://img.shields.io/badge/SIH%202026-PS%20SIH26129-blue.svg?style=for-the-badge&logo=gov.in)](https://sih.gov.in)
[![Organization](https://img.shields.io/badge/Sponsoring%20Org-Govt%20of%20Maharashtra-orange.svg?style=for-the-badge)](https://www.maharashtra.gov.in/)
[![Theme](https://img.shields.io/badge/Theme-Smart%20Automation-purple.svg?style=for-the-badge)](https://sih.gov.in)
[![Backend](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python%203.11-009688.svg?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Frontend](https://img.shields.io/badge/Frontend-React%2018%20%7C%20Vite-61DAFB.svg?style=for-the-badge&logo=react)](https://react.dev/)
[![Tests](https://img.shields.io/badge/Automated%20Tests-88%20Passed%20(Pytest)-brightgreen.svg?style=for-the-badge&logo=pytest)](docs/TEST_VERIFICATION.md)
[![Compliance](https://img.shields.io/badge/Compliance-IndEA%202.0%20%7C%20DPDP%202023-blueviolet.svg?style=for-the-badge)](docs/COMPLIANCE_STANDARDS.md)

> **Smart India Hackathon (SIH) 2026 — Problem Statement SIH26129**  
> **Problem Title:** *System integration and interoperability among government digital platforms, resulting in fragmented service delivery*  
> **Sponsoring Body:** Government of Maharashtra (Department of IT / e-Governance)  
> **Team Name:** The Code Blooded  
> **Jury & Evaluator Quick Test Guide:** 🏆 **[`JUDGES_TESTING_GUIDE.md`](JUDGES_TESTING_GUIDE.md)**  
> **Demo Walkthrough Video:** [Watch Unlisted 2.5-Minute Demo Video](https://youtube.com) *(Insert Video Link)*

---

## 🏛️ Executive Overview

State governments operate dozens of independent departmental systems across disparate technologies—modern JSON REST APIs, 20-year-old SOAP/XML registries, and asynchronous batch engines. When citizens apply for complex composite services (e.g., Business Registration or Property Transfer), data fragmentation forces repeated manual submissions and bureaucratic delays.

**GovMesh is not another citizen portal.**  
GovMesh is the **governed interoperability middleware beneath state portals like Aaple Sarkar (MahaOnline)**. It federates data across Land Records (Mahabhulekh), IGR Registration, Municipalities, and Tax registries through non-invasive adapters—**preserving 100% departmental data sovereignty without centralized data replication.**

```mermaid
flowchart LR
    subgraph Legacy ["❌ Traditional Fragmented Model"]
        direction TB
        Cit1["Citizen"] --> S1["Dept Portal A (Land)"]
        Cit1 --> S2["Dept Portal B (Taxes)"]
        Cit1 --> S3["Dept Portal C (Municipal)"]
        S1 -. "Manual Re-entry" .-> Cit1
        S2 -. "Physical Affidavit" .-> Cit1
        S3 -. "Bureaucratic Delay" .-> Cit1
    end

    subgraph Mesh ["✅ GovMesh Federated Interoperability Mesh"]
        direction TB
        Cit2["Citizen"] --> Portal["State Single-Window<br/>(Aaple Sarkar / MahaOnline)"]
        Portal --> GM["GovMesh Interoperability Core<br/>(DPDP Act 2023 Consent Gate)"]
        GM <--> D1["Land Records (SOAP/XML)"]
        GM <--> D2["IGR Registry (REST)"]
        GM <--> D3["Municipal System (REST)"]
        GM <--> D4["Tax Clearance (Async)"]
    end
```

---

## 🏗️ System Architecture Topology

```mermaid
graph TD
    classDef client fill:#1e293b,stroke:#3b82f6,stroke-width:2px,color:#f8fafc;
    classDef gateway fill:#0f172a,stroke:#10b981,stroke-width:3px,color:#f8fafc;
    classDef core fill:#1e293b,stroke:#6366f1,stroke-width:2px,color:#f8fafc;
    classDef adapter fill:#0b1120,stroke:#f59e0b,stroke-width:2px,color:#f8fafc;
    classDef dept fill:#0f172a,stroke:#a855f7,stroke-width:2px,color:#f8fafc;

    UI["Citizen & Admin Portal<br/>(React 18 + Vite · Port 3000)"]:::client
    Gateway["GovMesh Core Gateway<br/>(FastAPI / Python 3.11 · Port 8000)"]:::gateway

    subgraph CoreEngine ["GovMesh Core Engine"]
        Consent["Dynamic Consent Gate<br/>(DPDP Act 2023 Enforcement)"]:::core
        Workflow["Workflow Orchestrator<br/>(asyncio.gather Concurrency)"]:::core
        Intelligence["Schema Evolution Engine<br/>(v1→v2 Similarity Matching)"]:::core
        Audit["Append-Only Audit & Lineage<br/>(X-Correlation-ID Tracking)"]:::core
    end

    subgraph AdapterLayer ["Multi-Protocol Adapter Layer"]
        AdapterID["Identity Adapter<br/>REST / Bearer Token"]:::adapter
        AdapterMuni["Municipality Adapter<br/>REST / X-API-Key"]:::adapter
        AdapterProp["Property Adapter<br/>SOAP 1.2 / XML Envelope"]:::adapter
        AdapterTax["Tax & Revenue Adapter<br/>Async Two-Phase Job Queue"]:::adapter
    end

    subgraph DepartmentSystems ["Sovereign Department Simulators"]
        SvcID["Identity Registry<br/>(Port 8101 · JSON)"]:::dept
        SvcMuni["Municipality System<br/>(Port 8102 · JSON)"]:::dept
        SvcProp["Property Registry<br/>(Port 8103 · SOAP/XML)"]:::dept
        SvcTax["Tax Clearance Svc<br/>(Port 8104 · Async Batch)"]:::dept
    end

    UI -->|HTTPS / REST + JWT| Gateway
    Gateway --> Consent
    Consent -->|Policy Approved| Workflow
    Consent -.->|Zero Consent: Policy Denied| UI
    Workflow --> Intelligence
    Workflow --> Audit

    Workflow -->|Concurrent Dispatch| AdapterID
    Workflow -->|Concurrent Dispatch| AdapterMuni
    Workflow -->|Concurrent Dispatch| AdapterProp
    Workflow -->|Concurrent Dispatch| AdapterTax

    AdapterID <-->|HTTP GET| SvcID
    AdapterMuni <-->|HTTP GET| SvcMuni
    AdapterProp <-->|SOAP Envelope POST| SvcProp
    AdapterTax <-->|Job Dispatch & Poll| SvcTax
```

---

## 🔄 End-to-End Transaction Flow

```mermaid
sequenceDiagram
    autonumber
    actor Citizen as Citizen / Officer
    participant Gateway as GovMesh Gateway (8000)
    participant Consent as DPDP Consent Gate
    participant Adapters as Concurrent Adapters
    participant Departments as Microservices (8101-8104)
    participant Lineage as Audit & Lineage DB

    Citizen->>Gateway: Submit Request (CIT-1001 + JWT)
    Note over Gateway: Injects X-Correlation-ID
    Gateway->>Consent: Validate Purpose-Bound Consent

    alt No Consent / Expired
        Consent-->>Gateway: Denied (Zero-Trust)
        Gateway-->>Citizen: 403 Forbidden (Zero External Network Calls)
    else Consent Active
        Consent-->>Gateway: Approved
        par Parallel Execution via asyncio.gather
            Gateway->>Adapters: Query Identity (REST / Bearer)
            Adapters->>Departments: Port 8101 GET
            Departments-->>Adapters: Identity JSON
        and
            Gateway->>Adapters: Query Municipality (REST / API-Key)
            Adapters->>Departments: Port 8102 GET
            Departments-->>Adapters: Municipal JSON
        and
            Gateway->>Adapters: Query Property (SOAP 1.2 / XML)
            Adapters->>Departments: Port 8103 POST (XML Envelope)
            Departments-->>Adapters: SOAP XML Response
        and
            Gateway->>Adapters: Query Tax (Async 2-Phase Job)
            Adapters->>Departments: Port 8104 POST Job -> Poll GET
            Departments-->>Adapters: Tax Balance JSON
        end
        Adapters-->>Gateway: Normalized Output (Zero Fake Data)
        Gateway->>Lineage: Append Audit Trail & Source-to-Target Lineage
        Gateway-->>Citizen: Unified Canonical Response + Advisory Insights
    end
```

---

## ⚡ Core Technical Innovations & USPs

### 1. Dynamic Purpose-Bound Consent Gate (DPDP Act 2023 Aligned)
* Data is never fetched speculatively.
* An affirmative consent receipt explicitly scopes the requesting service and permitted departments.
* **Zero-Trust Denial Guarantee:** If consent is absent or expired, the gateway aborts execution immediately with zero external network queries.

```mermaid
stateDiagram-v2
    [*] --> ConsentRequested: Citizen Selects Service
    ConsentRequested --> ScopeEvaluated: Verify Purpose & Permitted Depts
    
    state ScopeEvaluated {
        ActiveConsent: Valid Signed Consent Receipt
        DeniedOrExpired: Consent Missing / Revoked / Expired
    }

    DeniedOrExpired --> ZeroTrustDenial: 403 Forbidden
    ZeroTrustDenial --> [*]: ZERO Network Sockets Opened to Depts

    ActiveConsent --> ParallelExecution: Concurrent Adapter Dispatch
    ParallelExecution --> UnifiedResponse: Canonical Harmonization
    UnifiedResponse --> [*]
```

### 2. Native Multi-Protocol Federation (Zero Rip-and-Replace)
* Integrates disparate protocols in parallel via `asyncio.gather`:
  * **Identity Service (8101)**: JSON REST with Bearer token authentication.
  * **Municipality Service (8102)**: JSON REST with `X-API-Key` headers.
  * **Property Service (8103)**: Legacy SOAP 1.2 XML with XML envelope parsing.
  * **Tax Service (8104)**: Asynchronous 2-phase job dispatch and polling.

### 3. Adaptive Schema Evolution & Governance (The Technical Differentiator)
* Detects upstream breaking changes when external departments upgrade schemas (`v1` $\rightarrow$ `v2`, e.g. `ownerName` $\rightarrow$ `propertyOwnerName`).
* Calculates n-gram similarity match scores (`EXACT`, `SEMANTIC`, `TRANSFORMATION-REQUIRED`).
* Features an interactive human-in-the-loop governance portal for certified **Data Stewards** to approve and activate mappings live.

```mermaid
flowchart LR
    Upstream["Upstream Dept Upgrade<br/>(v1 -> v2 Breaking Change)"] --> Detect["FastAPI Ingestion &<br/>Pydantic Isolation"]
    Detect --> Similarity["N-Gram Similarity Matcher<br/>(EXACT, SEMANTIC, TRANSFORM)"]
    Similarity --> Steward["Data Steward Console<br/>(Interactive Human Governance)"]
    Steward -->|Steward Approval| DynamicMap["Active Field Remapper<br/>(Zero Code Redeployment)"]
    DynamicMap --> Operational["Service Restored<br/>(100% Data Integrity)"]
```

### 4. Deterministic Graceful Degradation (Zero Hallucination)
* 8 pre-seeded deterministic citizen scenarios (`CIT-1001` to `CIT-1008`).
* When an external department is unavailable (`CIT-1003` Property absent), GovMesh returns a clean partial status with explainable advisory codes.
* **GovMesh NEVER fabricates, hallucinates, or generates fake citizen records.**

### 5. Distributed Traceability & Field-Level Lineage
* End-to-end `X-Correlation-ID` injected and propagated across all microservice hops.
* Field-level data lineage maps every returned value directly to its authoritative source field (`Identity DB.full_name` $\rightarrow$ `GovMesh Canonical.citizen.name`).

---

## 📚 Complete Documentation Suite

All detailed architectural specifications, API contracts, and evaluation guides are organized in the [`docs/`](docs/) directory:

| Document | Description |
| :--- | :--- |
| 🏆 [**Judges & Evaluator Testing Guide**](JUDGES_TESTING_GUIDE.md) | **Step-by-step evaluation workflow for SIH jury members with deterministic test fixtures.** |
| 📖 [**Architecture Specification**](docs/ARCHITECTURE.md) | In-depth system components, database schemas, and microservice topology with Level 0-3 DFDs. |
| 🔄 [**Data Flow & Sequence**](docs/DATA_FLOW.md) | End-to-end sequence diagrams, transaction lifecycles, and concurrency models. |
| 🔌 [**API Contract & Reference**](docs/API_REFERENCE.md) | Endpoints, headers, payload schemas, and authentication flows. |
| 🛡️ [**Security & DPDP Privacy Architecture**](docs/SECURITY_AND_PRIVACY.md) | Zero-trust boundaries, cryptographic tokens, PBKDF2 hashing, and STRIDE threat matrix. |
| 🧬 [**Schema Evolution Engine**](docs/SCHEMA_EVOLUTION.md) | Breaking change detection, similarity heuristics, and Data Steward governance. |
| ⚖️ [**Standards & Legal Compliance**](docs/COMPLIANCE_STANDARDS.md) | Alignment with IndEA 2.0, MeitY Open API Policy, and DPDP Act 2023. |
| ✅ [**Test & Security Verification**](docs/TEST_VERIFICATION.md) | Proof of 88 automated pytest cases, Vitest suites, and security hardening. |
| 🚀 [**Setup & Run Guide**](docs/SETUP.md) | Complete local and Docker installation instructions for developers. |
| 🎯 [**Live Demo Guide & Scenarios**](docs/DEMO_GUIDE.md) | Step-by-step walkthrough of the 8 deterministic citizen scenarios and the new 1-click Demo Hub. |
| 📊 [**Idea PPT Blueprint**](docs/GovMesh_SIH26129_PPT_Blueprint.md) | Official 6-slide SIH idea presentation blueprint following the AICTE template. |

---

## 🚀 Quick Start Guide

### Prerequisites
* Python 3.11 or 3.12
* Node.js 18+ and npm
* PostgreSQL 15+ (Local or Cloud instance like Neon)
* Git

### One-Click Launch (Windows)
Double-click **`start_all.bat`** (or run `.\start_all.ps1` from PowerShell) in the repository root. This boots:
* **Frontend Portal:** `http://localhost:3000`
* **Gateway API & Swagger Docs:** `http://localhost:8000/docs`
* **4 Department Simulators:** Ports 8101, 8102, 8103, and 8104.

*For Docker or manual step-by-step startup instructions, see [docs/SETUP.md](docs/SETUP.md).*

---

## 👥 Evaluator Demo Mode

The web application includes an **Evaluator Demo Suite** banner directly at the top of the interface:
* 🟢 **1. Golden Path (`CIT-1001`)**: All 4 services succeed concurrently.
* 🔴 **2. Zero-Trust Denial**: Demonstrates DPDP Act 2023 policy gate denial when consent is absent.
* 🟡 **3. Graceful Degradation (`CIT-1003`)**: Demonstrates clean partial records with ZERO fake data fabrication when the property registry has no record.
* 🟠 **4. Name Conflict (`CIT-1006`)**: Demonstrates deterministic advisory engine detecting cross-system name discrepancy.
* 🟣 **5. Schema Evolution (v1 $\rightarrow$ v2)**: Demonstrates breaking change detection and Data Steward approval.

---

## 👥 Team & Authorship

**Team Name:** The Code Blooded  
**Problem Statement ID:** SIH26129 (Government of Maharashtra)  

| Name | Role | Stream | Academic Year |
| :--- | :--- | :--- | :--- |
| **Lucky Singh Panwar** | Team Leader | B.Tech CSE | 4th Year (Batch 2023) |
| **Harikesh Kumar** | Core Developer | B.Tech CSE | 4th Year (Batch 2023) |
| **Aman Singh Kunwar** | Core Developer | B.Tech CSE | 3rd Year (Batch 2024) |
| **Abhishek Kumar Gupta** | Core Developer | B.Tech CSE | 3rd Year (Batch 2024) |
| **Arushi Saxena** | Researcher & Designer | B.Tech CSE | 3rd Year (Batch 2024) |
| **Harshita Rai** | AI/ML & Intelligence | B.Tech CSE (AI/ML) | 2nd Year (Batch 2025) |

*(SIH Gender Diversity Compliant: 4 Male, 2 Female).*

---

## 📄 License & Academic Attribution
Developed for the **Smart India Hackathon (SIH) 2026** under Problem Statement **SIH26129** sponsored by the **Government of Maharashtra**.  
All rights reserved by **The Code Blooded** team.
