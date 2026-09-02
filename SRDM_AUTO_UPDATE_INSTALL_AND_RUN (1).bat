@echo off
setlocal EnableExtensions EnableDelayedExpansion
title SRDM SATNA - Auto Update Install and Run
color 0A

rem ================================================================
rem SRDM SATNA one-file updater + daily 08:00 AM scheduler installer
rem Expected location: repository root (beside local_auto_update.py)
rem ================================================================

set "TASK_NAME=SRDM Daily Report 8AM"
set "LOG_DIR=%~dp0logs"
set "LOG_FILE=%LOG_DIR%\srdm-auto-update.log"
set "LOCK_DIR=%TEMP%\srdm_satna_update.lock"
set "PY_CMD="

cd /d "%~dp0"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%" >nul 2>&1

call :log ============================================================
call :log Starting SRDM dashboard update from %CD%

rem Prevent two scheduler/manual runs from overlapping.
2>nul mkdir "%LOCK_DIR%" || (
  call :log ERROR: Another SRDM update is already running.
  echo Another update is already running. See "%LOG_FILE%"
  exit /b 20
)

rem Always release the lock through :finish.
if not exist "local_auto_update.py" (
  call :log ERROR: local_auto_update.py is not beside this BAT file.
  echo.
  echo Put this BAT inside:
  echo C:\Users\welcome\Daily-labour-report-satna-maihar
  set "EXIT_CODE=21"
  goto :finish
)

if not exist ".git" (
  call :log ERROR: This folder is not the Git repository root.
  set "EXIT_CODE=22"
  goto :finish
)

where py >nul 2>&1 && set "PY_CMD=py"
if not defined PY_CMD where python >nul 2>&1 && set "PY_CMD=python"
if not defined PY_CMD (
  call :log ERROR: Python was not found.
  set "EXIT_CODE=23"
  goto :finish
)

where git >nul 2>&1 || (
  call :log ERROR: Git was not found.
  set "EXIT_CODE=24"
  goto :finish
)

rem Install/repair the daily scheduler every time. /F makes this idempotent.
schtasks /Create /TN "%TASK_NAME%" /SC DAILY /ST 08:00 /TR "\"%~f0\"" /RL LIMITED /F >>"%LOG_FILE%" 2>&1
if errorlevel 1 (
  call :log WARNING: Scheduler could not be installed. Run this BAT once as Administrator.
) else (
  call :log Scheduler ready: %TASK_NAME% at 08:00 local Windows time.
)

rem Sync source code before fetching. Never overwrite local user edits.
git pull --rebase --autostash >>"%LOG_FILE%" 2>&1
if errorlevel 1 (
  call :log ERROR: git pull/rebase failed. No update was published.
  set "EXIT_CODE=25"
  goto :finish
)

if not exist "data" mkdir "data" >nul 2>&1

rem Repair the missing CSV only from this repository's own history.
if not exist "data\official-summary.csv" (
  call :log official-summary.csv missing; searching Git history...
  del /q "data\official-summary.restore.tmp" >nul 2>&1
  for /f "delims=" %%C in ('git log --all --format^=%%H --diff-filter^=AM -- "data/official-summary.csv" 2^>nul') do (
    if not exist "data\official-summary.csv" (
      git show %%C:data/official-summary.csv >"data\official-summary.restore.tmp" 2>>"%LOG_FILE%"
      if not errorlevel 1 move /y "data\official-summary.restore.tmp" "data\official-summary.csv" >nul
    )
  )
  del /q "data\official-summary.restore.tmp" >nul 2>&1
  if exist "data\official-summary.csv" (
    call :log Restored official-summary.csv from repository history.
  ) else (
    call :log ERROR: Could not restore official-summary.csv from Git history.
    call :log A corrected project package is required; publishing was blocked safely.
    set "EXIT_CODE=26"
    goto :finish
  )
)

call :log Running official data fetch and dashboard rebuild...
%PY_CMD% -u local_auto_update.py >>"%LOG_FILE%" 2>&1
if errorlevel 1 (
  call :log ERROR: local_auto_update.py failed. Old live data was preserved.
  set "EXIT_CODE=30"
  goto :finish
)

rem Require explicit successful status before allowing a Git push.
if not exist "data\fetch-status.json" (
  call :log ERROR: fetch-status.json was not generated. Publishing blocked.
  set "EXIT_CODE=31"
  goto :finish
)
findstr /R /C:"\"ok\"[ ]*:[ ]*true" "data\fetch-status.json" >nul
if errorlevel 1 (
  call :log ERROR: Official fetch status is not OK. Publishing blocked.
  set "EXIT_CODE=32"
  goto :finish
)

for %%F in (auto-data.js auto-status.js index.html data\official-summary.csv data\fetch-status.json) do (
  if not exist "%%F" (
    call :log ERROR: Required output missing: %%F. Publishing blocked.
    set "EXIT_CODE=33"
    goto :finish
  )
)

call :log Validation passed. Publishing generated files...
git add -- auto-data.js auto-status.js index.html data/official-summary.csv data/fetch-status.json >>"%LOG_FILE%" 2>&1
git diff --cached --quiet
if not errorlevel 1 (
  call :log No data changes detected; nothing to publish.
  set "EXIT_CODE=0"
  goto :finish
)

git commit -m "Auto update dashboard data %DATE% %TIME%" >>"%LOG_FILE%" 2>&1
if errorlevel 1 (
  call :log ERROR: Git commit failed.
  set "EXIT_CODE=34"
  goto :finish
)

git pull --rebase >>"%LOG_FILE%" 2>&1
if errorlevel 1 (
  call :log ERROR: Final git pull/rebase failed. Push was not attempted.
  set "EXIT_CODE=35"
  goto :finish
)

git push >>"%LOG_FILE%" 2>&1
if errorlevel 1 (
  call :log ERROR: Git push failed. Commit remains safely on this laptop.
  set "EXIT_CODE=36"
  goto :finish
)

call :log SUCCESS: Dashboard data pushed. GitHub Pages may take 1-3 minutes.
set "EXIT_CODE=0"

:finish
if not defined EXIT_CODE set "EXIT_CODE=99"
rd "%LOCK_DIR%" >nul 2>&1
call :log Finished with exit code %EXIT_CODE%.
echo.
if "%EXIT_CODE%"=="0" (
  color 0A
  echo SUCCESS - update complete. Daily 8:00 AM task is configured.
) else (
  color 0C
  echo UPDATE STOPPED SAFELY - old live dashboard data was not replaced.
  echo Log: "%LOG_FILE%"
)
echo.
if /I not "%~1"=="/silent" pause
exit /b %EXIT_CODE%

:log
echo [%DATE% %TIME%] %*>>"%LOG_FILE%"
echo %*
exit /b 0
