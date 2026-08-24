@echo off
cd /d "%~dp0"
title VB-G RAM G - One Click Daily Report
echo ======================================================
echo   VB-G RAM G - ONE CLICK DAILY REPORT
echo   Automatic calculation + Muster mapping
echo ======================================================
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0AUTO_DAILY_REPORT.ps1"
echo.
echo ======================================================
echo Finished. Check Daily_Report_DD-MM-YYYY.xlsx
echo ======================================================
pause
