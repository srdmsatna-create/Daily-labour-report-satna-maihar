@echo off
setlocal EnableExtensions
title SRDM SATNA - Install Shramik Niyojan Final

set "REPO=%USERPROFILE%\Daily-labour-report-satna-maihar"
set "PAYLOAD=%~dp0update_files"

echo ============================================================
echo       SRDM SATNA - SHRAMIK NIYOJAN FINAL INSTALLER
echo ============================================================
echo.

if exist "%REPO%\.git" goto REPO_FOUND
if exist "%REPO%\index.html" goto REPO_FOUND
for /d %%D in ("%USERPROFILE%\Daily-labour-report-satna-maihar*") do if exist "%%~fD\.git" set "REPO=%%~fD"
if exist "%REPO%\.git" goto REPO_FOUND
for /d %%D in ("%USERPROFILE%\Downloads\Daily-labour-report-satna-maihar*") do if exist "%%~fD\.git" set "REPO=%%~fD"
if exist "%REPO%\.git" goto REPO_FOUND
echo Dashboard folder auto-detect nahi hua.
echo Folder ka complete path paste kare, example:
echo C:\Users\welcome\Daily-labour-report-satna-maihar
set /p "REPO=Dashboard folder path: "
if not exist "%REPO%\.git" (
  echo ERROR: Is folder me Git dashboard repository nahi mila:
  echo %REPO%
  pause
  exit /b 1
)

:REPO_FOUND
echo Dashboard folder: %REPO%
if not exist "%PAYLOAD%\index.html" (
  echo ERROR: Update files are missing. Extract the complete ZIP first.
  pause
  exit /b 1
)

copy /Y "%PAYLOAD%\index.html" "%REPO%\index.html" >nul
copy /Y "%PAYLOAD%\shramik-niyojan.js" "%REPO%\shramik-niyojan.js" >nul
copy /Y "%PAYLOAD%\shramik-niyojan-data.js" "%REPO%\shramik-niyojan-data.js" >nul
copy /Y "%PAYLOAD%\ONE_CLICK_DASHBOARD_DATA_UPDATE.bat" "%REPO%\ONE_CLICK_DASHBOARD_DATA_UPDATE.bat" >nul
copy /Y "%PAYLOAD%\README_SHRAMIK_NIYOJAN_HINDI.txt" "%REPO%\README_SHRAMIK_NIYOJAN_HINDI.txt" >nul
if not exist "%REPO%\scripts_local" mkdir "%REPO%\scripts_local"
copy /Y "%PAYLOAD%\scripts_local\update_shramik_niyojan.py" "%REPO%\scripts_local\update_shramik_niyojan.py" >nul

echo Update files installed successfully.
echo.
echo Starting One Click live-data update and GitHub publish...
call "%REPO%\ONE_CLICK_DASHBOARD_DATA_UPDATE.bat"
exit /b %errorlevel%
