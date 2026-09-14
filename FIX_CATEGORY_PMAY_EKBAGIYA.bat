@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title SRDM SATNA - FIX PMAY AND EK BAGIYA CATEGORY

echo =====================================================
echo SRDM SATNA - CATEGORY FIX
 echo IAY + PMAY-G = PMAY-G
 echo Gap Filling FY 2025-26 / 2026-27 = Ek Bagiya
 echo Ek Bagiya must validate exactly 756 unique works
 echo =====================================================
echo.

git pull --rebase --autostash origin main
if errorlevel 1 goto :err

set PY=python
where py >nul 2>nul && set PY=py
%PY% FIX_CATEGORY_PMAY_EKBAGIYA.py
if errorlevel 1 goto :err

git add ongoing-details.js FIX_CATEGORY_PMAY_EKBAGIYA.py FIX_CATEGORY_PMAY_EKBAGIYA.bat
git diff --cached --quiet
if not errorlevel 1 (
  echo No new category changes detected.
  goto :pushonly
)

git commit -m "Merge IAY into PMAY-G and normalize Ek Bagiya 756"
if errorlevel 1 goto :err

:pushonly
git push origin main
if errorlevel 1 goto :err

echo.
echo SUCCESS: CATEGORY FIX PUBLISHED
 echo PMAY-G now includes IAY Houses.
 echo Ek Bagiya validated at 756 unique works.
echo.
echo Wait 1-3 minutes, then press Ctrl+F5 on srdmsatna.online.
echo.
pause
exit /b 0

:err
echo.
echo ERROR: Category fix stopped safely.
echo IMPORTANT: If Ek Bagiya is not exactly 756, ongoing-details.js is NOT changed.
echo Send this screen if an error is shown.
echo.
pause
exit /b 1
