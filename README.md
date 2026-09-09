# GovMesh MVP

GovMesh is a prototype interoperability layer for SIH26129. It coordinates consent-aware service requests across simulated government departments, normalizes REST and SOAP responses, records workflow/audit metadata, and produces transparent rule-based advisory insights.

This repository contains:

- `frontend/`: React 18 and Vite operator/citizen interface.
- `backend/`: FastAPI API, synchronous workflow engine, consent/policy checks, audit and lineage records, and deterministic intelligence rules.
- `services/`: simulated Identity (REST + bearer token), Municipality (REST + API key), Property (SOAP/XML), and Tax (asynchronous-style REST) systems.
- `services/seed/`: fictional, deterministic records for `CIT-1001` through `CIT-1008` plus scenario expectations.
- `docker-compose.yml`: optional full-stack container configuration with PostgreSQL and Redis.

## Architecture and ports

| Component | URL | Purpose |
| --- | --- | --- |
| Frontend | `http://localhost:3000` | UI |
| Backend | `http://localhost:8000` | API and OpenAPI docs |
| Identity | `http://localhost:8101` | REST identity records |
| Municipality | `http://localhost:8102` | REST municipal records |
| Property | `http://localhost:8103` | SOAP/XML property records |
| Tax | `http://localhost:8104` | asynchronous-style tax lookup |

The prototype executes workflow steps synchronously and sequentially so a submitted request has a reliable final state before the response is returned. Redis is included for future event-driven execution but is not required by the current request path.

## Quick start

Use [SETUP.md](SETUP.md) for complete Windows, macOS/Linux, migration, native, and Docker instructions.

For native development:

1. Copy `backend/.env.example` to `backend/.env`, set a PostgreSQL `DATABASE_URL` and a non-default `SECRET_KEY`, then run `alembic upgrade head` from `backend/`.
2. Start the four department services on ports 8101–8104.
3. Start the backend on 8000 and the frontend on 3000.
4. Grant consent for the chosen service type before submitting a request.

The three supported service types use one central workflow definition:

| Service type | Required departments |
| --- | --- |
| `business_registration` | identity, property, municipality, tax |
| `property_transfer` | identity, property, municipality |
| `tax_clearance` | identity, tax |

## Deterministic demo scenarios

All people, addresses, and identifiers are fictional demo fixtures.

| Citizen | Scenario | Expected advisory |
| --- | --- | --- |
| `CIT-1001` | healthy and consistent | none |
| `CIT-1002` | tax due | `TAX_CLEARANCE_NOT_CONFIRMED` |
| `CIT-1003` | property missing | `DEPARTMENT_RESULTS_UNAVAILABLE` |
| `CIT-1004` | municipality missing | `DEPARTMENT_RESULTS_UNAVAILABLE` |
| `CIT-1005` | identity missing | `DEPARTMENT_RESULTS_UNAVAILABLE` |
| `CIT-1006` | owner-name mismatch | `CROSS_SYSTEM_NAME_MISMATCH` |
| `CIT-1007` | address mismatch | `CROSS_SYSTEM_ADDRESS_MISMATCH` |
| `CIT-1008` | tax pending | `TAX_CLEARANCE_NOT_CONFIRMED` (info) |

Seed files are validated when each simulated service starts. A missing, invalid, or duplicate record fails startup with a clear error; connectors never fabricate substitute citizen data.

## Advisory intelligence

After normalization, pure deterministic rules examine only the available department results. Every finding has a stable `rule_id`, `info` or `warning` severity, and a plain-language message. Name/address comparison trims whitespace, collapses repeated spaces, and compares case-insensitively. The UI labels this output “Advisory Insights” and states that it does not make eligibility or approval decisions.

## Tests

```bash
cd backend
python -m pytest -q

cd ../frontend
npm ci
npm test
npm run build
```

CI runs the same backend tests and frontend test/build checks for pull requests. Runtime databases, logs, caches, editor settings, environment secrets, and build outputs are ignored.

## Security boundaries

- Public registration always creates a `citizen`; callers cannot self-assign privileged roles.
- Passwords are validated and stored only as hashes.
- Schema ingestion and mapping approval/rejection require `admin` or `data_steward`.
- The repeatable intelligence demo trigger is available only in development, demo, or test environments.
- `.env` files are never committed; use the checked-in examples as templates.

This is a prototype, not a production identity, authorization, eligibility, or legal decision system.
