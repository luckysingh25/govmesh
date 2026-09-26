# GovMesh — System Architecture & Data Flow Diagrams (DFD)

**Project:** GovMesh (Consent-Aware Government Interoperability Mesh)  
**Problem Statement ID:** `SIH26129`  
**Sponsoring Organization:** Government of Maharashtra (Department of IT / e-Governance)  
**Theme:** Smart Automation | **Category:** Software  
**Document Classification:** Technical Architecture & Formal DFD Specification  

---

## 1. System Context & Architectural Philosophy

GovMesh is an interoperability middleware prototype designed to federate heterogeneous, legacy departmental databases beneath state single-window portals (such as **Aaple Sarkar / MahaOnline**) without centralized data replication.

### Department Sovereignty vs Centralized Warehouses:
* **The Antipattern (Centralized Database):** Forcing departments to push records into a central data lake violates departmental data sovereignty, creates single points of failure, and exposes personal data under the **DPDP Act 2023**.
* **The GovMesh Pattern (Federated Mesh):** Department databases remain authoritative and sovereign. GovMesh deploys non-invasive protocol adapters (JSON REST, legacy SOAP 1.2 XML, Async Polling), enforces purpose-bound consent gates, and harmonizes responses dynamically.

---

## 2. Level 0 DFD — Context Diagram

The Level 0 Data Flow Diagram illustrates the operational boundary of GovMesh, showing external actors and data exchanges:

```mermaid
graph TD
    classDef actor fill:#1e293b,stroke:#3b82f6,stroke-width:2px,color:#f8fafc;
    classDef process fill:#0f172a,stroke:#10b981,stroke-width:3px,color:#f8fafc;

    Citizen["Citizen / Civic Officer<br/>(Browser / React UI)"]:::actor
    IdentityDept["Identity Registry<br/>(Port 8101 / REST)"]:::actor
    MuniDept["Municipality System<br/>(Port 8102 / REST)"]:::actor
    PropertyDept["Property Registry<br/>(Port 8103 / SOAP 1.2 XML)"]:::actor
    TaxDept["Tax & Revenue Authority<br/>(Port 8104 / Async Jobs)"]:::actor
    DataSteward["Data Steward / Admin<br/>(Governance Officer)"]:::actor

    GovMesh(("0.0<br/>GovMesh Core<br/>Interoperability<br/>Mesh Gateway")):::process

    Citizen -- "1. Service Request + JWT<br/>2. Consent Grants / Revocations" --> GovMesh
    GovMesh -- "3. Unified Application Status<br/>4. Advisory Insights & Lineage" --> Citizen

    GovMesh -- "5. Outbound Query (Bearer Token)" --> IdentityDept
    IdentityDept -- "6. Identity Record (JSON)" --> GovMesh

    GovMesh -- "7. Outbound Query (X-API-Key)" --> MuniDept
    MuniDept -- "8. Municipal Registration (JSON)" --> GovMesh

    GovMesh -- "9. SOAP 1.2 Envelope (XML)" --> PropertyDept
    PropertyDept -- "10. SOAP Response Envelope (XML)" --> GovMesh

    GovMesh -- "11. Dispatch Job / Poll Status" --> TaxDept
    TaxDept -- "12. Tax Clearance Status (JSON)" --> GovMesh

    DataSteward -- "13. Ingest Schema / Approve Mapping" --> GovMesh
    GovMesh -- "14. Impact Analysis & Suggestions" --> DataSteward
```

---

## 3. Level 1 DFD — Functional System Decomposition

The Level 1 DFD decomposes GovMesh into its 7 primary sub-processes and authoritative data stores:

```mermaid
graph TD
    classDef proc fill:#1e293b,stroke:#3b82f6,stroke-width:2px,color:#f8fafc;
    classDef store fill:#0b1120,stroke:#f59e0b,stroke-width:2px,color:#f8fafc;
    classDef ext fill:#0f172a,stroke:#64748b,stroke-width:1px,color:#94a3b8;

    User["Citizen / Civic User"]:::ext
    Steward["Data Steward"]:::ext

    P1["1.0<br/>Authenticate &<br/>Enforce RBAC"]:::proc
    P2["2.0<br/>Validate Dynamic<br/>Consent Gate"]:::proc
    P3["3.0<br/>Orchestrate<br/>Workflow Tasks"]:::proc
    P4["4.0<br/>Adapt Protocols &<br/>Normalize Data"]:::proc
    P5["5.0<br/>Evaluate Deterministic<br/>Advisory Rules"]:::proc
    P6["6.0<br/>Log Audit Trail &<br/>Record Lineage"]:::proc
    P7["7.0<br/>Evolve Schemas &<br/>Manage Mappings"]:::proc

    D1[("D1: Users & Credentials<br/>(PostgreSQL)")]:::store
    D2[("D2: Consent Receipts<br/>(PostgreSQL)")]:::store
    D3[("D3: Service Requests & Workflows<br/>(PostgreSQL / Redis)")]:::store
    D4[("D4: Append-Only Audit & Lineage<br/>(PostgreSQL)")]:::store
    D5[("D5: Schema Registry & Mappings<br/>(PostgreSQL)")]:::store

    User -->|Credentials| P1
    P1 <-->|Validate Hash & Role| D1
    P1 -->|Authenticated Session + JWT| P2

    P2 <-->|Check Scope, Service & Expiry| D2
    P2 -->|Policy Approved Token| P3
    P2 -.->|Policy Denied: Halts Execution| User

    P3 <-->|Read Workflow Definition & State| D3
    P3 -->|Concurrent Parallel Queries| P4

    P4 -->|Outbound REST, SOAP, Async| Depts["External Dept Systems<br/>(8101, 8102, 8103, 8104)"]:::ext
    Depts -->|Raw Responses| P4

    P4 -->|Normalized Canonical JSON| P5
    P5 -->|Advisory Insight Codes| P6

    P6 -->|Write Immutable Trace| D4
    P6 -->|Final Harmonized Response| User

    Steward -->|New Schema Ingestion| P7
    P7 <-->|Versioned Schemas & Mappings| D5
    P7 -->|Active Mapping Rules| P4
```

