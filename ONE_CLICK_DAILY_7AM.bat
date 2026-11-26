@echo off
set "SRDM_ENTRY_BAT=%~f0"
call "%~dp0SRDM_FINAL_7AM.bat" %*
exit /b %errorlevel%
