@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title SRDM SATNA - CATEGORY NUMERIC BIG + OVERALL EXP COMPACT

echo =====================================================
echo SRDM SATNA - CATEGORY TABLE READABILITY
 echo Overall Exp %% column compact
 echo All numeric data larger
 echo Data/counts/financial logic will NOT change
 echo =====================================================
echo.

git pull --rebase --autostash origin main
if errorlevel 1 goto :err

set PY=python
where py >nul 2>nul && set PY=py
%PY% APPLY_CATEGORY_NUMERIC_BIG_COMPACT.py
if errorlevel 1 goto :err

git add index.html APPLY_CATEGORY_NUMERIC_BIG_COMPACT.py APPLY_CATEGORY_NUMERIC_BIG_COMPACT.bat
git diff --cached --quiet
if not errorlevel 1 (
  echo No new layout changes detected.
  goto :pushonly
)

git commit -m "Compact Overall Exp column and enlarge category numeric data"
if errorlevel 1 goto :err

:pushonly
git push origin main
if errorlevel 1 goto :err

echo.
echo SUCCESS: NUMERIC FONT ENLARGED AND OVERALL EXP COMPACT PUBLISHED
 echo Data/counts/financial split: UNCHANGED
 echo Wait 1-3 minutes, then press Ctrl+F5 on srdmsatna.online.
echo.
pause
exit /b 0

:err
echo.
echo ERROR: Layout patch stopped safely.
echo Data logic was not changed.
echo.
pause
exit /b 1
