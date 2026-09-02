@echo off
setlocal EnableExtensions
title SRDM SATNA - Publish Reports to GitHub V6
color 0A

set "REPO=C:\Users\welcome\Daily-labour-report-satna-maihar\Daily-labour-report-satna-maihar"
if not exist "%REPO%\index.html" goto :nofolder
cd /d "%REPO%"

echo Dashboard folder: %CD%
echo Staging Yuktdhara and Muster e-MB report files...

call :stage index.html
call :stage yuktdhara-data.js
call :stage muster-emb-data.js
call :stage scripts_local\update_yuktdhara_monitoring.py
call :stage scripts_local\update_muster_emb_monitoring.py
call :stage ONE_CLICK_DASHBOARD_DATA_UPDATE.bat

git diff --cached --quiet
if not errorlevel 1 goto :nostaged

git commit -m "Publish Yuktdhara and Muster e-MB reports"
if errorlevel 1 goto :commitfail

git pull --rebase --autostash
if errorlevel 1 goto :pullfail

git push origin main
if errorlevel 1 goto :pushfail

color 0A
echo.
echo ============================================================
echo SUCCESS - Reports committed and pushed to GitHub main branch.
echo Wait 1-3 minutes, then press Ctrl+Shift+R on the website.
echo ============================================================
pause
exit /b 0

:stage
if exist "%~1" (
  git add -f -- "%~1"
  if errorlevel 1 goto :stagefail
  echo Added: %~1
) else (
  echo Optional file not found, skipped: %~1
)
exit /b 0

:stagefail
color 0C
echo ERROR: Could not stage %~1
pause
exit /b 10

:nofolder
color 0C
echo ERROR: Dashboard folder not found:
echo %REPO%
pause
exit /b 1

:nostaged
color 0E
echo Nothing new to publish. GitHub may already contain these report files.
git status --short
pause
exit /b 2

:commitfail
color 0C
echo ERROR: Git commit failed.
pause
exit /b 3

:pullfail
color 0C
echo ERROR: Git pull/rebase failed. Push was not attempted.
pause
exit /b 4

:pushfail
color 0C
echo ERROR: GitHub push failed.
pause
exit /b 5
