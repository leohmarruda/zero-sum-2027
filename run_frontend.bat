@echo off
setlocal
cd /d "%~dp0frontend"

if not exist "node_modules\" (
  echo Installing npm dependencies...
  call npm install
)

echo Starting UI at http://127.0.0.1:5173
echo Using repo-root .env via Vite envDir
call npm run dev -- --host 127.0.0.1 --port 5173
endlocal
