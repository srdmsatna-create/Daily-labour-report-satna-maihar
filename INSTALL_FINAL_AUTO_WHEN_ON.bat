@echo off
setlocal
set "REPO=C:\Users\welcome\Daily-labour-report-satna-maihar"
set "SRC=%~dp0"

echo ============================================================
echo VB-G RAM G - FINAL AUTO WHEN LAPTOP IS USED
echo ============================================================
echo.

if not exist "%REPO%\.git" (
  echo ERROR: Repo not found:
  echo %REPO%
  pause
  exit /b 1
)

copy /Y "%SRC%VBGRAMG_AUTO_WHEN_ON.bat" "%REPO%\VBGRAMG_AUTO_WHEN_ON.bat" >nul
if errorlevel 1 (
  echo ERROR: Could not copy runner into repo.
  pause
  exit /b 2
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%SRC%SETUP_AUTO_WHEN_ON.ps1"
echo.
pause
