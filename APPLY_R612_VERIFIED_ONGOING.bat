@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title SRDM SATNA - APPLY VERIFIED R6.12 ONGOING

echo =====================================================
echo SRDM SATNA - VERIFIED R6.12 ONGOING REBUILD
echo Source: 13-09-2026 FINAL PART 1 + PART 2 + PART 3
echo =====================================================
echo.

git pull --rebase --autostash origin main
if errorlevel 1 goto :err

set PY=python
where py >nul 2>nul && set PY=py
%PY% APPLY_R612_VERIFIED_ONGOING.py
if errorlevel 1 goto :err

git add ongoing-details.js index.html APPLY_R612_VERIFIED_ONGOING.py APPLY_R612_VERIFIED_ONGOING.bat
git diff --cached --quiet
if not errorlevel 1 (
  echo No new changes detected.
  goto :done
)

git commit -m "Rebuild dashboard from verified R6.12 ongoing 15687"
if errorlevel 1 goto :err
git push origin main
if errorlevel 1 goto :err

:done
echo.
echo SUCCESS: VERIFIED R6.12 DATA PUBLISHED
echo Expected checks:
echo   Ongoing Works = 15687
echo   PMAY-G incl IAY = 10807
echo   IAY separate = 0
echo   Ek Bagiya ongoing = 755
echo   Ek Bagiya verified total = 756
echo.
echo Wait 1-3 minutes, then Ctrl+F5 on srdmsatna.online
echo.
pause
exit /b 0

:err
echo.
echo ERROR: Verified rebuild stopped safely.
echo Keep the 3 files below in Downloads and run again:
echo   SRDM_SATNA_R6.12_ONGOING_FINAL_PART1_13-09-2026.xlsx
echo   SRDM_SATNA_R6.12_ONGOING_FINAL_PART2_13-09-2026.xlsx
echo   SRDM_SATNA_R6.12_ONGOING_FINAL_PART3_13-09-2026.xlsx
echo.
pause
exit /b 1
