@echo off
setlocal EnableExtensions
title SRDM - Install 52 District Automatic Update
set "STATE_REPO=C:\Users\welcome\Daily-labour-report-satna-maihar"
if exist "%~dp0.git" set "STATE_REPO=%~dp0"
if not exist "%STATE_REPO%\.git" (
 echo ERROR: Report repository not found: %STATE_REPO%
 pause
 exit /b 1
)
cd /d "%STATE_REPO%"
set "STATE_PY=py"
where py >nul 2>nul
if errorlevel 1 set "STATE_PY=python"
git fetch origin main
if errorlevel 1 goto :fail
if not exist scripts_local mkdir scripts_local
git show origin/main:scripts_local/run_state_auto.py > scripts_local\run_state_auto.py
if errorlevel 1 goto :fail
%STATE_PY% -m pip install playwright
if errorlevel 1 goto :fail
%STATE_PY% -m playwright install chromium
if errorlevel 1 goto :fail
powershell -NoProfile -Command "$a=New-ScheduledTaskAction -Execute $env:STATE_PY -Argument ('\"'+$env:STATE_REPO+'\scripts_local\run_state_auto.py\"') -WorkingDirectory $env:STATE_REPO; $t=@((New-ScheduledTaskTrigger -Daily -At '08:00'),(New-ScheduledTaskTrigger -AtLogOn),(New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(5) -RepetitionInterval (New-TimeSpan -Hours 1))); $s=New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 20); $p=New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited; Register-ScheduledTask -TaskName 'SRDM_52_DISTRICTS_AUTO' -Action $a -Trigger $t -Settings $s -Principal $p -Force | Out-Null"
if errorlevel 1 goto :fail
echo Automatic task installed: 8 AM, logon and hourly retry while logged in.
echo Running first update now...
%STATE_PY% scripts_local\run_state_auto.py
if errorlevel 1 (
 echo WARNING: First update failed. Open logs\state-auto.log for the reason.
) else (
 echo First run completed. Source status in log determines freshness.
)
echo Log: %STATE_REPO%\logs\state-auto.log
pause
exit /b 0
:fail
echo ERROR: Setup did not finish. Send a screenshot of this window.
pause
exit /b 1
