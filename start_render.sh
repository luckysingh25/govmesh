#!/usr/bin/env bash
# GovMesh — Production Cloud Startup Script for Render / Linux Containers
# Launches all 4 departmental microservices in background and binds gateway to $PORT

echo "=========================================================="
echo "  GovMesh Cloud Deployment: Launching All Services        "
echo "=========================================================="

# 1. Identity Service (Port 8101)
(cd services/identity-service && python -m uvicorn app:app --host 127.0.0.1 --port 8101) &

# 2. Municipality Service (Port 8102)
(cd services/municipality-service && python -m uvicorn app:app --host 127.0.0.1 --port 8102) &

# 3. Property Service (Port 8103)
(cd services/property-service && python -m uvicorn app:app --host 127.0.0.1 --port 8103) &

# 4. Tax Service (Port 8104)
(cd services/tax-service && python -m uvicorn app:app --host 127.0.0.1 --port 8104) &

# Wait 2 seconds for microservices to bind
sleep 2

# 5. Core Gateway (Binds to Render $PORT)
echo "Launching Core Gateway on port ${PORT:-8000}..."
cd backend && exec python -m uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
