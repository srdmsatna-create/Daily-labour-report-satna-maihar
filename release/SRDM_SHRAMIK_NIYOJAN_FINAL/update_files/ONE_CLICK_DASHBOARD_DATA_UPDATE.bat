@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ============================================================
REM SRDM SATNA - ONE CLICK DASHBOARD DATA UPDATE
REM Double click this BAT to fetch latest data and publish to GitHub
REM ============================================================

title SRDM SATNA - One Click Dashboard Data Update

for %%I in ("%~dp0.") do set "REPO=%%~fI"

cls
echo ============================================================
echo      SRDM SATNA - DASHBOARD DATA AUTO UPDATE
echo ============================================================
echo.
echo Repo: %REPO%
echo.

if not exist "%REPO%" (
    echo ERROR: Dashboard folder not found:
    echo %REPO%
    echo.
    echo Edit REPO path inside this BAT if your folder has moved.
    pause
    exit /b 1
)

cd /d "%REPO%"

REM ------------------------------------------------------------
REM 1. Detect Python
REM ------------------------------------------------------------
set "PYTHON_CMD="
where py >nul 2>nul
if not errorlevel 1 set "PYTHON_CMD=py"
if not defined PYTHON_CMD (
    where python >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=python"
)

if not defined PYTHON_CMD (
    echo ERROR: Python is not installed or not available in PATH.
    echo Install Python and try again.
    pause
    exit /b 1
)

echo [1/9] Python detected: %PYTHON_CMD%

REM ------------------------------------------------------------
REM 2. Locate local updater
REM ------------------------------------------------------------
set "UPDATER="
if exist "local_auto_update.py" set "UPDATER=local_auto_update.py"
if not defined UPDATER if exist "scripts_local\local_auto_update.py" set "UPDATER=scripts_local\local_auto_update.py"
if not defined UPDATER if exist "scripts\local_auto_update.py" set "UPDATER=scripts\local_auto_update.py"

if not defined UPDATER (
    echo.
    echo ERROR: local_auto_update.py not found.
    echo Expected one of these locations:
    echo   %REPO%\local_auto_update.py
    echo   %REPO%\scripts_local\local_auto_update.py
    echo   %REPO%\scripts\local_auto_update.py
    echo.
    pause
    exit /b 1
)

echo [2/9] Updating R6.9 official data...
echo Using: %UPDATER%
echo.
%PYTHON_CMD% "%UPDATER%"
if errorlevel 1 (
    echo.
    echo WARNING: Official data fetch failed.
    echo Existing dashboard data will be preserved.
    echo UI and other local file changes will still be published to GitHub.
    echo.
    set DATA_FETCH_FAILED=1
) else (
    echo.
    echo Official data fetch: OK
    set DATA_FETCH_FAILED=0
)

REM ------------------------------------------------------------
REM 3-5. Update all other live portal reports
REM ------------------------------------------------------------
echo.
echo [3/9] Updating Muster Roll and e-MB report...
if exist "scripts_local\update_muster_emb_monitoring.py" (
    %PYTHON_CMD% "scripts_local\update_muster_emb_monitoring.py" --update-only
    if errorlevel 1 echo WARNING: Muster/e-MB fetch failed; previous valid data preserved.
)

echo.
echo [4/9] Updating Shramik Niyojan Persondays report...
if exist "scripts_local\update_shramik_niyojan.py" (
    %PYTHON_CMD% "scripts_local\update_shramik_niyojan.py"
    if errorlevel 1 echo WARNING: Shramik Niyojan fetch failed; previous valid data preserved.
)

echo.
echo [5/9] Updating Yuktdhara and VB-G RAM G statistics...
if exist "scripts_local\update_yuktdhara_monitoring.py" (
    %PYTHON_CMD% "scripts_local\update_yuktdhara_monitoring.py" --update-only
    if errorlevel 1 echo WARNING: Yuktdhara fetch failed; previous valid data preserved.
)
if exist "scripts_local\update_satna_block_statistics.py" (
    %PYTHON_CMD% "scripts_local\update_satna_block_statistics.py"
    if errorlevel 1 echo WARNING: Block statistics fetch failed; previous valid data preserved.
)

