# GovMesh MVP
**SIH 2026 Project (Problem Statement SIH26129)**

GovMesh is an interoperable platform connecting disparate government service data into a unified experience. This repository contains the initial Minimum Viable Product (MVP) representing the first vertical slice: the **Citizen Service Request** flow.

## 🏛️ Project Structure

- **`frontend/`**: React + Vite UI application. Displays the unified citizen data.
- **`backend/`**: FastAPI backend that orchestrates data retrieval across multiple departments using concurrent async connectors, normalizes data, and logs requests to PostgreSQL.
- **`services/`**: Mocked legacy/remote government systems.
  - `identity-service`: Mock REST API returning JSON (Token Auth).
  - `property-service`: Mock SOAP API returning XML (Requires XML parsing).
  - `municipality-service`: Mock REST API returning JSON (API Key Auth).
  - `tax-service`: Mock REST API returning JSON.
- **`database/`**: Configured PostgreSQL & Redis containers via `docker-compose`.

---

## 🚀 Local Quick Start (no Docker required)

GovMesh runs natively on macOS/zsh. You need a local PostgreSQL server; Redis is optional for this MVP and its unavailable status does not block the request flow.

**Local Ports Map**:
- Frontend UI: `http://localhost:3000` (run natively using `npm run dev`)
- Backend API: `http://localhost:8000`
- Identity Service: `http://localhost:8101`
- Municipality Service: `http://localhost:8102`
- Property Service: `http://localhost:8103`
- Tax Service: `http://localhost:8104`

---

## 🏃 Running Components Natively

### 1. Database
```bash
# Start your installed PostgreSQL service, then create the MVP database once.
createdb govmesh
# If your local PostgreSQL username is not govmesh, set DATABASE_URL in backend/.env.
```

### 2. Mock Department Services
Open separate terminals for each service and run:
```bash
# Identity Service (Port 8101)
cd services/identity-service
pip install -r requirements.txt
python3 -m uvicorn app:app --reload --port 8101

# Municipality Service (Port 8102)
cd services/municipality-service
pip install -r requirements.txt
python3 -m uvicorn app:app --reload --port 8102

# Property Service (Port 8103)
cd services/property-service
pip install -r requirements.txt
python3 -m uvicorn app:app --reload --port 8103

# Tax Service (Port 8104)
cd services/tax-service
pip install -r requirements.txt
python3 -m uvicorn app:app --reload --port 8104
```

### 3. Backend Core
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Run migrations to set up Postgres Schema
alembic upgrade head

# Start API
python3 -m uvicorn app.main:app --reload --port 8000
```

### 4. React Frontend
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

---

## 🛠️ Usage Examples

### 1. Health Checks
Verify that all services are alive:
```bash
curl http://localhost:8000/health
curl http://localhost:8101/health
```

### 2. Example Service Request
**Endpoint**: `POST /api/v1/service-requests`

**Request Body**:
```json
{
  "citizen_id": "CIT-1001",
  "service_type": "business_registration"
}
```

**Curl Command**:
```bash
curl -X POST http://localhost:8000/api/v1/service-requests \
     -H "Content-Type: application/json" \
     -H "X-Correlation-ID: demo-request-001" \
     -d '{"citizen_id": "CIT-1001", "service_type": "business_registration"}'
```

**Response**:
```json
{
  "request_id": "REQ-B892F20C",
  "correlation_id": "0208cd44-fb4d-4ba6-829b-a9bdf118e6ff",
  "citizen": {
    "citizen_id": "CIT-1001",
    "name": "Rajesh Kumar",
    "address": "123 MG Road, Bangalore, Karnataka"
  },
  "identity": {
    "status": "success",
    "data": { "full_name": "Rajesh Kumar", "date_of_birth": "1985-06-15" }
  },
  "overall_status": "completed"
}
```
*(Responses contain unified data from Property, Municipality, and Tax modules alongside the identity chunk)*
