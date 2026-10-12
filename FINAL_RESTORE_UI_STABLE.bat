@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title SRDM SATNA - FINAL UI STABLE RESTORE

set "STABLE=402bc6b26d877baf70605f9fed6b146c26e044bc"

echo ==========================================================
echo SRDM SATNA - FINAL UI STABLE RESTORE
echo ==========================================================
echo.
echo Restoring ALL presentation/runtime UI files from stable core.
echo Current live data files are NOT touched.
echo.

git pull --rebase --autostash origin main
if errorlevel 1 goto :err

if not exist backup_final_ui_restore mkdir backup_final_ui_restore
for %%F in (index.html app.js srdm-readable-print-final.js srdm-readable-print-final.css) do (
  if exist "%%F" copy /Y "%%F" "backup_final_ui_restore\%%F" >nul 2>nul
)

echo Restoring stable UI/runtime files...
git checkout %STABLE% -- index.html app.js srdm-readable-print-final.js srdm-readable-print-final.css
if errorlevel 1 goto :err

REM Force fresh browser copies of the restored JavaScript/CSS without changing data files.
powershell -NoProfile -Command "$p='index.html';$s=Get-Content $p -Raw;$s=$s -replace 'app\.js(\?v=[^\"'']*)?','app.js?v=FINAL9002';$s=$s -replace 'srdm-readable-print-final\.js(\?v=[^\"'']*)?','srdm-readable-print-final.js?v=FINAL9002';$s=$s -replace 'srdm-readable-print-final\.css(\?v=[^\"'']*)?','srdm-readable-print-final.css?v=FINAL9002';Set-Content -Path $p -Value $s -Encoding UTF8"
if errorlevel 1 goto :err

git add index.html app.js srdm-readable-print-final.js srdm-readable-print-final.css
git diff --cached --quiet
if not errorlevel 1 goto :push

git commit -m "Final restore all report UI runtime files to stable version"
if errorlevel 1 goto :err

:push
git push origin main
if errorlevel 1 goto :err

echo.
echo ==========================================================
echo SUCCESS: ALL REPORT UI FILES RESTORED TO STABLE VERSION
 echo ==========================================================
echo.
echo IMPORTANT:
echo 1. Wait 2 minutes.
echo 2. Close EVERY Chrome tab/window showing srdmsatna.online.
echo 3. Open Chrome Incognito: Ctrl+Shift+N.
echo 4. Open https://srdmsatna.online
 echo 5. Do NOT run any APPLY/FIX/icon/font/layout BAT.
echo.
pause
exit /b 0

:err
echo.
echo ERROR: Final UI restore failed. Send screenshot of this window.
echo.
pause
exit /b 1
