@echo off
setlocal EnableExtensions EnableDelayedExpansion
title SRDM SATNA - Install Yuktdhara Monitoring
color 0A
set "REPO="

REM First check this ZIP extraction folder and its usual child folder.
if exist "%~dp0index.html" set "REPO=%~dp0"
if not defined REPO if exist "%~dp0Daily-labour-report-satna-maihar\index.html" set "REPO=%~dp0Daily-labour-report-satna-maihar"

REM Then check common Windows locations.
for %%D in (
  "%USERPROFILE%\Daily-labour-report-satna-maihar"
  "%USERPROFILE%\Desktop\Daily-labour-report-satna-maihar"
  "%USERPROFILE%\Downloads\Daily-labour-report-satna-maihar"
  "%USERPROFILE%\Documents\Daily-labour-report-satna-maihar"
) do if not defined REPO if exist "%%~D\index.html" set "REPO=%%~D"

REM Search for the dashboard by its updater file in common user folders.
if not defined REPO for %%B in ("%USERPROFILE%\Desktop" "%USERPROFILE%\Downloads" "%USERPROFILE%\Documents" "%USERPROFILE%") do (
  if not defined REPO for /f "delims=" %%F in ('where /r "%%~B" ONE_CLICK_DASHBOARD_DATA_UPDATE.bat 2^>nul') do (
    if exist "%%~dpFindex.html" set "REPO=%%~dpF"
  )
)

REM If still not found, show a normal folder-selection window.
if not defined REPO (
  echo Dashboard folder automatically nahi mila. Folder select kijiye...
  for /f "usebackq delims=" %%D in (`powershell -NoProfile -STA -Command "Add-Type -AssemblyName System.Windows.Forms; $f=New-Object System.Windows.Forms.FolderBrowserDialog; $f.Description='Select SRDM dashboard folder containing index.html'; if($f.ShowDialog() -eq 'OK'){$f.SelectedPath}"`) do set "REPO=%%D"
)

if not defined REPO goto :nofolder
if not exist "%REPO%\index.html" goto :nofolder
echo Dashboard folder: %REPO%
cd /d "%REPO%"
where py >nul 2>&1 && set "PY=py"
if not defined PY set "PY=python"
%PY% "%~dp0APPLY_YUKTDHARA_MODULE.py" --repo "%REPO%"
if errorlevel 1 (color 0C& echo ERROR: Yuktdhara module installation failed.& pause& exit /b 2)
%PY% "%~dp0APPLY_MUSTER_EMB_MODULE.py" --repo "%REPO%"
if errorlevel 1 (color 0C& echo ERROR: Muster Roll and e-MB module installation failed.& pause& exit /b 2)
REM Stage each existing output separately; one missing optional file must not cancel all staging.
for %%F in (index.html yuktdhara-data.js muster-emb-data.js scripts_local\update_yuktdhara_monitoring.py scripts_local\update_muster_emb_monitoring.py ONE_CLICK_DASHBOARD_DATA_UPDATE.bat) do (
  if exist "%%F" git add -- "%%F"
)
git diff --cached --quiet
if not errorlevel 1 (
  color 0C
  echo ERROR: Report files were created but nothing was staged for GitHub.
  echo Log ka screenshot bhejiye. SUCCESS nahi mana jayega.
  pause
  exit /b 4
)
git commit -m "Add Yuktdhara and Muster e-MB monitoring reports"
if errorlevel 1 (color 0C& echo ERROR: Git commit failed.& pause& exit /b 5)
git pull --rebase --autostash
if errorlevel 1 goto :fail
git push
if errorlevel 1 goto :fail
git status --porcelain -- index.html yuktdhara-data.js muster-emb-data.js scripts_local/update_yuktdhara_monitoring.py scripts_local/update_muster_emb_monitoring.py
if errorlevel 1 goto :fail
echo SUCCESS - Yuktdhara and Muster Roll e-MB reports published.
echo Wait 1-3 minutes and press Ctrl+Shift+R.
pause
exit /b 0
:fail
color 0C
echo ERROR: Module installed locally but GitHub publish failed.
pause
exit /b 3

:nofolder
color 0C
echo ERROR: Selected folder me index.html nahi mila.
echo Dashboard ka main folder select kare jisme index.html aur ONE_CLICK_DASHBOARD_DATA_UPDATE.bat ho.
pause
exit /b 1
