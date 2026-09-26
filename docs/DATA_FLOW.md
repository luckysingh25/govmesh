# GovMesh — Data Flow & Transaction Lifecycle Specification

**Project:** GovMesh (Consent-Aware Government Interoperability Mesh)  
**Problem Statement ID:** `SIH26129`  
**Sponsoring Organization:** Government of Maharashtra  

---

## 1. End-to-End Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor Citizen as Citizen / Officer (React UI)
    participant Gateway as GovMesh Core Gateway (FastAPI)
    participant ConsentDB as Consent & Policy Engine
    participant Connectors as Protocol Adapter Layer
    participant DeptREST as Identity & Muni (REST)
    participant DeptSOAP as Property Registry (SOAP/XML)
    participant DeptAsync as Tax Svc (Async Job)
    participant RulesEngine as Advisory Engine
    participant AuditDB as Audit & Lineage DB

    Citizen->>Gateway: POST /api/v1/service-requests (Payload + JWT)
    Note over Gateway: Gateway generates X-Correlation-ID (UUID v4)
    Gateway->>ConsentDB: Verify Active Consent (Citizen ID + Service Type)
    
    alt Consent Absent or Expired (Policy Denial)
        ConsentDB-->>Gateway: Consent Denied
        Gateway->>AuditDB: Log Security Denial Event (Correlation ID)
        Gateway-->>Citizen: 403 Forbidden / Status: denied
        Note over Gateway: ZERO network sockets opened to external departments!
    else Consent Active (Policy Approved)
        ConsentDB-->>Gateway: Consent Approved (Scope Validated)
        Gateway->>AuditDB: Record Workflow Started + Consent Hash
        
        par Concurrent Execution via asyncio.gather
            Gateway->>Connectors: Dispatch Identity Query
            Connectors->>DeptREST: HTTP GET /citizen/{id} (Bearer Token)
            DeptREST-->>Connectors: 200 OK JSON
        and
            Gateway->>Connectors: Dispatch Municipality Query
            Connectors->>DeptREST: HTTP GET /registration/{id} (X-API-Key)
            DeptREST-->>Connectors: 200 OK JSON
        and
            Gateway->>Connectors: Dispatch Property Query
            Connectors->>DeptSOAP: SOAP 1.2 Request Envelope (XML)
            DeptSOAP-->>Connectors: SOAP Response Envelope (XML)
            Note over Connectors: XML Tree Parsing -> Canonical Property JSON
        and
            Gateway->>Connectors: Dispatch Tax Job Submission
            Connectors->>DeptAsync: POST /jobs (Create Job)
            DeptAsync-->>Connectors: 202 Accepted (job_id: TX-901)
            loop Two-Phase Polling
                Connectors->>DeptAsync: GET /jobs/TX-901
                DeptAsync-->>Connectors: Status: Completed
            end
        end

        Connectors-->>Gateway: Normalized Connector Results
        Gateway->>RulesEngine: Evaluate Deterministic Cross-System Rules
        Note over RulesEngine: Check name conflicts, address mismatch, tax arrears
        RulesEngine-->>Gateway: Advisory Insights (Severity + Code)
        Gateway->>AuditDB: Append Immutable Audit Events & Data Lineage
        Gateway-->>Citizen: Unified Response (Status, Canonical Data, Lineage)
    end
