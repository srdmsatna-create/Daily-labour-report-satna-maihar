@echo off
setlocal EnableExtensions EnableDelayedExpansion
title VBGRAMG FINAL AUTO WHEN LAPTOP IS USED V2

set "REPO=C:\Users\welcome\Daily-labour-report-satna-maihar"
set "SRC=%~dp0"
set "SRCFILE=%SRC%VBGRAMG_AUTO_WHEN_ON.bat"
set "DSTFILE=%REPO%\VBGRAMG_AUTO_WHEN_ON.bat"

echo ============================================================
echo VB-G RAM G - FINAL AUTO WHEN LAPTOP IS USED V2
echo ============================================================
echo.

if not exist "%REPO%\.git" (
  echo ERROR: Repo not found:
  echo %REPO%
  pause
  exit /b 1
)

if not exist "%SRCFILE%" (
  echo ERROR: VBGRAMG_AUTO_WHEN_ON.bat is missing beside installer.
  pause
  exit /b 2
)

for %%A in ("%SRCFILE%") do set "SRCFULL=%%~fA"
for %%A in ("%DSTFILE%") do set "DSTFULL=%%~fA"

echo Source: !SRCFULL!
echo Target: !DSTFULL!
echo.

if /I "!SRCFULL!"=="!DSTFULL!" (
  echo Runner is already inside the repo. Copy skipped.
) else (
  echo Copying runner into repo...
  copy /Y "%SRCFILE%" "%DSTFILE%" >nul
  if errorlevel 1 (
    echo ERROR: Could not copy runner into repo.
    pause
    exit /b 3
  )
  echo Copy OK.
)

if not exist "%DSTFILE%" (
  echo ERROR: Runner not found in repo after copy.
  pause
  exit /b 4
)

echo.
echo Installing Windows scheduled task...
powershell -NoProfile -ExecutionPolicy Bypass -File "%SRC%SETUP_AUTO_WHEN_ON.ps1"
if errorlevel 1 (
  echo.
  echo ERROR: Scheduled task setup failed.
  echo Try: Right-click this BAT ^> Run as administrator
  pause
  exit /b 5
)

echo.
echo ============================================================
echo SUCCESS - AUTO WHEN LAPTOP ON INSTALLED
echo ============================================================
echo No daily BAT clicking required.
echo Update runs at login and every hour while laptop is ON.
echo ============================================================
pause
