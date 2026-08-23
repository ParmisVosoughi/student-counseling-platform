@echo off
cd /d "%~dp0"
title Student Counseling Platform - Stop
echo Stopping the application...
docker compose down
echo Done. Your database data has NOT been deleted.
pause
