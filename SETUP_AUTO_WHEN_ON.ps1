$ErrorActionPreference = "Stop"

$Repo = "C:\Users\welcome\Daily-labour-report-satna-maihar"
$Runner = Join-Path $Repo "VBGRAMG_AUTO_WHEN_ON.bat"

if (-not (Test-Path (Join-Path $Repo ".git"))) {
    throw "Git repository not found: $Repo"
}
if (-not (Test-Path $Runner)) {
    throw "VBGRAMG_AUTO_WHEN_ON.bat not found in repo root."
}

$Action = New-ScheduledTaskAction `
    -Execute "cmd.exe" `
    -Argument "/c `"$Runner`"" `
    -WorkingDirectory $Repo

$Settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 25)

$Principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Highest

$AtLogOn = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME

$Hourly = New-ScheduledTaskTrigger `
    -Once `
    -At (Get-Date).AddMinutes(2) `
    -RepetitionInterval (New-TimeSpan -Hours 1) `
    -RepetitionDuration (New-TimeSpan -Days 3650)

Register-ScheduledTask `
    -TaskName "SRDM VBGRAMG Auto When Laptop On" `
    -Action $Action `
    -Trigger @($AtLogOn, $Hourly) `
    -Settings $Settings `
    -Principal $Principal `
    -Description "Fetch official VB-G RAM G at login and hourly while laptop is on." `
    -Force | Out-Null

Write-Host ""
Write-Host "============================================================"
Write-Host " VBGRAMG AUTO-WHEN-ON INSTALLED"
Write-Host "============================================================"
Write-Host "Runs automatically:"
Write-Host " - at Windows login"
Write-Host " - every hour while laptop is ON"
Write-Host ""
Write-Host "Running one test now..."
Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$Runner`"" -WorkingDirectory $Repo -Wait
Write-Host ""
Write-Host "Test finished."
Write-Host "Log: $Repo\logs\auto-when-on.log"
