@echo off
setlocal
cd /d "%~dp0"
if not exist index.html (
 echo ERROR: Put this package files inside your dashboard repository root, where index.html exists.
 pause
 exit /b 1
)
copy /Y index.html index_before_zero_mandays_backup.html >nul
if exist index_ZERO_MANDAYS_FINAL.html (
 copy /Y index_ZERO_MANDAYS_FINAL.html index.html >nul
) else (
 echo ERROR: index_ZERO_MANDAYS_FINAL.html missing
 pause
 exit /b 1
)
findstr /C:"srdmZeroMandaysBtn" index.html >nul || (echo VERIFY FAILED & pause & exit /b 1)
git add index.html
git commit -m "Fix Zero Mandays tab using Mandays Generation live dataset"
git push origin main
echo.
echo SUCCESS: Correct Zero Mandays tab pushed to main.
pause
