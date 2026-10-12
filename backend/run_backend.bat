@echo off
echo Starting TruthGuard Backend Server (Python 3.12)...
cd /d "%~dp0"
.\venv312\Scripts\uvicorn.exe app.main:app --reload --port 8000
pause

