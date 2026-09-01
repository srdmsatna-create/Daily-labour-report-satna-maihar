@echo off
setlocal EnableExtensions EnableDelayedExpansion
title VB-G RAM G Live Update - SATNA MAIHAR

REM ============================================================
REM VB-G RAM G LIVE UPDATE
REM Put this .bat file in the ROOT of the GitHub repository.
REM It will:
REM   1) Protect uncommitted local work
REM   2) Sync latest main
REM   3) Fetch official data from this PC/session
REM   4) Apply + validate update
REM   5) Commit only report output files
REM   6) Push to GitHub
REM ============================================================

cd /d "%~dp0"

echo.
echo ============================================================
echo   VB-G RAM G LIVE UPDATE - SATNA / MAIHAR
echo ============================================================
echo Repo: %CD%
echo.

REM ---- Basic checks ----
if not exist ".git" (
    echo [ERROR] This BAT is not inside the GitHub repository root.
    echo Put LIVE_UPDATE_VBGRAM.bat in the same folder where .git exists.
    pause
    exit /b 1
)

if not exist "scripts\fetch_official_vbgram.py" (
    echo [ERROR] scripts\fetch_official_vbgram.py not found.
    pause
    exit /b 1
)

where git >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git is not available in PATH.
    pause
    exit /b 1
)

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not available in PATH.
    pause
    exit /b 1
)

REM ---- Protect existing manual work ----
for /f "delims=" %%A in ('git status --porcelain') do (
    echo [STOP] Uncommitted local changes were found.
    echo.
    git status --short
    echo.
    echo Nothing has been changed by this updater.
    echo Commit or safely save your current work first, then run again.
    pause
    exit /b 2
)

echo [1/6] Syncing latest main...
git fetch origin main
if errorlevel 1 goto :fail

git pull --rebase origin main
if errorlevel 1 goto :fail

echo.
echo [2/6] Fetching official VB-G RAM G data from local PC...
python scripts\fetch_official_vbgram.py
if errorlevel 1 (
    echo.
    echo [ERROR] Official data fetch failed.
    echo Existing dashboard/report files were NOT committed or pushed.
    pause
    exit /b 3
)

echo.
echo [3/6] Applying official update...
python scripts\apply_auto_update.py
if errorlevel 1 goto :fail

echo.
echo [4/6] Validating published data...
python scripts\validate_auto_data.py
if errorlevel 1 (
    echo.
    echo [ERROR] Validation failed. Nothing will be pushed.
    pause
    exit /b 4
)

echo.
echo [5/6] Preparing report files...
git add -- auto-data.js auto-status.js official-summary.csv fetch-status.json ongoing-details.js index.html 2>nul
if exist "data\fetch-status.json" git add -- "data\fetch-status.json"
if exist "data" git add -u -- "data"

git diff --cached --quiet
if not errorlevel 1 (
    echo.
    echo [OK] No new report changes found. GitHub is already up to date.
    pause
    exit /b 0
)

for /f "tokens=1-3 delims=/-. " %%a in ("%date%") do set TODAY=%date%
for /f "tokens=1-2 delims=: " %%a in ("%time%") do set NOW=%time%

git commit -m "Automatic VBGRAMG update from local PC"
if errorlevel 1 goto :fail

echo.
echo [6/6] Pushing live update to GitHub...
git pull --rebase origin main
if errorlevel 1 goto :fail

git push origin main
if errorlevel 1 goto :fail

echo.
echo ============================================================
echo   SUCCESS - LIVE UPDATE PUSHED TO GITHUB
echo ============================================================
echo Dashboard will update after GitHub Pages refresh.
echo.
pause
exit /b 0

:fail
echo.
echo ============================================================
echo   UPDATE STOPPED - CHECK THE ERROR ABOVE
echo ============================================================
echo No forced reset was used.
echo Your existing repository work was not intentionally overwritten.
echo.
pause
exit /b 1
