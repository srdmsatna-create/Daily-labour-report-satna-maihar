@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title SRDM SATNA - EMERGENCY RESTORE REPORTS

echo =====================================================
echo SRDM SATNA - EMERGENCY RESTORE REPORTS TO STABLE INDEX
echo =====================================================
echo.
echo This restores ONLY index.html to the last pre-style-patch version.
echo Current data files such as auto-data.js, official-summary.csv,
echo ongoing-details.js and other report data are NOT rolled back.
echo.

git pull --rebase --autostash origin main
if errorlevel 1 goto :err

if exist index.html copy /Y index.html index.before_emergency_restore_14-09-2026.bak.html >nul

git checkout fb855842c924ddd728300e199f25bc9479d30732 -- index.html
if errorlevel 1 goto :err

git add index.html
git diff --cached --quiet
if not errorlevel 1 (
  echo No index change detected.
  goto :done
)

git commit -m "Emergency restore dashboard reports to pre-freeze index"
if errorlevel 1 goto :err

git push origin main
if errorlevel 1 goto :err

:done
echo.
echo SUCCESS: Stable report index restored and published.
echo Data files were kept current.
echo Wait 1-3 minutes, then close old dashboard tab completely,
echo reopen https://srdmsatna.online and press Ctrl+F5 once.
echo Do NOT run any layout/icon patch yet.
echo.
pause
exit /b 0

:err
echo.
echo ERROR: Emergency restore did not complete.
echo Send a screenshot of this window.
echo.
pause
exit /b 1
