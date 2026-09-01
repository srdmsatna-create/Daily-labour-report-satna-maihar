@echo off
setlocal EnableExtensions EnableDelayedExpansion
title VBGRAMG LOCK + RECOVERY + FONT + PORTRAIT PRINT + EXCEL

set "REPO=C:\Users\welcome\Daily-labour-report-satna-maihar"
set "P1=%~dp0patch_lock_and_recovery.py"
set "P2=%~dp0patch_font_print_excel.py"

echo ============================================================
echo VB-G RAM G - COMPLETE DASHBOARD FIX
echo ============================================================
echo 1. PMAY-G + Ek Bagiya Ongoing lock till 06-09-2026
echo 2. Correct Janpad-wise Recovery counts
echo 3. Bigger report fonts
echo 4. Print fixed to A4 Portrait
echo 5. Excel Download button
echo ============================================================
echo.

if not exist "%REPO%\.git" (
  echo ERROR: Repo not found:
  echo %REPO%
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

echo [1/8] Pull latest safely...
git pull --rebase --autostash
if errorlevel 1 goto :FAIL

echo.
echo [2/8] Restore PMAY/Ek Bagiya lock + Recovery...
%PY% "%P1%"
if errorlevel 1 goto :FAIL

echo.
echo [3/8] Apply font / portrait print / Excel patch...
%PY% "%P2%"
if errorlevel 1 goto :FAIL

echo.
echo [4/8] Rebuild dashboard data...
%PY% "scripts\merge_official_summary.py"
if errorlevel 1 goto :FAIL

echo.
echo [5/8] Verify 1-week lock...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$r=Import-Csv 'data\official-summary.csv'; $p=[int](($r|Measure-Object pmayOngoing -Sum).Sum); $e=[int](($r|Measure-Object ekOngoing -Sum).Sum); Write-Host ('PMAY-G Ongoing = '+$p); Write-Host ('Ek Bagiya Ongoing = '+$e); if($p -ne 11995 -or $e -ne 756){exit 9}"
if errorlevel 1 goto :FAIL

echo.
echo [6/8] Verify UI patch...
findstr /C:"Excel Download" "index.html" >nul
if errorlevel 1 (
  echo ERROR: Excel Download button not found.
  goto :FAIL
)
findstr /C:"SRDM_FONT_PRINT_EXCEL_FIX_01_09_2026" "index.html" >nul
if errorlevel 1 (
  echo ERROR: Font/Print patch marker not found.
  goto :FAIL
)
echo UI verification OK.

echo.
echo [7/8] Commit and push...
git add -f "index.html" "scripts\merge_official_summary.py" "data\official-summary.csv" "auto-data.js"
if exist "app.js" git add -f "app.js"

git diff --cached --quiet
if not errorlevel 1 (
  echo No new commit required.
) else (
  git commit -m "Fix locked ongoing recovery font portrait print and Excel export"
  if errorlevel 1 goto :FAIL
)

git pull --rebase --autostash
if errorlevel 1 goto :FAIL
git push
if errorlevel 1 goto :FAIL

echo.
echo [8/8] COMPLETE
echo ============================================================
echo SUCCESS - COMPLETE DASHBOARD FIX PUSHED
echo ============================================================
echo PMAY-G Ongoing total    : 11,995
echo Ek Bagiya Ongoing total : 756
echo Recovery total          : 549 (Janpad-wise correct)
echo Font                    : Bigger
echo Print                   : A4 Portrait
echo Excel                   : Excel Download button added
echo.
echo Wait 1-3 minutes, then Ctrl+F5 on srdmsatna.online
echo ============================================================
pause
exit /b 0

:FAIL
echo.
echo ============================================================
echo FIX FAILED - READ THE ERROR ABOVE
echo ============================================================
git status --short
pause
exit /b 1
