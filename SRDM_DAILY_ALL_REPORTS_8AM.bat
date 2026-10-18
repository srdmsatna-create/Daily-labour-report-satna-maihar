@echo off
setlocal EnableExtensions DisableDelayedExpansion
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "PYTHONUNBUFFERED=1"
title SRDM Daily 6AM - LIVE Report Progress
set "SRDM_DAILY_BAT=%~f0"
set "SRDM_DAILY_REPO=%~dp0"
if not exist "%SRDM_DAILY_REPO%.git" set "SRDM_DAILY_REPO=%USERPROFILE%\Daily-labour-report-satna-maihar"
if not exist "%SRDM_DAILY_REPO%\.git" (
 echo ERROR: Keep this BAT in the dashboard repository folder.
 goto failed
)
cd /d "%SRDM_DAILY_REPO%"
where py >nul 2>&1
if errorlevel 1 (set "SRDM_DAILY_PY=python") else (set "SRDM_DAILY_PY=py")
where %SRDM_DAILY_PY% >nul 2>&1
if errorlevel 1 goto failed
if /i "%~1"=="--scheduled" goto run
echo Installing one daily 6 AM India task...
powershell.exe -NoProfile -Command "$ErrorActionPreference='Stop'; if((Get-TimeZone).Id -ne 'India Standard Time'){throw 'Windows timezone must be India Standard Time for the 6 AM timer'}; $a=New-ScheduledTaskAction -Execute $env:ComSpec -Argument ('/d /s /c ""'+$env:SRDM_DAILY_BAT+'" --scheduled"') -WorkingDirectory $env:SRDM_DAILY_REPO; $u=[Security.Principal.WindowsIdentity]::GetCurrent().Name; $t=@((New-ScheduledTaskTrigger -Daily -At '06:00'),(New-ScheduledTaskTrigger -AtLogOn -User $u)); $s=New-ScheduledTaskSettingsSet -StartWhenAvailable -WakeToRun -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 15) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 3); $p=New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited; Register-ScheduledTask -TaskName 'SRDM_ALL_REPORTS_DAILY_6AM' -Action $a -Trigger $t -Settings $s -Principal $p -Force | Out-Null; Write-Host 'Daily 06:00 + every sign-in installed; missed run starts when laptop is available.'"
if errorlevel 1 goto failed
powershell.exe -NoProfile -Command "$names=@('SRDM_ALL_REPORTS_DAILY_8AM','SRDM_52_DISTRICTS_AUTO','SRDM_GP_EMUSTER_DAILY_8AM','SRDM_GP_ALL_IN_ONE_DAILY_8AM'); foreach($n in $names){try{$t=Get-ScheduledTask -TaskName $n -ErrorAction SilentlyContinue; if($t){$t | Disable-ScheduledTask -ErrorAction Stop | Out-Null}}catch{Write-Host ('WARNING: Could not disable old task '+$n+'. Current report update will continue.')}}; exit 0"
:run
echo Preparing latest unified updater...
git fetch origin main
if errorlevel 1 goto failed
set "SRDM_DAILY_BOOT=%TEMP%\SRDM_BOOT_%RANDOM%_%RANDOM%"
git worktree add --detach "%SRDM_DAILY_BOOT%" origin/main
if errorlevel 1 goto failed
echo [1/3] Checking Python requirements - live output below...
powershell.exe -NoProfile -Command "$ErrorActionPreference='Continue'; [Console]::OutputEncoding=New-Object System.Text.UTF8Encoding; & $env:SRDM_DAILY_PY -u -m pip install -r (Join-Path $env:SRDM_DAILY_BOOT 'requirements.txt') requests beautifulsoup4 2>&1 | Tee-Object -FilePath (Join-Path $env:SRDM_DAILY_REPO 'daily-all-reports.log') -Append; exit $LASTEXITCODE"
if errorlevel 1 goto failed
echo [2/3] Checking browser installation - live output below...
powershell.exe -NoProfile -Command "$ErrorActionPreference='Continue'; [Console]::OutputEncoding=New-Object System.Text.UTF8Encoding; & $env:SRDM_DAILY_PY -u -m playwright install chromium 2>&1 | Tee-Object -FilePath (Join-Path $env:SRDM_DAILY_REPO 'daily-all-reports.log') -Append; exit $LASTEXITCODE"
if errorlevel 1 goto failed
echo Refreshing all reports. Details: daily-all-reports.log
echo [3/3] LIVE REPORT UPDATE - each report name, progress and errors will appear below.
powershell.exe -NoProfile -Command "$ErrorActionPreference='Continue'; [Console]::OutputEncoding=New-Object System.Text.UTF8Encoding; & $env:SRDM_DAILY_PY -u (Join-Path $env:SRDM_DAILY_BOOT 'scripts_local\run_daily_unified.py') --publish 2>&1 | Tee-Object -FilePath (Join-Path $env:SRDM_DAILY_REPO 'daily-all-reports.log') -Append; exit $LASTEXITCODE"
if errorlevel 1 goto failed
git worktree remove "%SRDM_DAILY_BOOT%"
echo SUCCESS: Complete verified reports published together.
if /i not "%~1"=="--scheduled" pause
exit /b 0
:failed
echo FAILED: Full update was not completed. Read daily-all-reports.log; existing live reports are preserved.
if /i not "%~1"=="--scheduled" pause
exit /b 1
