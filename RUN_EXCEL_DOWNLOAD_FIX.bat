@echo off
setlocal EnableExtensions
title VBGRAMG EXCEL DOWNLOAD FIX FINAL

set "REPO=C:\Users\welcome\Daily-labour-report-satna-maihar"
set "PATCH=%~dp0APPLY_EXCEL_DOWNLOAD_FIX.py"

echo ============================================================
echo VB-G RAM G - EXCEL DOWNLOAD FIX
echo ============================================================
echo Fixes Excel Download button only.
echo Report data is NOT changed.
echo ============================================================
echo.

if not exist "%REPO%\.git" (
  echo ERROR: Repo not found.
  pause
  exit /b 1
)

cd /d "%REPO%"

set "PY="
where py >nul 2>nul
if not errorlevel 1 set "PY=py"
if not defined PY (
  where python >nul 2>nul
  if not errorlevel 1 set "PY=python"
)
if not defined PY (
  echo ERROR: Python not found.
  pause
  exit /b 2
)

echo [1/5] Apply Excel Download fix...
%PY% "%PATCH%"
if errorlevel 1 goto :FAIL

echo.
echo [2/5] Verify...
findstr /C:"srdm-excel-download-final.js?v=20260901excel2" "index.html" >nul
if errorlevel 1 goto :FAIL
findstr /C:"SRDM_EXCEL_DOWNLOAD_FINAL_01_09_2026" "srdm-excel-download-final.js" >nul
if errorlevel 1 goto :FAIL
echo Verification OK.

echo.
echo [3/5] Commit only Excel files...
git add -f "index.html" "srdm-excel-download-final.js"
git diff --cached --quiet
if not errorlevel 1 (
  echo No new commit required.
) else (
  git commit -m "Fix Excel Download button for current report"
  if errorlevel 1 goto :FAIL
)

echo.
echo [4/5] Sync...
git pull --rebase --autostash
if errorlevel 1 goto :FAIL

echo.
echo [5/5] Push...
git push
if errorlevel 1 goto :FAIL

echo.
echo ============================================================
echo SUCCESS - EXCEL DOWNLOAD FIX PUSHED
echo ============================================================
echo Wait 1-3 minutes and press Ctrl+F5.
echo Then click Excel Download.
echo Current visible report will download as .xls.
echo ============================================================
pause
exit /b 0

:FAIL
echo.
echo ============================================================
echo FAILED - FIRST ERROR IS ABOVE
echo ============================================================
git status --short
pause
exit /b 1
