# GovMesh Setup & Run Guide

GovMesh is an interoperable government service mesh prototype (SIH 26129) that federates distributed department microservices, enforces dynamic citizen consent, harmonizes multi-protocol APIs (REST, SOAP, Async Jobs), and provides schema intelligence and data lineage.

---

## Prerequisites

- **Python 3.11 or 3.12**
- **Node.js 18+ and npm**
- **PostgreSQL 15+** (Local or Cloud instance like Neon PostgreSQL)
- **Git**
- *Docker Desktop* (Optional, only if using containerized workflow)

---

## Environment Configuration

GovMesh uses two `.env` files for different execution contexts:

| File | Purpose | When Used |
| :--- | :--- | :--- |
| **`backend/.env`** | **Native Backend Execution** | Used when running Uvicorn directly from `backend/`. Controls database connection, JWT secret key, and department service URLs. |
| **`.env` (Root)** | **Docker Compose / Global** | Used by `docker compose up` to configure the PostgreSQL database container, Redis, and global container environment. |

### Setup Environment Files

Copy the provided example files into your local `.env` configurations:

```powershell
# Windows PowerShell
Copy-Item backend\.env.example backend\.env
Copy-Item .env.example .env
```

```bash
# macOS / Linux
cp backend/.env.example backend/.env
cp .env.example .env
```

Edit `backend/.env` to configure your PostgreSQL connection string (`DATABASE_URL`).

Authentication never creates users as a side effect. In development/demo only, create fictional accounts explicitly with a password supplied through a temporary environment variable:

```powershell
$env:GOVMESH_DEMO_PASSWORD = Read-Host -AsSecureString | ConvertFrom-SecureString -AsPlainText
cd backend
.\.venv\Scripts\python.exe -m app.cli create-demo-users --password-from-env GOVMESH_DEMO_PASSWORD
Remove-Item Env:GOVMESH_DEMO_PASSWORD
```

To use the steward-only schema and failure controls, set an unpredictable local key before starting all processes. Both the backend and Property simulator inherit it; do not commit it or capture it in screenshots:

```powershell
$env:ENVIRONMENT = "demo"
$env:DEMO_CONTROLS_ENABLED = "true"
$env:DEMO_CONTROL_KEY = [guid]::NewGuid().ToString()
.\start_all.ps1
```

Leave `DEMO_CONTROLS_ENABLED=false` for normal development and every non-demo environment.

---

## Database Migration & Initial Setup

From the `backend/` directory, set up your Python virtual environment and run the database migrations:

### Windows PowerShell:

```powershell
cd backend
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m alembic upgrade head
```

### macOS / Linux:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python -m alembic upgrade head
```

### Install Frontend Dependencies:

```bash
cd ../frontend
npm install
```

---

## Running the Project

### Option A: One-Click Launch (Windows — Recommended)

Double-click **`start_all.bat`** in the repository root, or run:

```powershell
.\start_all.ps1
```

This automatically opens 6 separate, organized terminal windows for all microservices, the core backend, and the frontend portal.

---

### Option B: Manual Multi-Terminal Launch

Open separate terminals for each service:

#### 1. Identity Service (REST — Port 8101)
```powershell
# Windows PowerShell
cd d:\govmesh\services\identity-service
..\..\backend\venv\Scripts\python.exe -m uvicorn app:app --reload --port 8101
```
```bash
# macOS / Linux
cd services/identity-service
../../backend/venv/bin/python -m uvicorn app:app --reload --port 8101
```

#### 2. Municipality Service (REST — Port 8102)
```powershell
# Windows PowerShell
cd d:\govmesh\services\municipality-service
..\..\backend\venv\Scripts\python.exe -m uvicorn app:app --reload --port 8102
```
```bash
# macOS / Linux
cd services/municipality-service
../../backend/venv/bin/python -m uvicorn app:app --reload --port 8102
```

#### 3. Property Service (SOAP / XML — Port 8103)
```powershell
# Windows PowerShell
cd d:\govmesh\services\property-service
..\..\backend\venv\Scripts\python.exe -m uvicorn app:app --reload --port 8103
```
```bash
# macOS / Linux
cd services/property-service
../../backend/venv/bin/python -m uvicorn app:app --reload --port 8103
```

#### 4. Tax Service (REST Async Jobs — Port 8104)
```powershell
# Windows PowerShell
cd d:\govmesh\services\tax-service
..\..\backend\venv\Scripts\python.exe -m uvicorn app:app --reload --port 8104
```
```bash
# macOS / Linux
cd services/tax-service
../../backend/venv/bin/python -m uvicorn app:app --reload --port 8104
```

#### 5. GovMesh Backend Core Gateway (Port 8000)
```powershell
# Windows PowerShell
cd d:\govmesh\backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```
```bash
# macOS / Linux
cd backend
./venv/bin/python -m uvicorn app.main:app --reload --port 8000
```

#### 6. GovMesh Frontend Dashboard (Port 3000)
```powershell
# Windows PowerShell / macOS / Linux
cd d:\govmesh\frontend
npm run dev
```

---

### Option C: Run with Docker Compose

```bash
docker compose up --build
```

To stop and reset all containerized demo data:
```bash
docker compose down -v
```

---

## Service Verification & URLs

| Service / Interface | URL | Protocol | Notes |
| :--- | :--- | :--- | :--- |
| **Frontend Portal** | `http://localhost:3000` | HTTP / React | Citizen & Admin Unified UI |
| **Backend API Docs** | `http://localhost:8000/docs` | Swagger / OpenAPI | Interactive API explorer |
| **Health Check** | `http://localhost:8000/health` | HTTP JSON | Database & Service health |
| **Live Systems Monitor**| `http://localhost:8000/api/v1/systems/monitoring` | HTTP JSON | Real-time department latency |
| **Identity Service** | `http://localhost:8101/health` | REST | Port 8101 |
| **Municipality Service**| `http://localhost:8102/health` | REST | Port 8102 |
| **Property Service** | `http://localhost:8103/health` | SOAP / XML | Port 8103 |
| **Tax Service** | `http://localhost:8104/health` | Async REST | Port 8104 |

---

## Running Automated Tests

### Backend Test Suite (Pytest — 88 Tests)

```powershell
# Windows PowerShell
cd backend
.\venv\Scripts\python.exe -m pytest -q
```

```bash
# macOS / Linux
cd backend
python -m pytest -q
```

### Frontend Test Suite (Vitest) & Production Build

```bash
cd frontend
npm test
npm run build
```

---

## Troubleshooting

- **Database connection error**: Confirm that `DATABASE_URL` and, when used, `DATABASE_URL_UNPOOLED` point to an accessible database. GovMesh uses the operating system's standard DNS and database connection path.
- **Port In Use (WinError 10048)**: Check what process is using the port with `Get-NetTCPConnection -LocalPort 8000` and stop duplicate uvicorn instances.
- **Consent Denied**: Submit consent at `http://localhost:3000/consent` before initiating a service request for a citizen.
- **Redis Connection**: Redis is non-blocking and optional in the synchronous workflow prototype; absence of a local Redis server will not halt request execution.
