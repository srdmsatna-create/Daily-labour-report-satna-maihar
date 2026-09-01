@echo off
setlocal EnableExtensions EnableDelayedExpansion
title VBGRAMG AUTO UPDATE WHEN LAPTOP IS ON

set "REPO=C:\Users\welcome\Daily-labour-report-satna-maihar"
set "LOGDIR=%REPO%\logs"
set "LOG=%LOGDIR%\auto-when-on.log"

if not exist "%LOGDIR%" mkdir "%LOGDIR%" >nul 2>nul

call :MAIN >> "%LOG%" 2>&1
exit /b %ERRORLEVEL%

:MAIN
echo.
echo ============================================================
echo START %DATE% %TIME%
echo ============================================================

if not exist "%REPO%\.git" (
  echo ERROR: Repo not found.
  exit /b 10
)

cd /d "%REPO%"

set "PY="
where py >nul 2>nul
if not errorlevel 1 set "PY=py"
if not defined PY (
  where python >nul 2>nul
  if not errorlevel 1 set "PY=python"
)
if not defined PY (
  echo ERROR: Python not found.
  exit /b 11
)

where git >nul 2>nul
if errorlevel 1 (
  echo ERROR: Git not found.
  exit /b 12
)

echo Waiting for network...
for /L %%I in (1,1,12) do (
  ping -n 1 github.com >nul 2>nul
  if not errorlevel 1 goto :NETOK
  timeout /t 10 /nobreak >nul
)
echo ERROR: Internet not available.
exit /b 13

:NETOK
echo Internet OK.

echo [1/6] Pull latest
git pull --rebase --autostash
if errorlevel 1 exit /b 20

set "UPDATER="
if exist "local_auto_update.py" set "UPDATER=local_auto_update.py"
if not defined UPDATER if exist "scripts_local\local_auto_update.py" set "UPDATER=scripts_local\local_auto_update.py"
if not defined UPDATER if exist "scripts\local_auto_update.py" set "UPDATER=scripts\local_auto_update.py"

if not defined UPDATER (
  echo ERROR: local_auto_update.py not found.
  exit /b 21
)

echo [2/6] Fetch official VB-G RAM G data
%PY% "%UPDATER%"
if errorlevel 1 (
  echo ERROR: Official fetch failed. Existing verified dashboard data remains unchanged.
  exit /b 22
)

echo [3/6] Merge dashboard data
if not exist "scripts\merge_official_summary.py" (
  echo ERROR: merge_official_summary.py not found.
  exit /b 23
)
%PY% "scripts\merge_official_summary.py"
if errorlevel 1 exit /b 24

echo [4/6] Verify generated files
if not exist "data\official-summary.csv" exit /b 25
if not exist "data\fetch-status.json" exit /b 26
if not exist "auto-data.js" exit /b 27
if not exist "auto-status.js" exit /b 28

echo [5/6] Commit verified data/status only
git add "data\official-summary.csv" "data\fetch-status.json" "auto-data.js" "auto-status.js"

git diff --cached --quiet
if not errorlevel 1 (
  echo No actual data change.
  echo END %DATE% %TIME% SUCCESS-NOCHANGE
  exit /b 0
)

git commit -m "Automatic VBGRAMG update when laptop online"
if errorlevel 1 exit /b 30

echo [6/6] Push
git push
if errorlevel 1 exit /b 31

echo END %DATE% %TIME% SUCCESS-PUSHED
exit /b 0
