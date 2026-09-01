@echo off
setlocal EnableExtensions EnableDelayedExpansion
title VBGRAMG CLOUD V7 FIXED COPY

set "REPO=C:\Users\welcome\Daily-labour-report-satna-maihar"
set "SRC=%~dp0"

echo ============================================================
echo VB-G RAM G - CLOUD V7 FIXED INSTALL
echo ============================================================
echo.

if not exist "%REPO%\.git" (
  echo ERROR: Repo not found:
  echo %REPO%
  pause
  exit /b 1
)

if not exist "%SRC%VBGRAMG_WORKFLOW_V2_SAFE.yml" (
  echo ERROR: VBGRAMG_WORKFLOW_V2_SAFE.yml missing.
  pause
  exit /b 2
)
if not exist "%SRC%local_auto_update_cloud_v2.py" (
  echo ERROR: local_auto_update_cloud_v2.py missing.
  pause
  exit /b 3
)
if not exist "%SRC%merge_official_summary.py" (
  echo ERROR: merge_official_summary.py missing.
  pause
  exit /b 4
)

cd /d "%REPO%"

where git >nul 2>nul
if errorlevel 1 (
  echo ERROR: Git not found.
  pause
  exit /b 5
)

for /f "delims=" %%B in ('git branch --show-current') do set "BRANCH=%%B"
if not defined BRANCH set "BRANCH=main"

echo [1/7] Creating folders...
if not exist ".github" md ".github"
if not exist ".github\workflows" md ".github\workflows"
if not exist "scripts_local" md "scripts_local"
if not exist "scripts" md "scripts"

echo.
echo [2/7] Copying files with CMD COPY...
copy /Y "%SRC%VBGRAMG_WORKFLOW_V2_SAFE.yml" ".github\workflows\vbgramg-cloud-auto-v2.yml"
if errorlevel 1 goto :COPYFAIL

copy /Y "%SRC%local_auto_update_cloud_v2.py" "scripts_local\local_auto_update_cloud_v2.py"
if errorlevel 1 goto :COPYFAIL

copy /Y "%SRC%merge_official_summary.py" "scripts\merge_official_summary.py"
if errorlevel 1 goto :COPYFAIL

echo.
echo [3/7] Verifying copied files...
if not exist ".github\workflows\vbgramg-cloud-auto-v2.yml" goto :VERIFYFAIL
if not exist "scripts_local\local_auto_update_cloud_v2.py" goto :VERIFYFAIL
if not exist "scripts\merge_official_summary.py" goto :VERIFYFAIL
echo Copy verification OK.

echo.
echo [4/7] Stage and commit...
git add -f ".github/workflows/vbgramg-cloud-auto-v2.yml"
if errorlevel 1 goto :GITFAIL
git add -f "scripts_local/local_auto_update_cloud_v2.py"
if errorlevel 1 goto :GITFAIL
git add -f "scripts/merge_official_summary.py"
if errorlevel 1 goto :GITFAIL

git diff --cached --quiet
if not errorlevel 1 (
  echo No new content to commit.
) else (
  git commit -m "Install VBGRAMG Cloud Auto Update V2 Safe"
  if errorlevel 1 goto :GITFAIL
)

echo.
echo [5/7] Sync remote safely...
git pull --rebase --autostash origin !BRANCH!
if errorlevel 1 goto :GITFAIL

echo.
echo [6/7] Push...
git push origin !BRANCH!
if errorlevel 1 goto :GITFAIL

echo.
echo [7/7] Verify workflow in HEAD...
git ls-tree -r HEAD --name-only | findstr /I /X ".github/workflows/vbgramg-cloud-auto-v2.yml" >nul
if errorlevel 1 goto :VERIFYHEAD

echo.
echo ============================================================
echo SUCCESS - WORKFLOW PUSHED TO GITHUB
echo ============================================================
echo Open GitHub Actions and press Ctrl+F5.
echo Workflow:
echo   VBGRAMG Cloud Auto Update V2 Safe
echo ============================================================
pause
exit /b 0

:COPYFAIL
echo.
echo ERROR: File copy failed.
goto :FAIL

:VERIFYFAIL
echo.
echo ERROR: Copied file verification failed.
goto :FAIL

:VERIFYHEAD
echo.
echo ERROR: Workflow is not present in HEAD after push.
goto :FAIL

:GITFAIL
echo.
echo ERROR: Git operation failed.
goto :FAIL

:FAIL
echo.
echo ============================================================
echo INSTALL FAILED
echo ============================================================
git status --short
echo.
pause
exit /b 1
