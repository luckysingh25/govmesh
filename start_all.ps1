# GovMesh — Start All Microservices & Core Platform
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Starting GovMesh Federated Platform & Microservices     " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$root = $PSScriptRoot
if (-not $root) { $root = Get-Location }

# Determine Python executable
$python = "$root\backend\venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $python = "$root\backend\.venv\Scripts\python.exe"
}
if (-not (Test-Path $python)) {
    $python = "python"
}

Write-Host "Using Python interpreter: $python" -ForegroundColor DarkCyan

# 1. Identity Service (Port 8101)
Write-Host "[1/6] Launching Identity Service on Port 8101..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\services\identity-service'; & '$python' -m uvicorn app:app --reload --port 8101"

# 2. Municipality Service (Port 8102)
Write-Host "[2/6] Launching Municipality Service on Port 8102..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\services\municipality-service'; & '$python' -m uvicorn app:app --reload --port 8102"

# 3. Property Service (Port 8103)
Write-Host "[3/6] Launching Property Service on Port 8103..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\services\property-service'; & '$python' -m uvicorn app:app --reload --port 8103"

# 4. Tax Service (Port 8104)
Write-Host "[4/6] Launching Tax Service on Port 8104..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\services\tax-service'; & '$python' -m uvicorn app:app --reload --port 8104"

# 5. Backend Core Gateway (Port 8000)
Write-Host "[5/6] Launching Backend Core Gateway on Port 8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\backend'; & '$python' -m uvicorn app.main:app --reload --port 8000"

# 6. Frontend UI (Port 3000)
Write-Host "[6/6] Launching Frontend UI on Port 3000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\frontend'; npm run dev"

Write-Host "`nAll 6 GovMesh processes have been launched in separate terminal windows!" -ForegroundColor Yellow
Write-Host "Frontend Portal:  http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
