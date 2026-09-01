@echo off
setlocal EnableExtensions EnableDelayedExpansion
title VBGRAMG CLOUD V4 FORCE INSTALL

set "REPO=C:\Users\welcome\Daily-labour-report-satna-maihar"
set "SRC=%~dp0"

echo ============================================================
echo VB-G RAM G - CLOUD V4 FORCE INSTALL
echo This will install the missing workflow on GitHub main branch.
echo ============================================================
echo.

if not exist "%REPO%\.git" (
  echo ERROR: Git repo not found:
  echo %REPO%
  pause
  exit /b 1
)

cd /d "%REPO%"

where git >nul 2>nul
if errorlevel 1 (
  echo ERROR: Git not found.
  pause
  exit /b 1
)

echo [1/8] Current branch...
for /f "delims=" %%B in ('git branch --show-current') do set "BRANCH=%%B"
if not defined BRANCH set "BRANCH=main"
echo Branch: !BRANCH!

echo.
echo [2/8] Pull latest safely with AUTOSTASH...
git pull --rebase --autostash origin !BRANCH!
if errorlevel 1 (
  echo.
  echo Pull with autostash failed. Trying fetch + rebase...
  git fetch origin
  if errorlevel 1 goto :FAIL
  git rebase --autostash origin/!BRANCH!
  if errorlevel 1 goto :FAIL
)

echo.
echo [3/8] Copy cloud workflow + updater files...
if not exist ".github\workflows" mkdir ".github\workflows"
if not exist "scripts_local" mkdir "scripts_local"
if not exist "scripts" mkdir "scripts"

copy /Y "%SRC%.github\workflows\vbgramg-cloud-auto-v2.yml" ".github\workflows\vbgramg-cloud-auto-v2.yml" >nul
if errorlevel 1 goto :FAIL

copy /Y "%SRC%scripts_local\local_auto_update_cloud_v2.py" "scripts_local\local_auto_update_cloud_v2.py" >nul
if errorlevel 1 goto :FAIL

copy /Y "%SRC%scripts\merge_official_summary.py" "scripts\merge_official_summary.py" >nul
if errorlevel 1 goto :FAIL

echo.
echo [4/8] Verify files exist locally...
if not exist ".github\workflows\vbgramg-cloud-auto-v2.yml" goto :FAIL
if not exist "scripts_local\local_auto_update_cloud_v2.py" goto :FAIL
if not exist "scripts\merge_official_summary.py" goto :FAIL
echo Local files: OK

echo.
echo [5/8] Commit ONLY installer files...
git add ".github\workflows\vbgramg-cloud-auto-v2.yml" "scripts_local\local_auto_update_cloud_v2.py" "scripts\merge_official_summary.py"

git diff --cached --quiet
if not errorlevel 1 (
  echo Files already committed locally.
) else (
  git commit -m "Install VBGRAMG Cloud Auto Update V2 Safe"
  if errorlevel 1 goto :FAIL
)

echo.
echo [6/8] Push to GitHub...
git push origin !BRANCH!
if errorlevel 1 (
  echo Push rejected. Pulling once more with autostash and retrying...
  git pull --rebase --autostash origin !BRANCH!
  if errorlevel 1 goto :FAIL
  git push origin !BRANCH!
  if errorlevel 1 goto :FAIL
)

echo.
echo [7/8] Verify workflow is in current Git commit...
git ls-tree -r HEAD --name-only | findstr /I /X ".github/workflows/vbgramg-cloud-auto-v2.yml" >nul
if errorlevel 1 (
  echo ERROR: Workflow is not in HEAD after push.
  goto :FAIL
)
echo Workflow in HEAD: OK

echo.
echo [8/8] Show latest commit...
git log -1 --oneline

echo.
echo ============================================================
echo SUCCESS - WORKFLOW PUSHED TO GITHUB
echo ============================================================
echo Now refresh GitHub Actions page with Ctrl+F5.
echo You should see:
echo   VBGRAMG Cloud Auto Update V2 Safe
echo.
echo If it does not appear immediately, wait 30-60 seconds and refresh.
echo ============================================================
pause
exit /b 0

:FAIL
echo.
echo ============================================================
echo INSTALL FAILED
echo No dashboard data was deleted.
echo ============================================================
echo.
git status --short
echo.
pause
exit /b 1
