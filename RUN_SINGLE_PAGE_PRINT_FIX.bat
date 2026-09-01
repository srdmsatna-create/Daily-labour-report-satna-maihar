@echo off
setlocal EnableExtensions
title VBGRAMG SINGLE PAGE PRINT / PDF FIX

set "REPO=C:\Users\welcome\Daily-labour-report-satna-maihar"
set "PATCH=%~dp0patch_single_page_print.py"

echo ============================================================
echo VB-G RAM G - SINGLE PAGE PRINT / PDF FIX
echo ============================================================
echo Official / Engineer report will NOT split into Part A + Part B.
echo Full report stays on ONE print page.
echo Portrait and Landscape both remain selectable.
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
echo [2/5] Verify...
findstr /C:"SRDM_SINGLE_PAGE_PRINT_NO_SPLIT_01_09_2026" "index.html" >nul
if errorlevel 1 (
  echo ERROR: Single page print patch marker missing.
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
  git commit -m "Keep Official and Engineer print on single page"
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
echo SUCCESS - SINGLE PAGE PRINT FIX PUSHED
echo ============================================================
echo Official / Engineer: ONE page only
echo Portrait: available
echo Landscape: available
echo No Part A / Part B split
echo.
echo Wait 1-3 minutes then Ctrl+F5 on srdmsatna.online
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
