@echo off
setlocal
cd /d "%~dp0"
echo ===============================================
echo SRDM SATNA - APPLY VERIFIED R6.12 COUNTS
 echo ===============================================

git pull --rebase origin main
if errorlevel 1 (
  echo ERROR: Git pull failed.
  pause
  exit /b 1
)

python APPLY_R612_VERIFIED_COUNTS.py
if errorlevel 1 (
  echo ERROR: R6.12 verified count patch failed.
  pause
  exit /b 1
)

git add index.html APPLY_R612_VERIFIED_COUNTS.py APPLY_R612_VERIFIED_COUNTS.bat
git diff --cached --quiet
if not errorlevel 1 (
  echo No new changes to commit. Patch may already be applied.
  pause
  exit /b 0
)

git commit -m "Use verified R6.12 ongoing PMAY and Ek Bagiya counts"
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
echo SUCCESS: Verified R6.12 counts published.
echo Ongoing = 15687
 echo PMAY-G Ongoing = 10499
 echo Ek Bagiya Ongoing = 755
 echo Ek Bagiya Verified Total = 756
 echo Wait 1-3 minutes, then open srdmsatna.online and press Ctrl+F5.
pause
