@echo off
setlocal
cd /d "%~dp0"
title Student Counseling Platform - Reset Data
color 0C
echo.
echo WARNING: This deletes ALL local project data and recreates demo data on next start.
echo.
set /p CONFIRM=Type DELETE to continue: 
if /I not "%CONFIRM%"=="DELETE" (
  echo Cancelled.
  pause
  exit /b 0
)
docker compose down -v --remove-orphans
echo.
echo Data deleted. Run START.bat to create a fresh database.
pause
