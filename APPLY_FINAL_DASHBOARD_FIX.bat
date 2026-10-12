@echo off
setlocal EnableExtensions EnableDelayedExpansion
title VBGRAMG FINAL FORMAT + PRINT + EXCEL + LOCK FIX

set "REPO=C:\Users\welcome\Daily-labour-report-satna-maihar"
set "P1=%~dp0patch_lock_and_recovery.py"
set "P2=%~dp0patch_ui_print_excel.py"

echo ============================================================
echo VB-G RAM G - FINAL DASHBOARD FIX
echo ============================================================
echo 1. PMAY/Ek Bagiya lock restore
echo 2. Janpad Recovery fix
echo 3. Bigger font
echo 4. Portrait Print/PDF default
echo 5. Excel Download (.xlsx)
echo ============================================================

if not exist "%REPO%\.git" (
  echo ERROR: Repo not found.
  pause
  exit /b 1
)

cd /d "%REPO%"

set "PY="
where py >nul 2>nul
if not errorlevel 1 set "PY=py"
if not defined PY set "PY=python"

echo [1/8] Pull latest...
git pull --rebase --autostash
if errorlevel 1 goto FAIL

echo [2/8] Lock + Recovery fix...
%PY% "%P1%"
if errorlevel 1 goto FAIL

echo [3/8] Font + Print + Excel fix...
%PY% "%P2%"
if errorlevel 1 goto FAIL

echo [4/8] Rebuild auto-data...
%PY% "scripts\merge_official_summary.py"
if errorlevel 1 goto FAIL

echo [5/8] Verify lock totals...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$r=Import-Csv 'data\official-summary.csv';$p=[int](($r|Measure-Object pmayOngoing -Sum).Sum);$e=[int](($r|Measure-Object ekOngoing -Sum).Sum);Write-Host ('PMAY-G Ongoing='+$p);Write-Host ('Ek Bagiya Ongoing='+$e);if((Get-Date).Date -le [datetime]'2026-09-06' -and ($p -ne 11995 -or $e -ne 756)){exit 9}"
if errorlevel 1 goto FAIL

echo [6/8] Verify UI...
findstr /C:"id=\"excelBtn\"" "index.html" >nul
if errorlevel 1 goto FAIL
findstr /C:"SRDM UI PRINT EXCEL FIX 01-09-2026" "index.html" >nul
if errorlevel 1 goto FAIL

echo [7/8] Commit...
git add -f index.html scripts\merge_official_summary.py data\official-summary.csv auto-data.js
if exist app.js git add -f app.js
git diff --cached --quiet
if errorlevel 1 (
  git commit -m "Improve dashboard font portrait print Excel export and restore locks"
  if errorlevel 1 goto FAIL
) else (
  echo No new commit needed.
)

echo [8/8] Push...
git pull --rebase --autostash
if errorlevel 1 goto FAIL
git push
if errorlevel 1 goto FAIL

echo.
echo ============================================================
echo SUCCESS - DASHBOARD FIX PUSHED
echo ============================================================
echo Larger font: YES
echo Portrait Print/PDF default: YES
echo Excel Download .xlsx: YES
echo PMAY/Ek Bagiya lock till 06-09-2026: YES
echo Janpad Recovery fix: YES
echo ============================================================
pause
exit /b 0

:FAIL
echo.
echo ============================================================
echo FAILED - SEE ERROR ABOVE
echo ============================================================
git status --short
pause
exit /b 1
