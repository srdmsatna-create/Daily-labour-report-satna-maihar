@echo off
setlocal EnableExtensions EnableDelayedExpansion
title VBGRAMG CLOUD V5 SIMPLE INSTALL

set "REPO=C:\Users\welcome\Daily-labour-report-satna-maihar"
set "SRC=%~dp0"

echo ============================================================
echo VB-G RAM G - CLOUD V5 SIMPLE INSTALL
echo All source files are visible in this same folder.
echo ============================================================
echo.

if not exist "%REPO%\.git" (
  echo ERROR: Repo not found:
  echo %REPO%
  pause
  exit /b 1
)

if not exist "%SRC%VBGRAMG_WORKFLOW_V2_SAFE.yml" (
  echo ERROR: VBGRAMG_WORKFLOW_V2_SAFE.yml missing beside this BAT.
  pause
  exit /b 2
)
if not exist "%SRC%local_auto_update_cloud_v2.py" (
  echo ERROR: local_auto_update_cloud_v2.py missing beside this BAT.
  pause
  exit /b 3
)
if not exist "%SRC%merge_official_summary.py" (
  echo ERROR: merge_official_summary.py missing beside this BAT.
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

echo [1/7] Pull latest with AUTOSTASH...
git pull --rebase --autostash origin !BRANCH!
if errorlevel 1 goto :FAIL

echo.
echo [2/7] Create required folders...
if not exist ".github" mkdir ".github"
if not exist ".github\workflows" mkdir ".github\workflows"
if not exist "scripts_local" mkdir "scripts_local"
if not exist "scripts" mkdir "scripts"

echo.
echo [3/7] Copy files...
copy /Y "%SRC%VBGRAMG_WORKFLOW_V2_SAFE.yml" ".github\workflows\vbgramg-cloud-auto-v2.yml"
if errorlevel 1 goto :FAIL

copy /Y "%SRC%local_auto_update_cloud_v2.py" "scripts_local\local_auto_update_cloud_v2.py"
if errorlevel 1 goto :FAIL

copy /Y "%SRC%merge_official_summary.py" "scripts\merge_official_summary.py"
if errorlevel 1 goto :FAIL

echo.
echo [4/7] Verify copied files...
if not exist ".github\workflows\vbgramg-cloud-auto-v2.yml" goto :FAIL
if not exist "scripts_local\local_auto_update_cloud_v2.py" goto :FAIL
if not exist "scripts\merge_official_summary.py" goto :FAIL
echo Copy verification OK.

echo.
echo [5/7] Commit only cloud updater files...
git add ".github\workflows\vbgramg-cloud-auto-v2.yml" "scripts_local\local_auto_update_cloud_v2.py" "scripts\merge_official_summary.py"

git diff --cached --quiet
if not errorlevel 1 (
  echo No new differences to commit.
) else (
  git commit -m "Install VBGRAMG Cloud Auto Update V2 Safe"
  if errorlevel 1 goto :FAIL
)

echo.
echo [6/7] Push to GitHub...
git push origin !BRANCH!
if errorlevel 1 (
  echo First push failed. Retrying after pull --rebase --autostash...
  git pull --rebase --autostash origin !BRANCH!
  if errorlevel 1 goto :FAIL
  git push origin !BRANCH!
  if errorlevel 1 goto :FAIL
)

echo.
echo [7/7] Verify workflow in HEAD...
git ls-tree -r HEAD --name-only | findstr /I /X ".github/workflows/vbgramg-cloud-auto-v2.yml" >nul
if errorlevel 1 (
  echo ERROR: Workflow not found in current HEAD.
  goto :FAIL
)

echo.
echo ============================================================
echo SUCCESS - CLOUD WORKFLOW PUSHED
echo ============================================================
echo Refresh GitHub Actions with Ctrl+F5.
echo Workflow name:
echo   VBGRAMG Cloud Auto Update V2 Safe
echo.
echo Then click Run workflow once for testing.
echo ============================================================
pause
exit /b 0

:FAIL
echo.
echo ============================================================
echo INSTALL FAILED
echo ============================================================
echo Git status:
git status --short
echo.
echo IMPORTANT:
echo Send a screenshot of THIS window showing the first ERROR line.
echo ============================================================
pause
exit /b 1
