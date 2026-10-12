@echo off
setlocal EnableExtensions
title SRDM - Add Yuktdhara Sub Engineer Report Only
set "REPO=C:\Users\welcome\Daily-labour-report-satna-maihar\Daily-labour-report-satna-maihar"
if not exist "%REPO%\index.html" set "REPO=C:\Users\welcome\Daily-labour-report-satna-maihar"
if not exist "%REPO%\index.html" (
  echo ERROR: Original dashboard index.html not found.
  echo No dashboard file was changed.
  pause
  exit /b 1
)
where py >nul 2>nul && (set "PY=py") || (set "PY=python")
%PY% "%~dp0APPLY_YUKTDHARA_SUB_ENGINEER_ONLY.py" --repo "%REPO%"
if errorlevel 1 (
  echo.
  echo ERROR: Patch was not applied. Original dashboard remains unchanged.
  pause
  exit /b 2
)
echo.
echo SUCCESS: Only existing Yuktdhara report was updated.
echo Other dashboard cards, reports and layout were preserved.
echo.
pause
