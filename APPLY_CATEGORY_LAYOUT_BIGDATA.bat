@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title SRDM SATNA - CATEGORY WIDTH + BIG DATA FONT

echo =====================================================
echo SRDM SATNA - CATEGORY TABLE WIDTH + BIG DATA FONT
 echo Work Category wider
 echo Numeric columns compact
 echo Numeric/body font larger
 echo Data/counts/financial logic will NOT change
 echo =====================================================
echo.

git pull --rebase --autostash origin main
if errorlevel 1 goto :err

set PY=python
where py >nul 2>nul && set PY=py
%PY% APPLY_CATEGORY_LAYOUT_BIGDATA.py
if errorlevel 1 goto :err

git add index.html APPLY_CATEGORY_LAYOUT_BIGDATA.py APPLY_CATEGORY_LAYOUT_BIGDATA.bat
git diff --cached --quiet
if not errorlevel 1 (
  echo No new layout changes detected.
  goto :pushonly
)

git commit -m "Widen category column and enlarge numeric data font"
if errorlevel 1 goto :err

:pushonly
git push origin main
if errorlevel 1 goto :err

echo.
echo SUCCESS: CATEGORY WIDTH AND BIG DATA FONT PUBLISHED
 echo Work Category wider
 echo Other columns compact
 echo Body numeric font larger
 echo Data/counts/financial split: UNCHANGED
 echo.
echo Wait 1-3 minutes, then press Ctrl+F5 on srdmsatna.online.
echo.
pause
exit /b 0

:err
echo.
echo ERROR: Layout patch stopped safely.
echo No data logic was changed.
echo.
pause
exit /b 1
