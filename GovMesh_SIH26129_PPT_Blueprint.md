# GovMesh — SIH26129 Idea Presentation Blueprint

## Template rules confirmed

The supplied SIH template contains seven slides. Slide 7 is an instruction page and says it must be deleted. Submit exactly **six slides**, including the title slide. Keep the existing template headings, layout, footer, and team-name field.

The template-backed section order is:

1. Title
2. Proposed Solution
3. Technical Approach
4. Feasibility and Viability
5. Impact and Benefits
6. Research and References

Use short points, diagrams, and infographics. Avoid paragraphs. Save the finished deck as a PDF for portal upload.

---

## Slide 1 — Title

### Title

**GovMesh: Consent-Aware Interoperability for Government Services**

### Fill the template fields from the SIH portal

- Problem Statement ID: SIH26129
- Problem Statement Title: Copy the exact portal wording
- Theme: Copy the exact portal wording
- PS Category: Software
- Team ID: Copy the exact portal ID
- Team Name: Copy the registered portal name

### Optional subtitle

Connecting heterogeneous departmental systems through secure adapters, governed data exchange, and schema intelligence.

### Visual direction

Keep this slide minimal. If space permits, use only a small network icon or four linked department icons. Do not add a large diagram.

---

## Slide 2 — Proposed Solution

### Heading

**A governed interoperability layer for cross-department service delivery**

### Copy-ready bullet content

- Government departments may use different APIs, schemas, protocols, and legacy applications.
- GovMesh provides one integration layer without replacing departmental databases or business logic.
- Department-specific connectors translate REST/JSON, SOAP/XML, and asynchronous responses into a common service model.
- A consent record defines the request purpose, data scope, requesting service, and expiry.
- Schema Intelligence detects field differences and proposes mappings for human approval.
- Audit and lineage records show which source supplied each response.

### How it addresses the problem

- One citizen service request can coordinate approved checks across participating systems.
- Departments retain control of their systems and data.
- Service teams receive a unified, traceable response instead of manually reconciling formats.

### Innovation and uniqueness

- Adapter-based integration for modern and legacy interfaces.
- Rule-based mapping suggestions for fields such as `full_name`, `resident_name`, and `ownerName`.
- Change-impact view: changed field → mapping → workflow step → affected service.
- Human approval before a proposed mapping becomes active.

### Recommended infographic

Place four differently shaped department blocks on the left:

- Identity: REST / JSON
- Property: SOAP / XML
- Municipality: Different JSON schema
- Tax: Asynchronous legacy interface

Place **GovMesh** in the centre and **Unified service response** on the right. Under GovMesh, add four small capability labels: Consent, Connectors, Schema Intelligence, Audit Trail.

### Accuracy guardrail

Call GovMesh a **prototype** or **MVP**. Do not claim that it already connects to UIDAI, API Setu, or live government databases.

---

## Slide 3 — Technical Approach

### Heading

**Prototype architecture and implementation flow**

### Architecture labels

- Citizen dashboard: React + Vite
- GovMesh API: Python + FastAPI
- Service data: PostgreSQL through SQLAlchemy
- Event and cache layer: Redis
- Connectors: Python adapter modules
- Department simulations: Identity, Property, Municipality, Tax
- Intelligence Engine: schema parsing, normalization, mapping score, change detection
- Governance layer: consent receipt, correlation ID, audit events, lineage

### Process flow

1. Citizen submits a service request.
2. GovMesh validates the request and creates a correlation ID.
3. Consent and permitted data scope are checked.
4. Connectors call participating department interfaces.
5. GovMesh normalizes responses into a common model.
6. Workflow returns status, trace, and source lineage.
7. A schema change creates a mapping suggestion for reviewer approval.

### Recommended diagram

Use a horizontal flow:

`Citizen UI → GovMesh API → Connector Layer → Department Systems`

Under the GovMesh API, place two supporting bands:

- Consent + Audit + Correlation ID
- Schema Intelligence + Mapping Approval

### Standards positioning

Use this small footer:

> Designed to align with documented API, metadata, and interoperability practices. The MVP uses simulated systems.

India's Open API policy promotes software interoperability, while API Setu supports API discovery, publishing, testing, and consumption. See [MeitY Open API Policy](https://www.meity.gov.in/static/uploads/2024/03/Policy-Document.pdf) and [API Setu](https://www.apisetu.gov.in/).

---

## Slide 4 — Feasibility and Viability

### Heading

**Incremental adoption with controlled technical risk**

### Feasibility content

