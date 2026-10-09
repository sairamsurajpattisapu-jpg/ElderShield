@echo off
echo ======================================================================
echo    ElderShield — Real-Time Scam Call Detection for Elderly Users
echo    Hack With Vizag 4.0 • Problem Statement HWV4-PS05
echo ======================================================================
echo.

echo [1/2] Starting ElderShield Python Backend on port 8000...
start "ElderShield-Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/2] Starting ElderShield React Frontend on port 5173...
start "ElderShield-Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ======================================================================
echo ElderShield services launched!
echo - Frontend: http://localhost:5173
echo - Backend API: http://localhost:8000/docs
echo ======================================================================
pause
