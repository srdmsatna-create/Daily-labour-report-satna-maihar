@echo off
setlocal EnableExtensions
title VBGRAMG EMERGENCY CLEAN INDEX RESTORE

set "REPO=C:\Users\welcome\Daily-labour-report-satna-maihar"
set "PATCH=%~dp0EMERGENCY_RESTORE_CLEAN_INDEX.py"

echo ============================================================
echo VB-G RAM G - EMERGENCY CLEAN INDEX RESTORE
echo ============================================================
echo Removes ALL broken visible JavaScript / Part A / Part B code
echo by restoring a clean index backup.
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

echo [1/5] Restore clean index...
%PY% "%PATCH%"
if errorlevel 1 goto :FAIL

echo.
echo [2/5] Verify clean HTML...
findstr /C:"function enrichHtml(mode)" "index.html" >nul
if not errorlevel 1 (
  echo ERROR: raw function still exists.
  goto :FAIL
)
findstr /C:"Part A — GP / Screen-2 / Individual Land" "index.html" >nul
if not errorlevel 1 (
  echo ERROR: Part A text still exists.
  goto :FAIL
)
echo CLEAN verification passed.

echo.
echo [3/5] Commit clean index only...
git add -f "index.html"
git diff --cached --quiet
if not errorlevel 1 (
  echo No new commit needed.
) else (
  git commit -m "Emergency restore clean dashboard index"
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
echo SUCCESS - CLEAN INDEX RESTORED AND PUSHED
echo ============================================================
echo Raw JavaScript removed.
echo Part A / Part B removed.
echo Original Print/PDF restored.
echo Excel Download retained.
echo.
echo Wait 1-3 minutes and press Ctrl+F5.
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
