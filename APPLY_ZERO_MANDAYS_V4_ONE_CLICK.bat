@echo off
setlocal EnableExtensions
color 0A
title SRDM Zero Mandays V4 - One Click Deploy

REM Find repository root from current folder
for /f "delims=" %%R in ('git rev-parse --show-toplevel 2^>nul') do set "REPO=%%R"
if not defined REPO (
  echo ERROR: This BAT must be run from inside your GitHub dashboard repository folder.
  echo Put this BAT + patch_zero_mandays_v4.py in the same dashboard repo folder, then run again.
  pause
  exit /b 1
)
cd /d "%REPO%"
echo Repository: %REPO%

git status --short --branch

echo.
echo [1/6] Pulling latest main...
git pull --ff-only origin main
if errorlevel 1 goto :fail

if not exist index.html (
  echo ERROR: %REPO%\index.html not found.
  goto :fail
)

REM Keep backup outside Git tracking noise where possible
if not exist .srdm_backup mkdir .srdm_backup >nul 2>&1
copy /Y index.html .srdm_backup\index_before_zero_v4.html >nul

echo [2/6] Patching CURRENT tracked index.html...
python "%~dp0patch_zero_mandays_v4.py" "%REPO%"
if errorlevel 1 (
  py -3 "%~dp0patch_zero_mandays_v4.py" "%REPO%"
  if errorlevel 1 goto :fail
)

echo [3/6] Verifying tab + live Mandays source...
findstr /C:"id=\"srdmZeroMandaysBtn\"" index.html >nul || goto :verifyfail
findstr /C:"SRDM_ZERO_MANDAYS_FINAL_V4_START" index.html >nul || goto :verifyfail
findstr /C:"window.SRDM_V8_MONTHLY" index.html >nul || goto :verifyfail

git add -f index.html

echo [4/6] Confirming REAL git diff...
git diff --cached --quiet -- index.html
if not errorlevel 1 (
  echo ERROR: index.html still has no staged change. Nothing will be falsely reported as SUCCESS.
  goto :fail
)
git diff --cached --stat -- index.html

echo [5/6] Committing...
git commit -m "Deploy visible Zero Mandays tab V4 using live Mandays data"
if errorlevel 1 goto :fail

for /f %%H in ('git rev-parse --short HEAD') do set "HASH=%%H"
echo Commit created: %HASH%

echo [6/6] Pushing to origin/main...
git push origin main
if errorlevel 1 goto :fail

echo.
echo ============================================================
echo SUCCESS: REAL commit %HASH% pushed to origin/main.
echo Zero Mandays tab is in tracked index.html.
echo Opening dashboard with cache-bypass...
echo ============================================================
start "" "https://srdmsatna.online/?v=%HASH%"
pause
exit /b 0

:verifyfail
echo ERROR: Verification failed. Tab/script/live data marker missing.
goto :fail

:fail
echo.
echo FAILED: No false SUCCESS message. Please send this window screenshot.
pause
exit /b 1
