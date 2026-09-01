@echo off
setlocal EnableExtensions EnableDelayedExpansion
title VBGRAMG CLOUD V6 ROBUST INSTALL

set "REPO=C:\Users\welcome\Daily-labour-report-satna-maihar"
set "SRC=%~dp0"
set "LOG=%TEMP%\vbgramg_v6_install.log"

> "%LOG%" echo VBGRAMG V6 INSTALL LOG
>>"%LOG%" echo Started: %DATE% %TIME%

echo ============================================================
echo VB-G RAM G - CLOUD V6 ROBUST INSTALL
echo ============================================================
echo.

if not exist "%REPO%\.git" goto :ERR_REPO
if not exist "%SRC%VBGRAMG_WORKFLOW_V2_SAFE.yml" goto :ERR_SRC1
if not exist "%SRC%local_auto_update_cloud_v2.py" goto :ERR_SRC2
if not exist "%SRC%merge_official_summary.py" goto :ERR_SRC3

cd /d "%REPO%"
where git >nul 2>nul
if errorlevel 1 goto :ERR_GIT

for /f "delims=" %%B in ('git branch --show-current') do set "BRANCH=%%B"
if not defined BRANCH set "BRANCH=main"

echo [1/7] Creating destination folders...
powershell -NoProfile -Command ^
  "New-Item -ItemType Directory -Force -Path '.github\workflows','scripts_local','scripts' | Out-Null"
if errorlevel 1 goto :ERR_MKDIR

echo [2/7] Copying workflow and scripts...
powershell -NoProfile -Command ^
  "Copy-Item -LiteralPath '%SRC%VBGRAMG_WORKFLOW_V2_SAFE.yml' -Destination '.github\workflows\vbgramg-cloud-auto-v2.yml' -Force; ^
   Copy-Item -LiteralPath '%SRC%local_auto_update_cloud_v2.py' -Destination 'scripts_local\local_auto_update_cloud_v2.py' -Force; ^
   Copy-Item -LiteralPath '%SRC%merge_official_summary.py' -Destination 'scripts\merge_official_summary.py' -Force"
if errorlevel 1 goto :ERR_COPY

if not exist ".github\workflows\vbgramg-cloud-auto-v2.yml" goto :ERR_VERIFY1
if not exist "scripts_local\local_auto_update_cloud_v2.py" goto :ERR_VERIFY2
if not exist "scripts\merge_official_summary.py" goto :ERR_VERIFY3
echo Copy verification: OK

echo [3/7] Adding ONLY required files...
git add -f ".github/workflows/vbgramg-cloud-auto-v2.yml" "scripts_local/local_auto_update_cloud_v2.py" "scripts/merge_official_summary.py"
if errorlevel 1 goto :ERR_ADD

echo [4/7] Commit...
git diff --cached --quiet
if not errorlevel 1 (
  echo Required files already match current commit.
) else (
  git commit -m "Install VBGRAMG Cloud Auto Update V2 Safe"
  if errorlevel 1 goto :ERR_COMMIT
)

echo [5/7] Fetch remote status...
git fetch origin !BRANCH!
if errorlevel 1 goto :ERR_FETCH

for /f %%N in ('git rev-list --count HEAD..origin/!BRANCH!') do set "BEHIND=%%N"
if not defined BEHIND set "BEHIND=0"
echo Remote commits ahead: !BEHIND!

if not "!BEHIND!"=="0" (
  echo Remote is ahead. Rebasing with autostash...
  git rebase --autostash origin/!BRANCH!
  if errorlevel 1 goto :ERR_REBASE
)

echo [6/7] Push workflow...
git push origin !BRANCH!
if errorlevel 1 goto :ERR_PUSH

echo [7/7] Verify in local HEAD...
git ls-tree -r HEAD --name-only | findstr /I /X ".github/workflows/vbgramg-cloud-auto-v2.yml" >nul
if errorlevel 1 goto :ERR_HEAD

echo.
echo ============================================================
echo SUCCESS - WORKFLOW PUSHED TO GITHUB
echo ============================================================
echo Refresh GitHub Actions with Ctrl+F5.
echo Workflow:
echo   VBGRAMG Cloud Auto Update V2 Safe
echo.
echo If it takes time, wait 30-60 seconds and refresh.
echo ============================================================
pause
exit /b 0

:ERR_REPO
set "ERR=Repository not found: %REPO%"
goto :FAIL
:ERR_SRC1
set "ERR=Source workflow file missing beside installer."
goto :FAIL
:ERR_SRC2
set "ERR=Source updater Python file missing beside installer."
goto :FAIL
:ERR_SRC3
set "ERR=Source merge Python file missing beside installer."
goto :FAIL
:ERR_GIT
set "ERR=Git command not found."
goto :FAIL
:ERR_MKDIR
set "ERR=Could not create destination folders."
goto :FAIL
:ERR_COPY
set "ERR=PowerShell Copy-Item failed."
goto :FAIL
:ERR_VERIFY1
set "ERR=Workflow destination file was not created."
goto :FAIL
:ERR_VERIFY2
set "ERR=Updater destination file was not created."
goto :FAIL
:ERR_VERIFY3
set "ERR=Merge destination file was not created."
goto :FAIL
:ERR_ADD
set "ERR=git add failed."
goto :FAIL
:ERR_COMMIT
set "ERR=git commit failed."
goto :FAIL
:ERR_FETCH
set "ERR=git fetch failed."
goto :FAIL
:ERR_REBASE
set "ERR=git rebase failed."
goto :FAIL
:ERR_PUSH
set "ERR=git push failed. This may be a GitHub credential/workflow permission issue."
goto :FAIL
:ERR_HEAD
set "ERR=Workflow missing from HEAD after push."
goto :FAIL

:FAIL
echo.
echo ============================================================
echo INSTALL FAILED
echo ERROR: !ERR!
echo ============================================================
>>"%LOG%" echo ERROR: !ERR!
git status --short
echo.
echo Log file:
echo %LOG%
echo ============================================================
pause
exit /b 1
