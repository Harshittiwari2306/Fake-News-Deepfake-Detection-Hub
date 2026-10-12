Write-Host "Starting TruthGuard Backend Server (Python 3.12)..." -ForegroundColor Cyan
Set-Location $PSScriptRoot
& ".\venv312\Scripts\uvicorn.exe" app.main:app --reload --port 8000

