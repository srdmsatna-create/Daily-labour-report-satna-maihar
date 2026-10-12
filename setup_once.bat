@echo off
title SRDM Satna - One Time Setup
cd /d "%~dp0"

echo ===============================================
echo   ONE-TIME SETUP - Installing required software
echo   Yeh sirf pehli baar chalana hai
echo ===============================================
echo.
echo Installing Python packages (playwright, requests)...
pip install playwright requests

echo.
echo Downloading browser for automation (thoda time lagega)...
python -m playwright install chromium

echo.
echo ===============================================
echo   SETUP COMPLETE!
echo   Ab aap 'run_daily_update.bat' ko double-click
echo   karke roz update chala sakte hain.
echo ===============================================
pause
