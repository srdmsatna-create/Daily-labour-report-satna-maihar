@echo off
setlocal EnableExtensions
title SRDM SATNA - Apply VBGRAM Source Summary Link
color 0A
cd /d "%~dp0"

if not exist "index.html" (
  color 0C
  echo ERROR: Put this BAT in C:\Users\welcome\Daily-labour-report-satna-maihar
  pause
  exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "$p='index.html'; $s=[IO.File]::ReadAllText($p); $n='<div class=\"vbg-stat-source\">FY 2026-27 ^&bull; <a href=\"https://vbgramgrep.dord.gov.in/VBGRAMG/vbgramg_ataglance/At_a_glance.aspx\" target=\"_blank\" rel=\"noopener noreferrer\">Source Summary</a></div>'; $r=[regex]::Replace($s,'<div class=\"vbg-stat-source\">.*?</div>',$n); if($r -eq $s){throw 'VB-GRAM Statistics source footer not found or already unchanged'}; [IO.File]::WriteAllText($p,$r,(New-Object Text.UTF8Encoding($false)))"
if errorlevel 1 (
  color 0C
  echo ERROR: Source footer could not be updated.
  pause
  exit /b 2
)

where git >nul 2>&1
if errorlevel 1 (
  echo index.html updated locally. Git was not found, so publish was skipped.
  pause
  exit /b 0
)

git add -- index.html
git commit -m "Add official VBGRAM At-a-Glance source link"
if errorlevel 1 (
  echo Source link is already applied or there is nothing new to commit.
  pause
  exit /b 0
)
git pull --rebase --autostash
if errorlevel 1 goto :fail
git push
if errorlevel 1 goto :fail

echo.
echo SUCCESS - Source Summary link published. Allow GitHub Pages 1-3 minutes.
pause
exit /b 0

:fail
color 0C
echo ERROR: Link was updated locally, but GitHub publish failed.
pause
exit /b 3
