@echo off
setlocal
cd /d "%~dp0"
echo ===============================================
echo SRDM SATNA - RESTORE PMAY / EK BAGIYA MR COLUMNS
echo ===============================================

git stash push -u -m "auto-before-restore-mr-columns"
git pull --rebase origin main
if errorlevel 1 (
  echo ERROR: Git pull failed.
  pause
  exit /b 1
)

python RESTORE_P_MUSTER_COLUMNS.py
if errorlevel 1 (
  echo ERROR: Restore MR columns patch failed.
  pause
  exit /b 1
)

git add index.html RESTORE_P_MUSTER_COLUMNS.py RESTORE_P_MUSTER_COLUMNS.bat
git diff --cached --quiet
if not errorlevel 1 (
  echo No new changes to commit. Patch may already be applied.
  pause
  exit /b 0
)

git commit -m "Restore PMAY and Ek Bagiya live MR columns"
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
echo SUCCESS: PMAY-G and Ek Bagiya MR columns restored and published.
echo Verified Ongoing stays: PMAY-G 10499 ^| Ek Bagiya 755
echo Live MR Issued and MR %% stay from today's official report.
echo Wait 1-3 minutes, then open srdmsatna.online and press Ctrl+F5.
pause
