@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title SRDM SATNA - FIX ALL HINDI ENCODING

echo =====================================================
echo SRDM SATNA - FIX ALL HINDI ENCODING
echo =====================================================
echo.

git pull --rebase --autostash origin main
if errorlevel 1 goto :err

set PY=python
where py >nul 2>nul && set PY=py
%PY% FIX_ALL_HINDI_ENCODING.py
if errorlevel 1 goto :err

git add index.html app.js srdm-readable-print-final.js srdm-readable-print-final.css FIX_ALL_HINDI_ENCODING.py FIX_ALL_HINDI_ENCODING.bat
git diff --cached --quiet
if not errorlevel 1 (
  echo No text changes detected. Continuing to push helper files only if needed...
)

git commit -m "Repair corrupted Hindi encoding across dashboard UI"
if errorlevel 1 (
  echo No new commit needed.
)

git push origin main
if errorlevel 1 goto :err

echo.
echo SUCCESS: ALL HINDI ENCODING REPAIRED AND PUBLISHED.
echo Wait 1-3 minutes, close all old dashboard tabs, then reopen srdmsatna.online and press Ctrl+F5.
echo.
pause
exit /b 0

:err
echo.
echo ERROR: Hindi encoding repair did not complete.
echo Send a screenshot of this window.
echo.
pause
exit /b 1
