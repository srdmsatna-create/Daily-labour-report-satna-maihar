@echo off
setlocal
cd /d "%~dp0"
echo ===============================================
echo SRDM SATNA - APPLY ALL REPORT TABLE STYLE
 echo ===============================================

git pull --rebase origin main
if errorlevel 1 (
  echo ERROR: Git pull failed. Resolve Git issue first.
  pause
  exit /b 1
)

python APPLY_ALL_REPORT_TABLE_STYLE.py
if errorlevel 1 (
  echo ERROR: Table style patch failed.
  pause
  exit /b 1
)

git add index.html APPLY_ALL_REPORT_TABLE_STYLE.py APPLY_ALL_REPORT_TABLE_STYLE.bat
git diff --cached --quiet
if not errorlevel 1 (
  echo No new changes to commit. Patch may already be applied.
  pause
  exit /b 0
)

git commit -m "Improve all report tables and highlight below district average"
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
echo SUCCESS: All report table styles updated and published.
echo Wait 1-3 minutes, then open srdmsatna.online and press Ctrl+F5.
pause
