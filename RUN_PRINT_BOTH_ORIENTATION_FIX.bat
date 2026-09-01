@echo off
setlocal EnableExtensions
title VBGRAMG PRINT BOTH ORIENTATION + PDF FIT FIX

set "REPO=C:\Users\welcome\Daily-labour-report-satna-maihar"
set "PATCH=%~dp0patch_print_both_orientation.py"

echo ============================================================
echo VB-G RAM G - PRINT / PDF FIX
echo ============================================================
echo Portrait  : available
echo Landscape : available
echo Official Portrait: Part A + Part B readable pages
echo Official Landscape: full current table
echo Other reports: selected orientation, auto fit
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

echo [1/5] Patch current index.html...
%PY% "%PATCH%"
if errorlevel 1 goto :FAIL

echo.
echo [2/5] Verify patch...
findstr /C:"SRDM_PRINT_BOTH_ORIENTATION_PDF_FIT_01_09_2026" "index.html" >nul
if errorlevel 1 (
  echo ERROR: Print patch marker not found.
  goto :FAIL
)
echo Verification OK.

echo.
echo [3/5] Commit only index.html...
git add -f "index.html"
git diff --cached --quiet
if not errorlevel 1 (
  echo No new commit needed.
) else (
  git commit -m "Fix portrait landscape print and PDF fit"
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
echo SUCCESS - PRINT / PDF FIX PUSHED
echo ============================================================
echo Both options remain: Portrait + Landscape
echo Portrait Official/Engineer = Part A + Part B
echo Landscape Official/Engineer = full wide table
echo Other screens = selected orientation + auto fit
echo.
echo Wait 1-3 minutes and Ctrl+F5 on srdmsatna.online
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
