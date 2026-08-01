@echo off
setlocal
cd /d "%~dp0backend"

if not exist ".venv\Scripts\python.exe" (
  echo Creating venv...
  python -m venv .venv
  call .venv\Scripts\activate.bat
  pip install -r requirements.txt
  if exist "..\..\llmcall" pip install -e "..\..\llmcall"
) else (
  call .venv\Scripts\activate.bat
)

echo Starting API at http://127.0.0.1:8000 (routes under /api)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
endlocal
