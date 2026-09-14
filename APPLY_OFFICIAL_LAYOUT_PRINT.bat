@echo off
setlocal
cd /d "%~dp0"
echo ===============================================
echo SRDM SATNA - OFFICIAL JANPAD LAYOUT AND PRINT
 echo ===============================================

git stash push -u -m "auto-before-official-layout-print"
git pull --rebase origin main
if errorlevel 1 (
  echo ERROR: Git pull failed.
  pause
  exit /b 1
)

python APPLY_OFFICIAL_LAYOUT_PRINT.py
if errorlevel 1 (
  echo ERROR: Official layout patch failed.
  pause
  exit /b 1
)

git add index.html APPLY_OFFICIAL_LAYOUT_PRINT.py APPLY_OFFICIAL_LAYOUT_PRINT.bat
git diff --cached --quiet
if not errorlevel 1 (
  echo No new changes to commit. Patch may already be applied.
  pause
  exit /b 0
)

git commit -m "Improve Official Janpad layout and add print selection"
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
echo SUCCESS: Official Janpad layout and print selection published.
echo Wait 1-3 minutes, then open srdmsatna.online and press Ctrl+F5.
pause
