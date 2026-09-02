@echo off
setlocal EnableExtensions
title SRDM SATNA - Restore Root and Publish Reports V7
color 0A

set "REPO=C:\Users\welcome\Daily-labour-report-satna-maihar"
if not exist "%REPO%\.git" goto :nofolder
cd /d "%REPO%"

echo Correct GitHub Pages root: %CD%
echo Restoring the tracked root index.html...
git restore --source=HEAD -- index.html
if errorlevel 1 goto :restorefail
if not exist "index.html" goto :restorefail

where py >nul 2>&1 && set "PY=py"
if not defined PY set "PY=python"

echo Installing Yuktdhara in the GitHub Pages root...
%PY% "%~dp0APPLY_YUKTDHARA_MODULE.py" --repo "%REPO%"
if errorlevel 1 goto :installfail

echo Installing Muster Roll and e-MB in the GitHub Pages root...
%PY% "%~dp0APPLY_MUSTER_EMB_MODULE.py" --repo "%REPO%"
if errorlevel 1 goto :installfail

call :stage index.html
call :stage yuktdhara-data.js
call :stage muster-emb-data.js
call :stage scripts_local\update_yuktdhara_monitoring.py
call :stage scripts_local\update_muster_emb_monitoring.py
call :stage ONE_CLICK_DASHBOARD_DATA_UPDATE.bat

git diff --cached --quiet
if not errorlevel 1 goto :nostaged

git commit -m "Publish Yuktdhara and Muster e-MB reports at site root"
if errorlevel 1 goto :commitfail
git pull --rebase --autostash
if errorlevel 1 goto :pullfail
git push origin main
if errorlevel 1 goto :pushfail

color 0A
echo.
echo ============================================================
echo SUCCESS - Root dashboard reports pushed to GitHub main.
echo Wait 1-3 minutes and press Ctrl+Shift+R on srdmsatna.online.
echo ============================================================
pause
exit /b 0

:stage
if exist "%~1" (
  git update-index --no-assume-unchanged --no-skip-worktree -- "%~1" >nul 2>&1
  git add -f -- "%~1"
  if errorlevel 1 goto :stagefail
  echo Added root file: %~1
)
exit /b 0

:stagefail
color 0C
echo ERROR: Could not stage root file %~1
pause
exit /b 10

:nofolder
color 0C
echo ERROR: Git repository not found: %REPO%
pause
exit /b 1
:restorefail
color 0C
echo ERROR: Could not restore the root index.html from Git.
pause
exit /b 2
:installfail
color 0C
echo ERROR: Report installation in root folder failed.
pause
exit /b 3
:nostaged
color 0C
echo ERROR: Root report files were not staged. SUCCESS not issued.
git status --short
pause
exit /b 4
:commitfail
color 0C
echo ERROR: Git commit failed.
pause
exit /b 5
:pullfail
color 0C
echo ERROR: Git pull/rebase failed.
pause
exit /b 6
:pushfail
color 0C
echo ERROR: GitHub push failed.
pause
exit /b 7
