@echo off
setlocal EnableExtensions
title VBGRAMG FINAL READABLE FONT + WRAP + PRINT

set "REPO=C:\Users\welcome\Daily-labour-report-satna-maihar"
set "SRC=%~dp0"

echo ============================================================
echo VB-G RAM G - FINAL READABLE TABLE / PRINT FIX
echo ============================================================
echo Bigger font
echo Narrower columns + wrapping
echo One full table
echo Portrait + Landscape both
echo No Part A / Part B
echo No raw JavaScript text
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

echo [1/6] Apply final clean print/font patch...
%PY% "%SRC%APPLY_FINAL_READABLE_PRINT.py"
if errorlevel 1 goto :FAIL

echo.
echo [2/6] Verify files...
if not exist "srdm-readable-print-final.css" goto :FAIL
if not exist "srdm-readable-print-final.js" goto :FAIL
findstr /C:"srdm-readable-print-final.css" "index.html" >nul
if errorlevel 1 goto :FAIL
findstr /C:"srdm-readable-print-final.js" "index.html" >nul
if errorlevel 1 goto :FAIL
echo Verification OK.

echo.
echo [3/6] Stage only final dashboard files...
git add -f "index.html" "srdm-readable-print-final.css" "srdm-readable-print-final.js"

echo.
echo [4/6] Commit...
git diff --cached --quiet
if not errorlevel 1 (
  echo No new commit required.
) else (
  git commit -m "Final readable report font wrap and print layout"
  if errorlevel 1 goto :FAIL
)

echo.
echo [5/6] Sync...
git pull --rebase --autostash
if errorlevel 1 goto :FAIL

echo.
echo [6/6] Push...
git push
if errorlevel 1 goto :FAIL

echo.
echo ============================================================
echo SUCCESS - FINAL READABLE PRINT FIX PUSHED
echo ============================================================
echo Screen font: larger
echo Column widths: compact + wrap
echo Landscape print: 9 px readable
echo Portrait print: 7.4 px fit
echo Official / Engineer: ONE full table
echo Portrait + Landscape: BOTH available
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
