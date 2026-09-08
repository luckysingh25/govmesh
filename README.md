# GovMesh — SIH 26129 MVP

GovMesh is a small hackathon-ready starter for a government-service interoperability platform. It provides a FastAPI backend, a minimal frontend, PostgreSQL and Redis, plus four isolated mock department services.

## Quick start

1. Copy the sample configuration: `cp .env.example .env`
2. Start the complete local stack: `docker compose up --build`
3. Open the frontend at [http://localhost:3000](http://localhost:3000) and API docs at [http://localhost:8000/docs](http://localhost:8000/docs).

## Local backend without Docker

The Python environment is already at `backend/venv`.

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs), or check [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health).

## Services

| Service | Address |
| --- | --- |
| Backend API | `http://localhost:8000` |
| Frontend | `http://localhost:3000` |
| Citizen simulator | `http://localhost:8101` |
| Health simulator | `http://localhost:8102` |
| Education simulator | `http://localhost:8103` |
| Transport simulator | `http://localhost:8104` |

Each department service offers `/health` and `/records/{citizen_id}` for demo-only mocked data. Do not put real citizen data in this MVP.
