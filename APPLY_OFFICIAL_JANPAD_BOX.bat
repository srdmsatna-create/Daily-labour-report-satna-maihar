@echo off
setlocal
cd /d "%~dp0"
echo ===============================================
echo SRDM SATNA - OFFICIAL JANPAD BOX PATCH
 echo ===============================================

git pull --rebase origin main
if errorlevel 1 (
  echo ERROR: Git pull failed.
  pause
  exit /b 1
)

python APPLY_OFFICIAL_JANPAD_BOX.py
if errorlevel 1 (
  echo ERROR: Patch failed.
  pause
  exit /b 1
)

git add index.html APPLY_OFFICIAL_JANPAD_BOX.py APPLY_OFFICIAL_JANPAD_BOX.bat
git diff --cached --quiet
if not errorlevel 1 (
  echo No new changes to commit. Patch may already be applied.
  pause
  exit /b 0
)

git commit -m "Box Official Janpad PMAY-G and Ek Bagiya ongoing columns"
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
echo SUCCESS: Official Janpad report updated.
echo Wait 1-3 minutes, then open srdmsatna.online and press Ctrl+F5.
pause
