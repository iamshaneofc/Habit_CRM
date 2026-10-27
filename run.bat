@echo off
echo Starting Habit CRM Server...
python -m uvicorn main:app --reload --port 8000
pause
