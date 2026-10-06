@echo off
setlocal
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
cd /d "C:\Users\welcome\Daily-labour-report-satna-maihar"
set "SRDM_RUN_RESULT=0"
echo START %date% %time%
call ONE_CLICK_DASHBOARD_DATA_UPDATE_FIXED.bat --no-pause
if errorlevel 1 set "SRDM_RUN_RESULT=1"
call SRDM_GP_ALL_IN_ONE_DAILY_8AM_FIXED.bat --no-pause
if errorlevel 1 set "SRDM_RUN_RESULT=1"
echo END %date% %time% RESULT=%SRDM_RUN_RESULT%
exit /b %SRDM_RUN_RESULT%
