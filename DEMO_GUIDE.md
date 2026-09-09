# GovMesh deterministic demo guide

## Before the demo

1. Start PostgreSQL, all four simulated department services, the backend, and the frontend using [SETUP.md](SETUP.md).
2. Confirm `/health` on ports 8000, 8101, 8102, 8103, and 8104.
3. Open `http://localhost:3000/consent`, grant consent for the citizen/service combination, then submit it at `http://localhost:3000/service-request`.

For `business_registration`, consent must include identity, property, municipality, and tax. `property_transfer` requires identity, property, and municipality. `tax_clearance` requires identity and tax.

## Recommended presentation sequence

### 1. Consent gate

Submit `CIT-1001` before granting consent. Explain that the policy gate returns a denial without contacting a department. Then grant business-registration consent and resubmit.

### 2. Healthy interoperability

Use `CIT-1001` (Asha Verma). All four normalized results succeed and the Advisory Insights section reports no detected issue.

### 3. Explainable advisory

Use one or more of these fictional scenarios:

| Citizen | Result to demonstrate |
| --- | --- |
| `CIT-1002` — Nila Rao | Tax status `DUE`, outstanding amount `14500.5`, warning `TAX_CLEARANCE_NOT_CONFIRMED` |
| `CIT-1003` — Omar Das | Property record is absent; partial result and `DEPARTMENT_RESULTS_UNAVAILABLE` |
| `CIT-1004` — Leela Sen | Municipality record is absent; partial result and `DEPARTMENT_RESULTS_UNAVAILABLE` |
| `CIT-1005` — Ishan Kapoor | Identity record is absent; no identity is fabricated |
| `CIT-1006` — Kabir Jain | Property owner deliberately differs; `CROSS_SYSTEM_NAME_MISMATCH` |
| `CIT-1007` — Mira Bose | Municipality address deliberately differs; `CROSS_SYSTEM_ADDRESS_MISMATCH` |
| `CIT-1008` — Tara Mehta | Tax job remains pending; informational `TAX_CLEARANCE_NOT_CONFIRMED` |

Explain that each stable rule ID comes from deterministic comparisons of normalized results. These are advisory integration checks, not AI predictions, fraud scores, eligibility decisions, or legal decisions.

### 4. Protocol adaptation

Show that Identity and Municipality return JSON REST payloads, Property returns SOAP/XML, and Tax uses a submit/result job shape. The backend exposes one consistent department-result structure without hiding missing, pending, timeout, or unavailable states.

### 5. Real monitoring and auditability

Open the Systems page. Status and latency come from concurrent calls to each real department `/health` endpoint. “Not measured” is intentional for historical metrics. Then show the request’s correlation ID in workflow/audit views.

## Accurate technical claims

- Workflow execution is synchronous and sequential in this prototype.
- A department failure degrades the aggregate without generating fake citizen data.
- Redis is optional and is not currently a background workflow worker.
- PostgreSQL stores orchestration, consent, mapping, audit, and lineage metadata—not a permanent centralized copy of department source records.
- Public registration cannot create administrators or data stewards.
- Schema-change demo data is repeatable: triggering it more than once does not create unlimited versions.

## Resetting demo state

For a native database, use your normal PostgreSQL administration process and rerun `python -m alembic upgrade head`. Do not delete an unknown database automatically. For the Compose-only demo database, `docker compose down -v` deletes its named volume and all contained demo data.
