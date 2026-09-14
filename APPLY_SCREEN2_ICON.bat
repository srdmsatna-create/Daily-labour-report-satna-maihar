@echo off
setlocal
cd /d "%~dp0"
echo ===============================================
echo SRDM SATNA - APPLY SCREEN-2 ICON
echo ===============================================

git pull --rebase origin main
if errorlevel 1 (
  echo ERROR: Git pull failed.
  pause
  exit /b 1
)

py APPLY_SCREEN2_ICON.py 2>nul
if errorlevel 1 python APPLY_SCREEN2_ICON.py
if errorlevel 1 (
  echo ERROR: Screen-2 icon patch failed.
  pause
  exit /b 1
)

git add index.html screen2-workers-icon.svg APPLY_SCREEN2_ICON.py APPLY_SCREEN2_ICON.bat
git diff --cached --quiet
if not errorlevel 1 (
  echo No new changes to commit. Icon may already be applied.
  pause
  exit /b 0
)

git commit -m "Add Screen-2 worker icon"
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
echo SUCCESS: Screen-2 icon published.
echo Wait 1-3 minutes, then open srdmsatna.online and press Ctrl+F5.
pause
