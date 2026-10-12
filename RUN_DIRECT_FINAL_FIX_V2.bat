@echo off
setlocal EnableExtensions EnableDelayedExpansion
title VBGRAMG DIRECT FINAL FIX V2

set "REPO=C:\Users\welcome\Daily-labour-report-satna-maihar"
set "SRC=%~dp0"

echo ============================================================
echo VB-G RAM G - DIRECT FINAL FIX V2
echo ============================================================
echo PMAY/Ek Bagiya lock + Recovery + Bigger Font + Portrait + Excel
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

echo [1/7] Patch CURRENT index.html...
%PY% "%SRC%patch_current_index_FINAL_V2.py"
if errorlevel 1 goto :FAIL

echo.
echo [2/7] Install locked merge script...
copy /Y "%SRC%merge_official_summary_LOCKED.py" "%REPO%\scripts\merge_official_summary.py" >nul
if errorlevel 1 goto :FAIL

echo.
echo [3/7] Rebuild auto-data.js...
%PY% "%REPO%\scripts\merge_official_summary.py"
if errorlevel 1 goto :FAIL

echo.
echo [4/7] Verify exact result...
%PY% "%SRC%verify_FINAL_V2.py"
if errorlevel 1 goto :FAIL

echo.
echo [5/7] Commit ONLY target dashboard files...
git add -f "index.html" "scripts/merge_official_summary.py" "auto-data.js"
git diff --cached --quiet
if not errorlevel 1 (
  echo No new commit needed.
) else (
  git commit -m "Direct fix PMAY Ek Bagiya Recovery font portrait Excel"
  if errorlevel 1 goto :FAIL
)

echo.
echo [6/7] Sync remote after fix...
git pull --rebase --autostash
if errorlevel 1 goto :FAIL

echo.
echo [7/7] Push...
git push
if errorlevel 1 goto :FAIL

echo.
echo ============================================================
echo SUCCESS - FINAL FIX PUSHED
echo ============================================================
echo PMAY-G Ongoing : 11,995
echo Ek Bagiya      : 756
echo Recovery       : Janpad-wise correct, Total 549
echo Font           : Bigger
echo Print          : A4 Portrait, Official split Part A + Part B
echo Excel          : Excel Download added
echo.
echo Wait 1-3 minutes, then Ctrl+F5 on srdmsatna.online
echo ============================================================
pause
exit /b 0

:FAIL
echo.
echo ============================================================
echo FAILED - FIRST ERROR IS ABOVE
echo ============================================================
echo The many lines starting with ?? are only old untracked installer files.
echo They are NOT pushed by this installer.
echo.
git status --short
pause
exit /b 1
