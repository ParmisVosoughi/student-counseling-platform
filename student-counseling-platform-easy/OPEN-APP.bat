@echo off
cd /d "%~dp0"
if exist .app-port (
  set /p APP_PORT=<.app-port
) else (
  set APP_PORT=18088
)
start "" "http://localhost:%APP_PORT%"