---

## 4. Level 2 DFD — Workflow Orchestration & Multi-Protocol Adaptation

This deep dive details how Process 3.0 and Process 4.0 handle protocol differences concurrently:

```mermaid
graph TD
    classDef subproc fill:#1e293b,stroke:#06b6d4,stroke-width:2px,color:#f8fafc;
    classDef store fill:#0b1120,stroke:#f59e0b,stroke-width:2px,color:#f8fafc;
    classDef dept fill:#0f172a,stroke:#a855f7,stroke-width:2px,color:#f8fafc;

    PolicyToken["Approved Policy Token<br/>(Correlation ID + Scope)"]

    P31["3.1<br/>Resolve Workflow<br/>Definition Steps"]:::subproc
    P32["3.2<br/>Concurrent Dispatch<br/>(asyncio.gather)"]:::subproc

    P41["4.1<br/>Identity REST Adapter<br/>(Bearer Token Injected)"]:::subproc
    P42["4.2<br/>Municipality REST Adapter<br/>(X-API-Key Injected)"]:::subproc
    P43["4.3<br/>Property SOAP Adapter<br/>(XML Envelope Builder)"]:::subproc
    P44["4.4<br/>Tax Async Adapter<br/>(Two-Phase Job Polling)"]:::subproc
    P45["4.5<br/>Canonical Harmonizer &<br/>Graceful Degradation Handler"]:::subproc

    S_Identity["Identity Svc (8101)"]:::dept
    S_Muni["Municipality Svc (8102)"]:::dept
    S_Property["Property Svc (8103)"]:::dept
    S_Tax["Tax Svc (8104)"]:::dept

    PolicyToken --> P31
    P31 --> P32

    P32 -->|Async Task 1| P41
    P32 -->|Async Task 2| P42
    P32 -->|Async Task 3| P43
    P32 -->|Async Task 4| P44

    P41 <-->|HTTP GET (Bearer)| S_Identity
    P42 <-->|HTTP GET (X-API-Key)| S_Muni
    P43 <-->|HTTP POST SOAP/XML| S_Property
    P44 <-->|POST Job -> Poll GET| S_Tax

    P41 -->|Raw Identity JSON| P45
    P42 -->|Raw Municipal JSON| P45
    P43 -->|Parsed XML Tree| P45
    P44 -->|Resolved Tax JSON| P45

    P45 -->|Isolated Failure Status if Down| Output["Harmonized Canonical Record<br/>(Zero Fake Data Fabricated)"]
```

---

## 5. Level 3 DFD — Schema Evolution & Intelligence Engine

This detailed view explains how Process 7.0 ingests upstream schema changes and governs them:

```mermaid
graph TD
    classDef subproc fill:#1e293b,stroke:#ec4899,stroke-width:2px,color:#f8fafc;
    classDef store fill:#0b1120,stroke:#f59e0b,stroke-width:2px,color:#f8fafc;

    RawSchema["Upstream Department Schema<br/>(JSON / XML XSD)"]
    Steward["Certified Data Steward"]

    P71["7.1<br/>Lexical Tokenizer &<br/>AST Schema Parser"]:::subproc
    P72["7.2<br/>Breaking Change &<br/>Deprecation Analyzer"]:::subproc
    P73["7.3<br/>N-Gram & Similarity<br/>Match Scoring Engine"]:::subproc
    P74["7.4<br/>Workflow Impact<br/>Assessment Generator"]:::subproc
    P75["7.5<br/>Human Approval &<br/>Versioned Activation"]:::subproc

    D5[("D5: Schema Registry &<br/>Mapping Suggestions")]:::store

    RawSchema --> P71
    P71 -->|Extracted Field Tokens| P72
    P72 <-->|Compare Against v1 Schema| D5

    P72 -->|New / Renamed Fields| P73
    P73 -->|Match Scores: EXACT / SEMANTIC / TRANSFORM| P74
    P72 -->|Broken Downstream Steps| P74

    P74 -->|Persist Inactive Suggestion| D5
    D5 -->|Display Suggestion & Impact| Steward

    Steward -->|Authenticated Action: Approve / Reject| P75
    P75 -->|Activate v2 Mapping Rule| D5
    P75 -->|Emit Governance Audit Log| D4[("D4: Audit Trail")]:::store
```

---

## 6. Technical Specifications & Ports

| Subsystem | Technology | Port | Authentication | Protocol |
| :--- | :--- | :--- | :--- | :--- |
| **Frontend Portal** | React 18 + Vite | `3000` | Session / JWT | HTTPS / WSS |
| **GovMesh Core Gateway** | FastAPI / Python 3.11 | `8000` | Signed JWT (HS256) | REST / JSON |
| **Identity Service** | FastAPI Microservice | `8101` | Bearer Token | REST / JSON |
| **Municipality Service** | FastAPI Microservice | `8102` | `X-API-Key` | REST / JSON |
| **Property Registry** | SOAP Simulator | `8103` | None (Simulated) | SOAP 1.2 / XML |
| **Tax & Revenue Service** | Async Job Simulator | `8104` | None (Simulated) | Asynchronous Polling |
| **Relational Database** | PostgreSQL 16 | `5432` | Standard Password | TCP / SQL |
| **Event / Cache Layer** | Redis 7 | `6379` | Token (Optional) | Redis Protocol |
