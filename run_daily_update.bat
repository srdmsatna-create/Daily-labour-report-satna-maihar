@echo off
setlocal EnableExtensions EnableDelayedExpansion
title SRDM SATNA - All Reports Auto Update
color 0A

rem ================================================================
rem SRDM SATNA - ALL REPORTS AUTO UPDATE
rem Put this file in the repository root, replacing run_daily_update.bat
rem Runs manually and configures the daily 08:00 Windows task.
rem ================================================================

set "TASK_NAME=SRDM Daily Report 8AM"
set "LOG_DIR=%~dp0logs"
set "LOG_FILE=%LOG_DIR%\srdm-auto-update.log"
set "LOCK_DIR=%TEMP%\srdm_satna_all_reports.lock"
set "PY_CMD="
set "EXIT_CODE=0"
set /a REPORT_OK=0
set /a REPORT_FAILED=0

cd /d "%~dp0"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%" >nul 2>&1

call :log ============================================================
call :log Starting SRDM ALL REPORTS update from %CD%

2>nul mkdir "%LOCK_DIR%" || (
  call :log ERROR: Another SRDM update is already running.
  echo Another update is already running. See "%LOG_FILE%"
  exit /b 20
)

if not exist ".git" (
  call :log ERROR: This BAT must be inside the Git repository root.
  set "EXIT_CODE=21"
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

rem Keep the daily task pointed to this exact file.
schtasks /Create /TN "%TASK_NAME%" /SC DAILY /ST 08:00 /TR "\"%~f0\" /silent" /RL LIMITED /F >>"%LOG_FILE%" 2>&1
if errorlevel 1 (
  call :log WARNING: Scheduler could not be installed. Run once as Administrator.
) else (
  call :log Scheduler ready: %TASK_NAME% at 08:00 local Windows time.
)

call :log [1/7] Syncing latest repository code...
git pull --rebase --autostash >>"%LOG_FILE%" 2>&1
if errorlevel 1 (
  call :log ERROR: Initial git pull/rebase failed. Publishing stopped safely.
  set "EXIT_CODE=25"
  goto :finish
)

set "UPDATER="
if exist "local_auto_update.py" set "UPDATER=local_auto_update.py"
if not defined UPDATER if exist "scripts_local\local_auto_update.py" set "UPDATER=scripts_local\local_auto_update.py"
if not defined UPDATER (
  call :log ERROR: local_auto_update.py was not found.
  set "EXIT_CODE=26"
  goto :finish
)

call :log [2/7] Updating official R6.9 dashboard data...
%PY_CMD% -u "%UPDATER%" >>"%LOG_FILE%" 2>&1
if errorlevel 1 (
  call :log WARNING: Official R6.9 fetch failed; previous valid data preserved.
  set /a REPORT_FAILED+=1
) else (
  if exist "scripts\merge_official_summary.py" (
    %PY_CMD% -u "scripts\merge_official_summary.py" >>"%LOG_FILE%" 2>&1
    if errorlevel 1 (
      call :log WARNING: Official data rebuild failed; previous published data remains live.
      set /a REPORT_FAILED+=1
    ) else (
      call :log SUCCESS: Official R6.9 report updated.
      set /a REPORT_OK+=1
    )
  ) else (
    call :log WARNING: merge_official_summary.py missing.
    set /a REPORT_FAILED+=1
  )
)

call :log [3/7] Updating Muster Roll and e-MB report...
if exist "scripts_local\update_muster_emb_monitoring.py" (
  %PY_CMD% -u "scripts_local\update_muster_emb_monitoring.py" --update-only >>"%LOG_FILE%" 2>&1
  if errorlevel 1 (
    call :log WARNING: Muster/e-MB fetch failed; previous valid data preserved.
    set /a REPORT_FAILED+=1
  ) else (
    call :log SUCCESS: Muster/e-MB report updated.
    set /a REPORT_OK+=1
  )
) else (
  call :log WARNING: Muster/e-MB updater is missing.
  set /a REPORT_FAILED+=1
)

call :log [4/7] Updating Shramik Niyojan report...
if exist "scripts_local\update_shramik_niyojan.py" (
  %PY_CMD% -u "scripts_local\update_shramik_niyojan.py" >>"%LOG_FILE%" 2>&1
  if errorlevel 1 (
    call :log WARNING: Shramik Niyojan fetch failed; previous valid data preserved.
    set /a REPORT_FAILED+=1
  ) else (
    call :log SUCCESS: Shramik Niyojan report updated.
    set /a REPORT_OK+=1
  )
) else (
  call :log WARNING: Shramik Niyojan updater is missing.
  set /a REPORT_FAILED+=1
)

call :log [5/7] Updating Yuktdhara and Bhuvan Planning reports...
if exist "scripts_local\update_yuktdhara_monitoring.py" (
  %PY_CMD% -u "scripts_local\update_yuktdhara_monitoring.py" --update-only >>"%LOG_FILE%" 2>&1
  if errorlevel 1 (
    call :log WARNING: Yuktdhara/Bhuvan fetch failed; previous valid data preserved.
    set /a REPORT_FAILED+=1
  ) else (
    call :log SUCCESS: Yuktdhara and Bhuvan Planning reports updated.
    set /a REPORT_OK+=1
  )
) else (
  call :log WARNING: Yuktdhara updater is missing.
  set /a REPORT_FAILED+=1
)

call :log [6/7] Updating VB-G RAM G block statistics...
if exist "scripts_local\update_satna_block_statistics.py" (
  %PY_CMD% -u "scripts_local\update_satna_block_statistics.py" >>"%LOG_FILE%" 2>&1
  if errorlevel 1 (
    call :log WARNING: Block Statistics fetch failed; previous valid data preserved.
    set /a REPORT_FAILED+=1
  ) else (
    call :log SUCCESS: Block Statistics report updated.
    set /a REPORT_OK+=1
  )
) else (
  call :log WARNING: Block Statistics updater is missing.
  set /a REPORT_FAILED+=1
)

if !REPORT_OK! EQU 0 (
  call :log ERROR: No report updated successfully. Nothing will be published.
  set "EXIT_CODE=30"
  goto :finish
)

call :log [7/7] Publishing verified report files...
for %%F in (auto-data.js auto-status.js muster-emb-data.js shramik-niyojan-data.js yuktdhara-data.js yuktdhara-official-data.js vbg-block-stats.js run_daily_update.bat) do (
  if exist "%%F" git add -- "%%F" >>"%LOG_FILE%" 2>&1
)
for %%F in (data\official-summary.csv data\fetch-status.json) do (
  if exist "%%F" git add -- "%%F" >>"%LOG_FILE%" 2>&1
)

git diff --cached --quiet
if not errorlevel 1 (
  call :log No report data changes detected; nothing to publish.
  set "EXIT_CODE=0"
  goto :finish
)

git commit -m "Auto update all dashboard reports %DATE% %TIME%" >>"%LOG_FILE%" 2>&1
if errorlevel 1 (
  call :log ERROR: Git commit failed.
  set "EXIT_CODE=34"
  goto :finish
)

git pull --rebase --autostash >>"%LOG_FILE%" 2>&1
if errorlevel 1 (
  call :log ERROR: Final git pull/rebase failed. Push was not attempted.
  set "EXIT_CODE=35"
  goto :finish
)

git push origin main >>"%LOG_FILE%" 2>&1
if errorlevel 1 (
  call :log ERROR: Git push failed. Commit remains safely on this laptop.
  set "EXIT_CODE=36"
  goto :finish
)

call :log SUCCESS: !REPORT_OK! reports updated; !REPORT_FAILED! failed/preserved. Dashboard pushed.
call :log GitHub Pages may take 1-3 minutes.
set "EXIT_CODE=0"

:finish
if not defined EXIT_CODE set "EXIT_CODE=99"
rd "%LOCK_DIR%" >nul 2>&1
call :log Finished with exit code %EXIT_CODE%.
echo.
if "%EXIT_CODE%"=="0" (
  color 0A
  echo SUCCESS - All available reports update completed.
  echo Updated: !REPORT_OK!   Failed/preserved: !REPORT_FAILED!
) else (
  color 0C
  echo UPDATE STOPPED SAFELY - existing live data was preserved.
  echo Log: "%LOG_FILE%"
)
echo.
if /I not "%~1"=="/silent" pause
exit /b %EXIT_CODE%

:log
echo [%DATE% %TIME%] %*>>"%LOG_FILE%"
echo %*
exit /b 0