```

---

## 2. Request State Machine Lifecycle

Every transaction in GovMesh transitions through an explicit state machine:

```mermaid
stateDiagram-v2
    [*] --> SUBMITTED : Citizen initiates request

    SUBMITTED --> CONSENT_CHECK : Validate against DPDP Gate
    
    CONSENT_CHECK --> DENIED : Consent missing or expired
    DENIED --> [*] : Halts before external calls

    CONSENT_CHECK --> DISPATCHED : Consent active & validated
    
    DISPATCHED --> CONCURRENT_ADAPTERS : asyncio.gather()
    
    state CONCURRENT_ADAPTERS {
        [*] --> REST_CALLS : Bearer / API-Key
        [*] --> SOAP_CALL : XML Envelope Parse
        [*] --> ASYNC_JOB : Polling Loop
    }

    CONCURRENT_ADAPTERS --> HARMONIZING : All adapters return

    HARMONIZING --> ADVISORY_RULES : Canonical JSON Formed
    
    ADVISORY_RULES --> SUCCESS : All departments clean
    ADVISORY_RULES --> PARTIAL : Dept missing (Zero fake data)
    ADVISORY_RULES --> ADVISORY_FLAGGED : Mismatch detected

    SUCCESS --> COMPLETED : Audit & Lineage logged
    PARTIAL --> COMPLETED : Audit & Lineage logged
    ADVISORY_FLAGGED --> COMPLETED : Audit & Lineage logged

    COMPLETED --> [*]
```

---

## 3. The 8 Deterministic Scenario Fixtures (`CIT-1001` to `CIT-1008`)

To guarantee reproducible evaluations without depending on volatile external network states, GovMesh includes 8 pre-seeded deterministic citizen scenarios:

| Citizen ID | Name | Department Outcomes | Resulting Status | Observed Advisory / Rationale |
| :--- | :--- | :--- | :--- | :--- |
| `CIT-1001` | Asha Verma | Identity: ✅ Muni: ✅ Property: ✅ Tax: ✅ | `success` | Golden path: All records consistent, verified, and tax cleared. |
| `CIT-1002` | Nila Rao | Identity: ✅ Muni: ✅ Property: ✅ Tax: ⚠️ | `success` | `TAX_CLEARANCE_NOT_CONFIRMED`: Tax due with outstanding ₹14,500.50. |
| `CIT-1003` | Omar Das | Identity: ✅ Muni: ✅ Property: ❌ Tax: ✅ | `partially_completed` | `DEPARTMENT_RESULTS_UNAVAILABLE`: Property record absent; returns partial status without fake data. |
| `CIT-1004` | Leela Sen | Identity: ✅ Muni: ❌ Property: ✅ Tax: ✅ | `partially_completed` | `DEPARTMENT_RESULTS_UNAVAILABLE`: Municipal registration absent; no hallucinated registration. |
| `CIT-1005` | Ishan Kapoor | Identity: ❌ Muni: ✅ Property: ✅ Tax: ✅ | `partially_completed` | `DEPARTMENT_RESULTS_UNAVAILABLE`: Identity record absent; fails gracefully without substitute. |
| `CIT-1006` | Kabir Jain | Identity: ✅ Muni: ✅ Property: ⚠️ Tax: ✅ | `success` | `CROSS_SYSTEM_NAME_MISMATCH`: Property owner name differs (`Kabir A. Jain` vs `Kabir Jain`). |
| `CIT-1007` | Mira Bose | Identity: ✅ Muni: ⚠️ Property: ✅ Tax: ✅ | `success` | `CROSS_SYSTEM_ADDRESS_MISMATCH`: Municipal address conflicts with Identity address. |
| `CIT-1008` | Tara Mehta | Identity: ✅ Muni: ✅ Property: ✅ Tax: ⏳ | `pending_external` | Tax job in progress; returns non-terminal status until job completion is polled. |

---

## 4. Failure Isolation & Concurrency Model

### Parallel Concurrency via `asyncio.gather`
Instead of executing sequential queries that compound latency:
$$\text{Total Latency} = \max(t_{\text{identity}}, t_{\text{muni}}, t_{\text{property}}, t_{\text{tax}})$$
The gateway fires all 4 queries concurrently. A network timeout on one adapter does not stall the execution of remaining adapters.

### Zero-Hallucination Degradation Principle
When an external department fails or is unreachable:
1. The error is isolated to that microservice's sub-object in the JSON response.
2. The overall response status transitions to `partially_completed`.
3. **No fake or dummy data is ever inserted** into missing fields.
4. Downstream civic officers receive an explicit warning badge identifying exactly which department record was absent.
