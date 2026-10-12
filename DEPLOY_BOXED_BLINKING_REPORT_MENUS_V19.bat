@echo off
setlocal EnableExtensions
title SRDM SATNA - Boxed Blinking Report Menus V19
color 0A

set "SOURCE=%~dp0final"
set "REPO=C:\Users\welcome\Daily-labour-report-satna-maihar"

if not exist "%SOURCE%\index.html" goto :nosource
if not exist "%REPO%\.git" goto :nogit

echo Source     : %SOURCE%
echo Git root   : %REPO%
echo Applying boxed report menus with unique colours and blinking indicators...

copy /Y "%SOURCE%\index.html" "%REPO%\index.html" >nul || goto :copyfail
copy /Y "%SOURCE%\auto-data.js" "%REPO%\auto-data.js" >nul || goto :copyfail
copy /Y "%SOURCE%\auto-status.js" "%REPO%\auto-status.js" >nul || goto :copyfail
copy /Y "%SOURCE%\yuktdhara-data.js" "%REPO%\yuktdhara-data.js" >nul || goto :copyfail
copy /Y "%SOURCE%\yuktdhara-subengineer.js" "%REPO%\yuktdhara-subengineer.js" >nul || goto :copyfail
copy /Y "%SOURCE%\muster-emb-data.js" "%REPO%\muster-emb-data.js" >nul || goto :copyfail
if not exist "%REPO%\scripts_local" mkdir "%REPO%\scripts_local"
copy /Y "%SOURCE%\scripts_local\update_muster_emb_monitoring.py" "%REPO%\scripts_local\update_muster_emb_monitoring.py" >nul

cd /d "%REPO%"
git add -f -- index.html auto-data.js auto-status.js yuktdhara-data.js yuktdhara-subengineer.js muster-emb-data.js scripts_local/update_muster_emb_monitoring.py
git diff --cached --quiet
if not errorlevel 1 goto :same
git commit -m "Add boxed coloured report menus and blinking indicators V19"
if errorlevel 1 goto :commitfail
git pull --rebase --autostash
if errorlevel 1 goto :pullfail
git push origin main
if errorlevel 1 goto :pushfail
goto :success

:same
echo No staged difference. Pushing any pending commit...
git push origin main
if errorlevel 1 goto :pushfail
goto :success

:success
echo.
echo ============================================================
echo SUCCESS - Boxed Blinking Report Menus V19 pushed.
echo Wait 1-3 minutes and press Ctrl+Shift+R.
echo ============================================================
pause
exit /b 0

:nosource
color 0C
echo ERROR: final\index.html is missing from extracted V19 package.
pause
exit /b 1
:nogit
color 0C
echo ERROR: Git root not found at %REPO%
pause
exit /b 2
:copyfail
color 0C
echo ERROR: File copy failed.
pause
exit /b 3
:commitfail
color 0C
echo ERROR: Git commit failed. Run git status in %REPO%
pause
exit /b 4
:pullfail
color 0C
echo ERROR: Git pull/rebase failed. Run git status in %REPO%
pause
exit /b 5
:pushfail
color 0C
echo ERROR: Git push failed.
pause
exit /b 6
