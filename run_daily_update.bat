@echo off
REM SRDM Satna - Daily Auto Update (runs on your own PC)
REM Place this file INSIDE your cloned repository folder, next to index.html

cd /d "%~dp0"

echo ===============================================
echo  SRDM Satna Daily Update - %date% %time%
echo ===============================================

echo.
echo [1/4] Fetching latest report from official portal...
python scripts_local\local_auto_update.py
if errorlevel 1 (
    echo Fetch failed - stopping. Check the message above.
    pause
    exit /b 1
)

echo.
echo [2/4] Rebuilding auto-data.js from CSV...
python scripts\merge_official_summary.py

echo.
echo [3/4] Committing changes to Git...
git add auto-data.js auto-status.js data\official-summary.csv data\fetch-status.json
git commit -m "Auto update daily report data (local PC fetch)"

echo.
echo [4/4] Pushing to GitHub...
git push origin main

echo.
echo ===============================================
echo  Done. Site will update in 1-2 minutes.
echo ===============================================
pause
