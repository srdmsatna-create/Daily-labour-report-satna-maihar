@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>&1
if not errorlevel 1 (
  set "PY=py -3"
) else (
  set "PY=python"
)

git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
  echo ERROR: Is file ko repository ke main folder me rakhein aur wahin se chalayein.
  pause
  exit /b 1
)

git diff --cached --quiet
if errorlevel 1 (
  echo ERROR: Git me pehle se staged changes hain. Unhe commit ya unstage karke phir chalayein.
  pause
  exit /b 1
)

echo.
echo AS /Yuktdhara Before-Geotag report source se fetch ho rahi hai.
echo Agar portal login mange, khule browser me login karke yahan Enter dabayein.
echo.

%PY% -u scripts_local/update_as_geotag_before.py
if errorlevel 1 (
  echo.
  echo FAILED: Portal fetch/validation nahi hui. Purani live report bani rahegi.
  pause
  exit /b 1
)

%PY% scripts_local/apply_secure_ts_counts.py
if errorlevel 1 (
  echo FAILED: AS, SECURE TS aur R33.1 source ko merge/reconcile nahi kiya ja saka.
  pause
  exit /b 1
)

git add -- data/as-geotag-before-latest.json as-geotag-before-data.js as-geotag-before.html index.html
if errorlevel 1 (
  echo ERROR: Refreshed files stage nahi ho sake.
  pause
  exit /b 1
)

git diff --cached --quiet
if not errorlevel 1 (
  echo Koi naya report data nahi tha; publish karne ke liye changes nahi mile.
  pause
  exit /b 0
)

git commit -m "Refresh AS before geotag report"
if errorlevel 1 (
  echo ERROR: Commit nahi ho saka.
  pause
  exit /b 1
)

git fetch origin main
if errorlevel 1 (
  echo ERROR: GitHub se latest main fetch nahi hua. Commit local me surakshit hai.
  pause
  exit /b 1
)

git rebase origin/main
if errorlevel 1 (
  echo ERROR: Rebase conflict. Automatic push roka gaya; local commit surakshit hai.
  git rebase --abort
  pause
  exit /b 1
)

git push origin HEAD:main
if errorlevel 1 (
  echo ERROR: GitHub push fail hua. Local commit surakshit hai.
  pause
  exit /b 1
)

echo.
echo SUCCESS: Fresh report GitHub par publish ho gayi. Pages deploy kuch minute le sakta hai.
pause
