@echo off
setlocal
cd /d "%~dp0"
echo ===============================================
echo SRDM SATNA - VASULI COUNT FIX
 echo ===============================================

git pull --rebase origin main
if errorlevel 1 (
  echo ERROR: Git pull failed.
  pause
  exit /b 1
)

python APPLY_VASULI_COUNT_FIX.py
if errorlevel 1 (
  echo ERROR: Vasuli count patch failed.
  pause
  exit /b 1
)

git add index.html APPLY_VASULI_COUNT_FIX.py APPLY_VASULI_COUNT_FIX.bat
git diff --cached --quiet
if not errorlevel 1 (
  echo No new changes to commit. Patch may already be applied.
  pause
  exit /b 0
)

git commit -m "Fix Vasuli Janpad and Sub Engineer report counts"
if errorlevel 1 (
  echo ERROR: Git commit failed.
  pause
  exit /b 1
)

git push origin main
if errorlevel 1 (
  echo ERROR: Git push failed.
  pause
  exit /b 1
)

echo.
echo SUCCESS: Vasuli Janpad and Sub Engineer counts fixed and published.
echo Wait 1-3 minutes, then open srdmsatna.online and press Ctrl+F5.
pause
