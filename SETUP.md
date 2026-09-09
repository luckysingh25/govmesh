# GovMesh setup guide

## Prerequisites

- Python 3.12 recommended
- Node.js 20 and npm
- PostgreSQL 15+
- Git
- Docker Desktop only if using the optional container workflow

Redis is optional for the current synchronous prototype.

## Environment configuration

Never commit real credentials. For native development, copy `backend/.env.example` to `backend/.env` and replace the database password and `SECRET_KEY`. For Docker Compose, copy the root `.env.example` to `.env` and replace the development password.

The native service URLs must remain:

```dotenv
IDENTITY_URL=http://localhost:8101
MUNICIPALITY_URL=http://localhost:8102
PROPERTY_URL=http://localhost:8103
TAX_URL=http://localhost:8104
```

## Native setup

Create the backend environment and database schema.

Windows PowerShell:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env, create its PostgreSQL database, then:
python -m alembic upgrade head
```

macOS/Linux:

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
# Edit .env, create its PostgreSQL database, then:
python -m alembic upgrade head
```

Install frontend dependencies:

```bash
cd frontend
npm ci
```

## Run natively without Docker

Open six terminals from the project root. Reuse the backend virtual-environment Python for the small simulated services.

Windows PowerShell:

```powershell
# Terminal 1
cd services\identity-service
..\..\backend\.venv\Scripts\python.exe -m uvicorn app:app --reload --port 8101

# Terminal 2
cd services\municipality-service
..\..\backend\.venv\Scripts\python.exe -m uvicorn app:app --reload --port 8102

# Terminal 3
cd services\property-service
..\..\backend\.venv\Scripts\python.exe -m uvicorn app:app --reload --port 8103

# Terminal 4
cd services\tax-service
..\..\backend\.venv\Scripts\python.exe -m uvicorn app:app --reload --port 8104

# Terminal 5
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000

# Terminal 6
cd frontend
npm run dev
```

On macOS/Linux, replace the Python path with `../../backend/.venv/bin/python` for department services and `.venv/bin/python` for the backend.

## Run with Docker Compose

```bash
cp .env.example .env  # PowerShell: Copy-Item .env.example .env
# Replace POSTGRES_PASSWORD in .env
docker compose config --quiet
docker compose up --build
```

The backend container applies Alembic migrations before starting. Department images include the shared validated seed directory. The frontend dev proxy targets the backend container by service name.

To reset only the Docker demo database, stop the stack and explicitly remove its named volume:

```bash
docker compose down -v
```

This permanently removes containerized PostgreSQL demo data.

## Verification

| Check | URL / command |
| --- | --- |
| Frontend | `http://localhost:3000` |
| Backend health | `http://localhost:8000/health` |
| OpenAPI | `http://localhost:8000/docs` |
| Live department monitoring | `http://localhost:8000/api/v1/systems/monitoring` |
| Identity health | `http://localhost:8101/health` |
| Municipality health | `http://localhost:8102/health` |
| Property health | `http://localhost:8103/health` |
| Tax health | `http://localhost:8104/health` |

Monitoring reports live reachability and latency. Historical uptime/error-rate values display as “Not measured” because this prototype has no metrics store.

## Tests and build

```bash
cd backend
python -m pytest -q

cd ../frontend
npm test
npm run build
```

## Troubleshooting

- Consent denied: grant consent for the same citizen and service type, including exactly that workflow’s required departments.
- Department offline: verify its corrected port above and check `/health` directly.
- Database connection failure: confirm PostgreSQL is running, the database exists, and `DATABASE_URL` is correct.
- Migration failure: run from `backend/` so `alembic.ini` is discoverable.
- Redis unavailable: expected to be non-blocking in synchronous mode; do not claim event-driven execution until a worker is implemented.
- Demo schema button unavailable: it is intentionally disabled outside development/demo/test environments.
