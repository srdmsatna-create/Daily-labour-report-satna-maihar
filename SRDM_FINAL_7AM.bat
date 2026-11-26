@echo off
set "SRDM_ENTRY_BAT=%~f0"
set "SRDM_SCHEDULE_TIME=07:00"
set "SRDM_TASK_NAME=SRDM_ALL_REPORTS_DAILY_7AM"
call "%~dp0SRDM_FINAL_8AM.bat" %*
exit /b %errorlevel%
