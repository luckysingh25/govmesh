# 🛠️ GovMesh — Full Project Setup Guide

> **Smart India Hackathon 2026 — Problem Statement SIH26129**  
> Interoperable, Federated Government Data Mesh Platform with Dynamic Consent & Real-Time Orchestration.

---

## 📋 Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [Architecture Overview](#2-architecture-overview)
3. [Environment Configuration (.env)](#3-environment-configuration-env)
4. [Step-by-Step Installation](#4-step-by-step-installation)
   - [A. Python Virtual Environment & Dependencies](#a-python-virtual-environment--dependencies)
   - [B. Database Setup (Neon PostgreSQL)](#b-database-setup-neon-postgresql)
   - [C. Frontend Setup (React + Vite)](#c-frontend-setup-react--vite)
5. [Starting All Services (Terminal Commands)](#5-starting-all-services-terminal-commands)
6. [One-Click Startup Scripts](#6-one-click-startup-scripts)
7. [Verification & Health Checks](#7-verification--health-checks)
8. [Troubleshooting & FAQs](#8-troubleshooting--faqs)

---

## 1. Prerequisites

Ensure you have the following installed on your machine:

| Component | Minimum Version | Check Command |
| :--- | :--- | :--- |
| **Python** | 3.10+ (3.11 or 3.12 recommended) | `python --version` or `python3 --version` |
| **Node.js** | 18.x or 20.x | `node -v` |
| **npm** | 9.x or 10.x | `npm -v` |
| **PostgreSQL** | 15+ (Cloud Neon or Local) | Provided in cloud via Neon |
| **Git** | 2.x | `git --version` |

---

## 2. Architecture Overview & Port Allocation

GovMesh uses an asynchronous federated architecture where the Backend Core orchestrates calls to 4 departmental microservices.

```
┌─────────────────────────────────────────────────────────────┐
│                    GovMesh Architecture                     │
└─────────────────────────────────────────────────────────────┘
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
       [ Frontend (UI) ]              [ Backend Core API ]
     http://localhost:3000           http://localhost:8000
                                               │
     ┌──────────────────┬──────────────────────┼──────────────────┐
     ▼                  ▼                      ▼                  ▼
[ Identity ]      [ Property ]          [ Municipality ]       [ Tax ]
  Port 8101          Port 8102             Port 8103          Port 8104
```

| Service | Technology | Port | Directory |
| :--- | :--- | :--- | :--- |
| **Backend Core** | FastAPI + SQLAlchemy + Asyncpg | `8000` | `backend/` |
| **Frontend UI** | React 18 + Vite + Lucide Icons | `3000` | `frontend/` |
| **Identity Service** | FastAPI (REST + Token Auth) | `8101` | `services/identity-service/` |
| **Property Service** | FastAPI (SOAP / XML Mock) | `8102` | `services/property-service/` |
| **Municipality Service**| FastAPI (REST + API Key) | `8103` | `services/municipality-service/` |
| **Tax Service** | FastAPI (REST API) | `8104` | `services/tax-service/` |
| **Database** | Neon Serverless PostgreSQL | Cloud | Configured via `DATABASE_URL` |

---

## 3. Environment Configuration (.env)

The root `.env` and `backend/.env` files configure database credentials and service endpoints.

Ensure `backend/.env` exists (copy from `.env.example` if needed):

```dotenv
# backend/.env
APP_NAME=govmesh-backend
ENVIRONMENT=development
DATABASE_URL="postgresql://<username>:<password>@<neon-host>/neondb?sslmode=require"
# Or local PostgreSQL: DATABASE_URL="postgresql://govmesh:govmesh@localhost:5432/govmesh"
SECRET_KEY=your-secret-key-change-me-in-production
REDIS_URL=redis://localhost:6379/0

# Department Service URLs
IDENTITY_URL=http://localhost:8101
PROPERTY_URL=http://localhost:8102
MUNICIPALITY_URL=http://localhost:8103
TAX_URL=http://localhost:8104
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## 4. Step-by-Step Installation

### A. Python Virtual Environment & Dependencies

From the project root:

#### Windows (PowerShell):
```powershell
# 1. Navigate to backend directory and create virtual environment
cd backend
python -m venv venv

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. Upgrade pip and install core backend dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### macOS / Linux:
```bash
# 1. Navigate to backend directory and create virtual environment
cd backend
python3 -m venv venv

# 2. Activate virtual environment
source venv/bin/activate

# 3. Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

> 💡 **Pro-Tip**: The same virtual environment (`backend/venv`) contains FastAPI, Uvicorn, and httpx, which can be shared across all 4 microservices.

---

### B. Database Setup (Neon PostgreSQL)

Run database schema migrations to create all required tables (`service_requests`, `consent_records`, `audit_logs`, `policy_rules`):

```powershell
# Inside backend/ with venv activated:
alembic upgrade head
```

If you ever need to seed initial test data or policies, you can run:
```powershell
python -m app.db.init_db
```

---

### C. Frontend Setup (React + Vite)

Open a new terminal and navigate to `frontend/`:

```bash
cd frontend
npm install
```

---

## 5. Starting All Services (Terminal Commands)

To run the entire GovMesh stack locally, open **6 terminal windows** (or use the multi-service launcher script in Section 6):

### Terminal 1: Identity Service (Port 8101)
```powershell
# Windows
cd d:\govmesh\services\identity-service
..\..\backend\venv\Scripts\python.exe -m uvicorn app:app --reload --port 8101

# macOS/Linux
cd services/identity-service
../../backend/venv/bin/python -m uvicorn app:app --reload --port 8101
```

### Terminal 2: Property Service (Port 8102)
```powershell
# Windows
cd d:\govmesh\services\property-service
..\..\backend\venv\Scripts\python.exe -m uvicorn app:app --reload --port 8102

# macOS/Linux
cd services/property-service
../../backend/venv/bin/python -m uvicorn app:app --reload --port 8102
```

### Terminal 3: Municipality Service (Port 8103)
```powershell
# Windows
cd d:\govmesh\services\municipality-service
..\..\backend\venv\Scripts\python.exe -m uvicorn app:app --reload --port 8103

# macOS/Linux
cd services/municipality-service
../../backend/venv/bin/python -m uvicorn app:app --reload --port 8103
```

### Terminal 4: Tax Service (Port 8104)
```powershell
# Windows
cd d:\govmesh\services\tax-service
..\..\backend\venv\Scripts\python.exe -m uvicorn app:app --reload --port 8104

# macOS/Linux
cd services/tax-service
../../backend/venv/bin/python -m uvicorn app:app --reload --port 8104
```

### Terminal 5: Backend Core API Gateway (Port 8000)
```powershell
# Windows
cd d:\govmesh\backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000

# macOS/Linux
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000
```

### Terminal 6: Frontend UI (Port 3000)
```bash
cd frontend
npm run dev
```

---

## 6. One-Click Startup Scripts

### Windows PowerShell Startup Script (`start_all.ps1`)
You can run all services with a single PowerShell script:

```powershell
# Run from project root:
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd services/identity-service; ..\..\backend\venv\Scripts\python.exe -m uvicorn app:app --reload --port 8101"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd services/property-service; ..\..\backend\venv\Scripts\python.exe -m uvicorn app:app --reload --port 8102"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd services/municipality-service; ..\..\backend\venv\Scripts\python.exe -m uvicorn app:app --reload --port 8103"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd services/tax-service; ..\..\backend\venv\Scripts\python.exe -m uvicorn app:app --reload --port 8104"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"
```

---

## 7. Verification & Health Checks

Once all services are running, verify them in your browser or with curl:

| Endpoint | Target URL | Expected Response |
| :--- | :--- | :--- |
| **Frontend Portal** | `http://localhost:3000` | GovMesh Modern Dashboard |
| **Backend Health** | `http://localhost:8000/health` | `{"status": "ok", "database": {"status": "connected"}}` |
| **Department Health** | `http://localhost:8000/api/v1/systems/monitoring` | Live health for all 4 microservices |
| **Swagger Docs** | `http://localhost:8000/docs` | Interactive OpenAPI documentation |
| **Identity Service** | `http://localhost:8101/health` | `{"status": "ok", "service": "identity-service"}` |
| **Property Service** | `http://localhost:8102/health` | `{"status": "ok", "service": "property-service"}` |
| **Municipality Service** | `http://localhost:8103/health` | `{"status": "ok", "service": "municipality-service"}` |
| **Tax Service** | `http://localhost:8104/health` | `{"status": "ok", "service": "tax-service"}` |

---

## 8. Troubleshooting & FAQs

### Q1: `uvicorn : The term 'uvicorn' is not recognized`
**Fix**: Ensure you invoke Python with the full venv path, or activate the venv:
```powershell
d:\govmesh\backend\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

### Q2: `ECONNREFUSED` on port 8000 from frontend
**Fix**: The backend is not running on port 8000. Start Terminal 5 (Backend Core) before making frontend requests.

### Q3: `Redis unavailable` in health check
**Note**: Redis is completely optional in this MVP. GovMesh automatically falls back to in-memory event bus and caching without any loss of functionality.

### Q4: Consent Denied on first request
**Fix**: Go to the **Consent** page (`http://localhost:3000/consent`), select `CIT-1001` and `business_registration`, and click **"Grant Consent"**.
