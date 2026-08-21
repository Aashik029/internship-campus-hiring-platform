@echo off
setlocal
title Capstone - Backend + Frontend Launcher
echo Starting Internship and Campus Hiring Platform...
echo.

cd /d "D:\capstone"

if exist ".venv\Scripts\python.exe" goto backend_ready
echo [INFO] Creating virtual environment (Python 3.12)...
py -3.12 -m venv .venv
echo [INFO] Installing backend dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt

:backend_ready
if exist "frontend\node_modules" goto frontend_ready
echo [INFO] Installing frontend dependencies...
pushd frontend
call npm install
popd

:frontend_ready
echo [START] Launching backend on http://localhost:8000 ...
start "Backend API" cmd /k "cd /d D:\capstone && D:\capstone\.venv\Scripts\python.exe -m uvicorn app.main:app --reload"

echo [START] Launching frontend on http://localhost:5173 ...
start "Frontend" cmd /k "cd /d D:\capstone\frontend && npm run dev"

echo.
echo Both servers started in separate windows:
echo   Backend  : http://localhost:8000   (Swagger: http://localhost:8000/docs)
echo   Frontend : http://localhost:5173
echo.
echo Keep both windows open. Press any key to close this launcher...
pause
endlocal