| Feasibility factor | GovMesh approach |
| --- | --- |
| Existing systems | Add connector adapters; do not replace departmental applications |
| Different schemas | Canonical fields plus versioned mapping rules |
| Legacy interfaces | Support REST/JSON, SOAP/XML, and asynchronous adapter patterns |
| Privacy and trust | Purpose-bound consent, minimum necessary data, audit events |
| Schema changes | Detect differences, suggest mapping, require human approval |
| Rollout | Start with one service workflow and simulated connectors; add departments gradually |

### Risks and mitigations

- Incorrect field mapping → confidence threshold, reviewer approval, rollback to prior mapping.
- Department outage → timeout, partial response, retry queue, visible workflow status.
- Unauthorized access → role-based access, scoped credentials, audit records.
- Sensitive data exposure → no real citizen data in the demo; use synthetic records only.
- Inconsistent standards → retain source-specific adapters and version mappings.

### Recommended infographic

Use a three-stage rollout roadmap:

- Pilot: four simulated systems and one citizen workflow
- Validation: approved mappings, audit checks, failure handling
- Adoption: onboard real participating systems only after authorization and security review

### External research basis

India's IndEA framework treats data standards and metadata as important for sharing data across domains. MeitY's standards portal also describes metadata and data standards as necessary for semantic interoperability. See [IndEA Framework](https://egovstandards.gov.in/sites/default/files/IndEA%20Framework%201.0_0.pdf) and [e-Governance Standards](https://egovstandards.gov.in/domain-committees).

---

## Slide 5 — Impact and Benefits

### Heading

**Expected value for citizens, departments, and service teams**

### For citizens

- Fewer repeated submissions across a participating workflow.
- Clear request status and transparent service timeline.
- Purpose-specific data sharing with visible consent records.

### For departments

- Reuse existing systems through adapters.
- Reduce manual format reconciliation for selected workflows.
- Trace data sources, transformations, and workflow decisions.

### For service administrators

- Identify connector failures and affected workflow steps.
- Review proposed schema mappings before use.
- Maintain an audit trail for each service request.

### Public-value guardrails

- Do not claim universal access or time savings without pilot measurement.
- Do not claim live-system integration without authorization.
- Suggested pilot metrics: connector availability, mapping-review accuracy, request completion rate, and time spent resolving schema changes.

### Recommended infographic

Use three audience icons: Citizen, Department, Administrator. Place two benefits below each. Add a narrow bottom strip:

`Consent | Minimum necessary data | Traceability`

### External research basis

The National Data Sharing and Accessibility Policy and the Open Government Data Platform emphasize access to shareable government data in machine-readable forms within applicable policies, acts, and rules. This supports the direction of GovMesh; it does not validate a particular implementation or integration. See [NDSAP](https://www.india.gov.in/category/science-it-communication/subcategory/research-development./details/national-data-sharing-and-accessibility-policy) and [OGD Platform India](https://data.gov.in/about).

---

## Slide 6 — Research and References

Keep this slide to six short, clickable references. Use a title and organization rather than long displayed URLs.

1. [Policy on Open APIs for Government of India — MeitY](https://www.meity.gov.in/static/uploads/2024/03/Policy-Document.pdf)
2. [API Setu — Government API platform — Digital India Corporation / NeGD](https://www.apisetu.gov.in/)
3. [India Enterprise Architecture Framework 1.0 — MeitY](https://egovstandards.gov.in/sites/default/files/IndEA%20Framework%201.0_0.pdf)
4. [Metadata and Data Standards / Interoperability — e-Governance Standards Portal](https://egovstandards.gov.in/domain-committees)
5. [Aadhaar Authentication and consent requirements — UIDAI](https://uidai.gov.in/hi/about-authentication)
6. [National Data Sharing and Accessibility Policy — Government of India](https://www.india.gov.in/category/science-it-communication/subcategory/research-development./details/national-data-sharing-and-accessibility-policy)

### Supporting technical reference

[OpenAPI Specification](https://spec.openapis.org/oas/)

### Important source-use note

Use the UIDAI page only to support the general principle that authentication requires consent and controls. Do not place Aadhaar in the demo flow or imply UIDAI integration without formal authorization.

---

## Message to send the PPT teammate

Hi, please make the SIH idea PPT only in the official template and keep exactly six slides including the title slide. Delete template slide 7 before submission.

Use the GovMesh title and content blueprint in this file. Keep everything in short bullets, diagrams, and simple infographics, not paragraphs. Please do not claim that our prototype already integrates with UIDAI, API Setu, or any live government database. Describe the four systems as simulated departmental systems and call GovMesh an MVP/prototype.

For references, use only the official links provided. Keep the template headings and layout unchanged, fill the team details exactly from the SIH portal, export the final PPT as PDF, and check that all six slides remain readable.
