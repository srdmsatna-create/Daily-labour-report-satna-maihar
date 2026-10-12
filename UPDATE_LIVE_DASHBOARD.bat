@echo off
setlocal EnableExtensions
chcp 65001 >nul
title SRDM SATNA Dashboard Update

echo =====================================================
echo   SRDM SATNA - Mandays Dashboard One Click Update
echo =====================================================
echo.

set "PACKAGE_DIR=%~dp0"
set "SOURCE_FILE=%PACKAGE_DIR%index.html"

if not exist "%SOURCE_FILE%" (
  echo ERROR: index.html is not available with this BAT file.
  echo Extract the complete ZIP first, then run this BAT file.
  pause
  exit /b 1
)

set /p "REPO_DIR=Paste your GitHub repository folder path: "
set "REPO_DIR=%REPO_DIR:"=%"

if not exist "%REPO_DIR%\.git" (
  echo.
  echo ERROR: This is not a Git repository folder:
  echo %REPO_DIR%
  pause
  exit /b 1
)

where git >nul 2>&1
if errorlevel 1 (
  echo.
  echo ERROR: Git is not installed or is not available in PATH.
  pause
  exit /b 1
)

if exist "%REPO_DIR%\index.html" (
  copy /Y "%REPO_DIR%\index.html" "%REPO_DIR%\index_BACKUP_BEFORE_MANDAYS_FIX.html" >nul
  if errorlevel 1 (
    echo ERROR: Could not create the backup file.
    pause
    exit /b 1
  )
)

copy /Y "%SOURCE_FILE%" "%REPO_DIR%\index.html" >nul
if errorlevel 1 (
  echo ERROR: Could not copy corrected index.html.
  pause
  exit /b 1
)

pushd "%REPO_DIR%"
git add index.html
git diff --cached --quiet
if not errorlevel 1 (
  echo.
  echo No new change was detected. The corrected file may already be live.
  popd
  pause
  exit /b 0
)

git commit -m "Fix Rampur Baghelan mandays engineer cluster mapping"
if errorlevel 1 (
  echo.
  echo ERROR: Git commit failed. Check your Git name/email configuration.
  popd
  pause
  exit /b 1
)

git push
if errorlevel 1 (
  echo.
  echo ERROR: Git push failed. Sign in to GitHub and run this BAT again.
  popd
  pause
  exit /b 1
)

popd
echo.
echo SUCCESS: Corrected dashboard was pushed to GitHub.
echo GitHub Pages may take 1-3 minutes to refresh.
echo Open: https://srdmsatna.online/
pause
exit /b 0
