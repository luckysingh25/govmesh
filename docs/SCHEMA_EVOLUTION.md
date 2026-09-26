# GovMesh — Adaptive Schema Evolution & Intelligence Engine

**Technical Differentiator (USP):** Automated Upstream Breaking Change Detection with Human-in-the-Loop Data Governance.

---

## 1. The Core Enterprise Problem: Schema Drift & Fragility

In a federated government architecture, external departments periodically upgrade their internal database schemas or API specifications. 

### What Happens in Traditional e-Gov Portals:
* Department A renames `ownerName` to `propertyOwnerName`.
* Downstream integrated applications (Trade Licenses, Registration, Municipal Checks) immediately crash with unhandled `KeyError` or missing-field exceptions.
* Bureaucrats and engineers spend weeks coordinating email chains, updating hardcoded codebases, and scheduling maintenance downtimes.

### The GovMesh Approach:
GovMesh implements an **Adaptive Schema Intelligence Engine** that automatically detects upstream schema changes, isolates broken workflows, computes semantic similarity mappings, and provides an interactive approval interface for a certified **Data Steward**.

```
+----------------------------------------------------------------------------------------------------+
|                                    SCHEMA EVOLUTION PIPELINE                                       |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  [External Department]                                                                             |
|      v1 Schema: { "ownerName": "Asha Verma" }                                                      |
|           |                                                                                        |
|           | (Department upgrades to v2)                                                            |
|           v                                                                                        |
|      v2 Schema: { "propertyOwnerName": "Asha Verma" }                                              |
|                                                                                                    |
|  [GovMesh Intelligence Ingestion]                                                                  |
|      1. AST / Lexical Parsing: Detects field 'ownerName' removed; 'propertyOwnerName' added        |
|      2. Impact Analysis: Flags affected workflows -> "Business Registration (Property Step)"       |
|      3. Match Scoring Engine:                                                                      |
|         - EXACT Match (Score = 1.0)                                                                |
|         - SEMANTIC Match (N-Gram / Token Distance, Score = 0.95)                                   |
|         - TRANSFORMATION-REQUIRED (Type coercion or string concatenation)                          |
|      4. Suggestion Table: Proposes "propertyOwnerName" -> "citizen.name" (Confidence: 95%)        |
|                                                                                                    |
|  [Human-in-the-Loop Governance]                                                                   |
|      5. Data Steward Reviews Mapping in /intelligence                                              |
|      6. Steward clicks [Approve] -> Mapping v2 becomes active; Lineage updated; Audit logged      |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
```

---

## 2. Match Scoring Heuristics

The engine categorizes field mapping relationships using deterministic scoring algorithms (`app/intelligence/engine.py`):

1. **`EXACT` Match (Score: 1.0)**:
   - Field names match exactly after case normalization and whitespace stripping (e.g. `full_name` $\rightarrow$ `fullName`).
2. **`SEMANTIC` Match (Score: 0.85 – 0.99)**:
   - Computed using token overlap, character n-gram similarities, and canonical synonym dictionaries:
     * `ownerName` $\rightarrow$ `propertyOwnerName` (Confidence: **95%**)
     * `dob` $\rightarrow$ `date_of_birth` (Confidence: **90%**)
     * `tax_balance` $\rightarrow$ `outstanding_amount` (Confidence: **88%**)
3. **`TRANSFORMATION-REQUIRED`**:
   - Triggers when data types differ (e.g. integer timestamps vs ISO 8601 strings) or when multiple source fields combine into a single canonical field (e.g. `first_name` + `last_name` $\rightarrow$ `name`).

---

## 3. Change Impact Analysis

When a schema upgrade is ingested, the engine generates an **Impact Analysis Report** before any mappings are altered:

* **Target System:** Property Registry (`v1` $\rightarrow$ `v2`)
* **Breaking Change:** Field `['ownerName']` is no longer emitted.
* **Affected Workflows:**
  - `business_registration` (Property Verification Step)
  - `property_transfer` (Ownership Verification Step)
* **Risk Level:** `HIGH` (Downstream citizen service requests will degrade until resolved).

---

## 4. Human-in-the-Loop Governance (Data Steward Role)

Government data governance policies mandate that **unsupervised machine learning or algorithmic mapping must never alter legal citizen records without human accountability**.

### The Approval Workflow:
1. Proposed mappings are placed in a `pending` state inside the database.
2. Only users authenticated with the role **`data_steward`** or **`admin`** can access the approval APIs.
3. Upon review:
   * **Approve**: The mapping state transitions to `approved`, the schema version advances, and an immutable audit log is generated:
     `[Actor: steward@govmesh.gov.in] [Action: Mapping Approved] [Target: propertyOwnerName -> citizen.name] [Version: v2]`.
   * **Reject**: The suggestion is dismissed, and the steward can define a custom manual mapping.