REM ------------------------------------------------------------
REM 6. Rebuild dashboard data if merge/build scripts exist
REM ------------------------------------------------------------
echo [6/9] Rebuilding dashboard data files...
set BUILD_DONE=0

if "%DATA_FETCH_FAILED%"=="1" (
    echo Data fetch failed - skipping rebuild to preserve existing dashboard data.
    goto AFTER_BUILD
)

if exist "scripts\merge_official_summary.py" (
    %PYTHON_CMD% "scripts\merge_official_summary.py"
    if errorlevel 1 goto :BUILD_ERROR
    set "BUILD_DONE=1"
)

if exist "scripts\build_dashboard_data.py" (
    %PYTHON_CMD% "scripts\build_dashboard_data.py"
    if errorlevel 1 goto :BUILD_ERROR
    set "BUILD_DONE=1"
)

if exist "build_dashboard_data.py" (
    %PYTHON_CMD% "build_dashboard_data.py"
    if errorlevel 1 goto :BUILD_ERROR
    set "BUILD_DONE=1"
)

if "!BUILD_DONE!"=="0" (
    echo No separate rebuild script found - updater output will be used directly.
) else (
    echo Dashboard data rebuild: OK
)

:AFTER_BUILD
REM ------------------------------------------------------------
REM 7. Basic verification
REM ------------------------------------------------------------
echo.
echo [7/9] Verifying files...
if not exist "index.html" (
    echo ERROR: index.html not found in repo.
    pause
    exit /b 1
)

if exist "data\official-summary.csv" echo   official-summary.csv : OK
if exist "auto-data.js" echo   auto-data.js          : OK
if exist "auto-status.js" echo   auto-status.js        : OK
if exist "muster-emb-data.js" echo   muster-emb-data.js    : OK
if exist "shramik-niyojan-data.js" echo   shramik-niyojan-data.js : OK
if exist "index.html" echo   index.html            : OK

REM ------------------------------------------------------------
REM 8. Git sync, commit and push when repo is connected
REM ------------------------------------------------------------
echo.
echo [8/9] Publishing changes...
if not exist ".git" (
    echo Git repository not detected.
    echo Local data update is complete; skipping GitHub publish.
    goto :DONE
)

where git >nul 2>nul
if errorlevel 1 (
    echo Git command not found.
    echo Local data update is complete; skipping GitHub publish.
    goto :DONE
)

echo Syncing latest remote changes before commit...
git pull --rebase --autostash
if errorlevel 1 (
    echo.
    echo ERROR: Git sync failed. Local dashboard files are safe.
    echo Run git status and resolve the reported conflict.
    pause
    exit /b 1
)

git add -A

git diff --cached --quiet
if not errorlevel 1 (
    echo No new file changes found. Nothing to commit.
) else (
    git commit -m "Auto update dashboard data"
    if errorlevel 1 (
        echo ERROR: Git commit failed.
        pause
        exit /b 1
    )
)

echo Pushing to GitHub...
git push origin main
if errorlevel 1 (
    echo.
    echo ERROR: Git push failed.
    pause
    exit /b 1
)

echo GitHub publish: OK

:DONE
echo.
echo [9/9] COMPLETE
echo ============================================================
echo SUCCESS - DASHBOARD DATA UPDATED
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set TODAY=%%a-%%b-%%c
echo.
echo Wait 1-3 minutes for GitHub Pages deployment.
echo Then open srdmsatna.online and press Ctrl+F5.
echo ============================================================
echo.
pause
exit /b 0

:BUILD_ERROR
echo.
echo ERROR: Dashboard rebuild script failed.
pause
exit /b 1
