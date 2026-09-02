@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ============================================================
REM SRDM SATNA - ONE CLICK DASHBOARD DATA UPDATE
REM Double click this BAT to fetch latest data and publish to GitHub
REM ============================================================

title SRDM SATNA - One Click Dashboard Data Update

set "REPO=C:\Users\welcome\Daily-labour-report-satna-maihar"

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

echo [1/6] Python detected: %PYTHON_CMD%

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

echo [2/6] Updating official data...
echo Using: %UPDATER%
echo.
%PYTHON_CMD% "%UPDATER%"
if errorlevel 1 (
    echo.
    echo ERROR: Data update failed.
    echo Please read the error shown above.
    pause
    exit /b 1
)

echo.
echo Official data fetch: OK

if exist "scripts_local\update_satna_block_statistics.py" (
    echo Updating Satna block-wise At-a-Glance statistics...
    %PYTHON_CMD% "scripts_local\update_satna_block_statistics.py"
    if errorlevel 1 (
        echo ERROR: Satna block statistics update failed. Publishing stopped.
        pause
        exit /b 1
    )
)

REM ------------------------------------------------------------
REM YUKTDHARA_AUTO_UPDATE_V1

%PYTHON_CMD% "scripts_local\update_yuktdhara_monitoring.py" --update-only

if errorlevel 1 (echo ERROR: Yuktdhara update failed.& pause& exit /b 1)



REM MUSTER_EMB_AUTO_UPDATE_V1
%PYTHON_CMD% "scripts_local\update_muster_emb_monitoring.py" --update-only
if errorlevel 1 (echo ERROR: Muster e-MB update failed.& pause& exit /b 1)

REM 3. Rebuild dashboard data if merge/build scripts exist
REM ------------------------------------------------------------
echo [3/6] Rebuilding dashboard data files...
set "BUILD_DONE=0"

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

REM ------------------------------------------------------------
REM 4. Basic verification
REM ------------------------------------------------------------
echo.
echo [4/6] Verifying files...
if not exist "index.html" (
    echo ERROR: index.html not found in repo.
    pause
    exit /b 1
)

if exist "data\official-summary.csv" echo   official-summary.csv : OK
if exist "auto-data.js" echo   auto-data.js          : OK
if exist "auto-status.js" echo   auto-status.js        : OK
if exist "index.html" echo   index.html            : OK

REM ------------------------------------------------------------
REM 5. Git commit + push when repo is connected
REM ------------------------------------------------------------
echo.
echo [5/6] Publishing changes...
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

echo Pulling latest remote changes...
git pull --rebase
if errorlevel 1 (
    echo.
    echo ERROR: git pull --rebase failed.
    echo Resolve Git conflict, then run this BAT again.
    pause
    exit /b 1
)

echo Pushing to GitHub...
git push
if errorlevel 1 (
    echo.
    echo ERROR: Git push failed.
    pause
    exit /b 1
)

echo GitHub publish: OK

:DONE
echo.
echo [6/6] COMPLETE
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
