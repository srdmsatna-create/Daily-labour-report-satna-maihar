@echo off
setlocal EnableExtensions
title VBGRAMG REMOVE RAW CODE + CLEAN PRINT FINAL

set "REPO=C:\Users\welcome\Daily-labour-report-satna-maihar"
set "PATCH=%~dp0REMOVE_RAW_CODE_AND_FIX_PRINT.py"

echo ============================================================
echo VB-G RAM G - REMOVE RAW CODE + CLEAN PRINT
echo ============================================================
echo Removes visible JavaScript / Part A / Part B text.
echo Keeps full report as ONE table.
echo Portrait + Landscape both remain.
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

echo [1/5] Remove broken/raw print code...
%PY% "%PATCH%"
if errorlevel 1 goto :FAIL

echo.
echo [2/5] Verify raw text is gone...
findstr /C:"function enrichHtml(mode)" "index.html" >nul
if not errorlevel 1 (
  echo ERROR: Raw code still present.
  goto :FAIL
)
findstr /C:"SRDM_CLEAN_SINGLE_TABLE_PRINT_FINAL_01_09_2026" "index.html" >nul
if errorlevel 1 (
  echo ERROR: Clean print marker missing.
  goto :FAIL
)
echo Verification OK.

echo.
echo [3/5] Commit index.html only...
git add -f "index.html"
git diff --cached --quiet
if not errorlevel 1 (
  echo No new commit needed.
) else (
  git commit -m "Remove broken print code and restore clean single-table print"
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
echo SUCCESS - RAW CODE REMOVED AND FIX PUSHED
echo ============================================================
echo Wait 1-3 minutes and press Ctrl+F5.
echo Full Official/Engineer report remains ONE table.
echo No Part A / Part B text.
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
