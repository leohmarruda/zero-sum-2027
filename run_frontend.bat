@echo off
setlocal
cd /d "%~dp0frontend"

if not exist "node_modules\" (
  echo Installing npm dependencies...
  call npm install
)

if not exist ".env" if exist ".env.example" (
  copy /y ".env.example" ".env" >nul
)

echo Starting UI at http://127.0.0.1:5173
call npm run dev -- --host 127.0.0.1 --port 5173
endlocal
