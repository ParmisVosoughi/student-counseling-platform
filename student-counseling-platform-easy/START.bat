@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Student Counseling Platform - Start

echo.
echo ==============================================
echo   Student Counseling Platform - Easy Start
echo ==============================================
echo.

where docker >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Docker Desktop is not installed or docker is not in PATH.
  echo Install/open Docker Desktop, then run START.bat again.
  echo.
  pause
  exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
  echo Docker Desktop is installed but is not running.
  echo Trying to start Docker Desktop...
  if exist "C:\Program Files\Docker\Docker\Docker Desktop.exe" start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
  echo Waiting for Docker Engine...
  for /l %%I in (1,1,60) do (
    docker info >nul 2>&1 && goto docker_ready
    timeout /t 2 /nobreak >nul
  )
  echo [ERROR] Docker Engine did not start. Please open Docker Desktop and try again.
  pause
  exit /b 1
)

:docker_ready
echo Docker is ready.

echo Stopping any previous copy of this project...
docker compose down --remove-orphans >nul 2>&1

for /f %%P in ('powershell -NoProfile -Command "$p=18088; while (Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue) { $p++ }; Write-Output $p"') do set APP_PORT=%%P
if not defined APP_PORT set APP_PORT=18088
set CORS_ALLOWED_ORIGINS=http://localhost:%APP_PORT%

echo %APP_PORT%>.app-port
echo Using local address: http://localhost:%APP_PORT%
echo.
echo Building and starting the application. First run can take several minutes...
echo.

docker compose up -d --build
if errorlevel 1 goto failed

echo.
echo Waiting for the application to become ready...
for /l %%I in (1,1,90) do (
  powershell -NoProfile -Command "try { $r=Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:%APP_PORT%/' -TimeoutSec 2; if ($r.StatusCode -ge 200) { exit 0 } } catch {}; exit 1" >nul 2>&1
  if not errorlevel 1 goto ready
  timeout /t 2 /nobreak >nul
)

echo [ERROR] The application did not become ready in time.
goto failed

:ready
echo.
echo ==============================================
echo   READY
echo   Address: http://localhost:%APP_PORT%
echo.
echo   Admin username: admin
echo   Admin password: Admin123!
echo.
echo   Supervisor: supervisor1 / Supervisor123!
echo   Advisor:    advisor1 / Advisor123!
echo ==============================================
echo.
start "" "http://localhost:%APP_PORT%"
echo The browser should open automatically.
echo You can close this window now; Docker will keep the app running.
pause
exit /b 0

:failed
echo.
echo Startup failed. Last container logs:
echo ----------------------------------------------
docker compose logs --tail=120
echo ----------------------------------------------
echo.
echo Keep this window and send a screenshot if needed.
pause
exit /b 1
