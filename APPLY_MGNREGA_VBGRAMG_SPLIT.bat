@echo off
setlocal EnableExtensions
set "REPO=C:\Users\welcome\Daily-labour-report-satna-maihar"
cd /d "%REPO%"
title SRDM SATNA - MGNREGA + VBGRAMG FINANCIAL SPLIT

echo ============================================================
echo SRDM SATNA - MGNREGA / VB-G RAM G FINANCIAL SPLIT
echo Verified base: R6.12 13-09-2026 ^| 15,687 ongoing works
echo Counts/categories will NOT be changed.
echo ============================================================
echo.

git pull --rebase --autostash origin main
if errorlevel 1 goto :err

set PY=python
where py >nul 2>nul && set PY=py
%PY% "%~dp0APPLY_MGNREGA_VBGRAMG_SPLIT.py" "%REPO%"
if errorlevel 1 goto :err

git add ongoing-details.js index.html
git diff --cached --quiet
if not errorlevel 1 (
  echo No new changes to commit.
  goto :push
)

git commit -m "Split MGNREGA and VBGRAMG booked expenditure on verified R6.12"
if errorlevel 1 goto :err

:push
git push origin main
if errorlevel 1 goto :err

echo.
echo ============================================================
echo SUCCESS: MGNREGA / VBGRAMG FINANCIAL SPLIT PUBLISHED
echo Expected unchanged counts:
echo   Ongoing Works = 15687
echo   PMAY-G incl IAY = 10807
echo   IAY separate = 0
echo   Ek Bagiya ongoing = 755 ^| verified total = 756
echo.
echo Wait 1-3 minutes, then press Ctrl+F5 on srdmsatna.online
echo ============================================================
echo.
pause
exit /b 0

:err
echo.
echo ERROR: Financial split stopped safely.
echo Send a screenshot of this window.
echo.
pause
exit /b 1
