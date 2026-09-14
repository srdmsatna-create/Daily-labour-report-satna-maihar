@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title SRDM SATNA - CATEGORY REPORT FONT BIG

echo =====================================================
echo SRDM SATNA - CATEGORY FINANCIAL REPORT FONT BIG
 echo Only font size/readability will change.
 echo Counts, categories and financial data will NOT change.
echo =====================================================
echo.

git pull --rebase --autostash origin main
if errorlevel 1 goto :err

set PY=python
where py >nul 2>nul && set PY=py
%PY% APPLY_CATEGORY_FONT_BIG.py
if errorlevel 1 goto :err

git add index.html APPLY_CATEGORY_FONT_BIG.py APPLY_CATEGORY_FONT_BIG.bat
git diff --cached --quiet
if not errorlevel 1 (
  echo No new font changes detected.
  goto :pushonly
)

git commit -m "Increase category financial report font size"
if errorlevel 1 goto :err

:pushonly
git push origin main
if errorlevel 1 goto :err

echo.
echo SUCCESS: CATEGORY REPORT FONT ENLARGED AND PUBLISHED
 echo Data/counts/financial split: UNCHANGED
 echo Wait 1-3 minutes, then press Ctrl+F5 on srdmsatna.online.
echo.
pause
exit /b 0

:err
echo.
echo ERROR: Font patch stopped safely.
echo No data logic was changed by this patch.
echo.
pause
exit /b 1
