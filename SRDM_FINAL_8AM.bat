@echo off
title SRDM FINAL - Daily 8 AM Reports
echo SRDM FINAL 8AM - 09 OCT 2026 - corrected launcher
setlocal EnableExtensions DisableDelayedExpansion
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "SRDM_DAILY_BAT=%~f0"
set "SRDM_DAILY_REPO=%~dp0"
if not exist "%SRDM_DAILY_REPO%\.git" (
 echo ERROR: Keep this BAT in the dashboard repository folder.
 goto failed
)
cd /d "%SRDM_DAILY_REPO%"
if errorlevel 1 goto failed
where git >nul 2>&1
if errorlevel 1 (
 echo ERROR: Git is missing from PATH.
 goto failed
)
where py >nul 2>&1
if errorlevel 1 (set "SRDM_DAILY_PY=python") else (set "SRDM_DAILY_PY=py")
where %SRDM_DAILY_PY% >nul 2>&1
if errorlevel 1 goto failed
if /i "%~1"=="--scheduled" goto run
echo Installing one daily 8 AM India task...
powershell.exe -NoProfile -Command "$ErrorActionPreference='Stop'; if((Get-TimeZone).Id -ne 'India Standard Time'){throw 'Windows timezone must be India Standard Time for the 8 AM timer'}; $a=New-ScheduledTaskAction -Execute $env:ComSpec -Argument ('/d /s /c ""'+$env:SRDM_DAILY_BAT+'" --scheduled"') -WorkingDirectory $env:SRDM_DAILY_REPO; $t=New-ScheduledTaskTrigger -Daily -At '08:00'; $s=New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 3); $p=New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited; Register-ScheduledTask -TaskName 'SRDM_ALL_REPORTS_DAILY_8AM' -Action $a -Trigger $t -Settings $s -Principal $p -Force | Out-Null; Write-Host 'Daily 08:00 task installed; missed start runs when laptop is available.'"
if errorlevel 1 goto failed
powershell.exe -NoProfile -Command "$names=@('SRDM_52_DISTRICTS_AUTO','SRDM_GP_EMUSTER_DAILY_8AM','SRDM_GP_ALL_IN_ONE_DAILY_8AM'); foreach($n in $names){try{$t=Get-ScheduledTask -TaskName $n -ErrorAction SilentlyContinue; if($t){$t | Disable-ScheduledTask -ErrorAction Stop | Out-Null}}catch{Write-Host ('WARNING: Could not disable old task '+$n+'. Current report update will continue.')}}; exit 0"
:run
echo Preparing latest unified updater...
git fetch origin main
if errorlevel 1 goto failed
set "SRDM_DAILY_BOOT=%TEMP%\SRDM_BOOT_%RANDOM%_%RANDOM%"
git worktree add --detach "%SRDM_DAILY_BOOT%" origin/main
if errorlevel 1 goto failed
%SRDM_DAILY_PY% -m pip install -r "%SRDM_DAILY_BOOT%\requirements.txt" requests beautifulsoup4 >> "%SRDM_DAILY_REPO%\daily-all-reports.log" 2>&1
if errorlevel 1 goto failed
%SRDM_DAILY_PY% -m playwright install chromium >> "%SRDM_DAILY_REPO%\daily-all-reports.log" 2>&1
if errorlevel 1 goto failed
echo Refreshing all reports. Details: daily-all-reports.log
%SRDM_DAILY_PY% -u "%SRDM_DAILY_BOOT%\scripts_local\run_daily_unified.py" --publish >> "%SRDM_DAILY_REPO%\daily-all-reports.log" 2>&1
if errorlevel 1 goto failed
git worktree remove "%SRDM_DAILY_BOOT%"
echo SUCCESS: Complete verified reports published together.
if /i not "%~1"=="--scheduled" pause
exit /b 0
:failed
echo FAILED: Complete update did not finish. Existing live reports are preserved.
if exist "%SRDM_DAILY_REPO%\daily-all-reports.log" powershell.exe -NoProfile -Command "Get-Content -LiteralPath (Join-Path $env:SRDM_DAILY_REPO 'daily-all-reports.log') -Tail 35"
if /i not "%~1"=="--scheduled" pause
exit /b 1
