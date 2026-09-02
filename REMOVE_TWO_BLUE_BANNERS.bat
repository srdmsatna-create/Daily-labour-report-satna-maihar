@echo off
setlocal EnableExtensions
title SRDM SATNA - Remove Two Blue Banners
color 0A
cd /d "%~dp0"

if not exist "index.html" (
  color 0C
  echo ERROR: Put this BAT in C:\Users\welcome\Daily-labour-report-satna-maihar
  pause
  exit /b 1
)

copy /y "index.html" "index_before_remove_two_banners.html" >nul

powershell -NoProfile -ExecutionPolicy Bypass -Command "$p='index.html'; $s=[IO.File]::ReadAllText($p); $o=$s; $s=[regex]::Replace($s,'(?s)<section class=\"premium-hero\">.*?</section>\s*',''); $s=[regex]::Replace($s,'(?s)<section class=\"selected-janpad-banner no-print\" id=\"selectedJanpadBanner\">.*?</section>\s*',''); if($s -eq $o){throw 'Target banners not found or already removed'}; [IO.File]::WriteAllText($p,$s,(New-Object Text.UTF8Encoding($false)))"
if errorlevel 1 (
  color 0C
  echo ERROR: Banners could not be removed.
  pause
  exit /b 2
)

where git >nul 2>&1
if errorlevel 1 (
  echo SUCCESS - both banners removed locally. Git publish skipped.
  pause
  exit /b 0
)

git add -- index.html
git commit -m "Remove duplicate blue navigation banners"
if errorlevel 1 (
  echo Banners are already removed or there is nothing new to commit.
  pause
  exit /b 0
)
git pull --rebase --autostash
if errorlevel 1 goto :fail
git push
if errorlevel 1 goto :fail

echo.
echo SUCCESS - both blue banners removed and published.
echo GitHub Pages may take 1-3 minutes. Press Ctrl+F5 afterward.
pause
exit /b 0

:fail
color 0C
echo ERROR: Banners were removed locally, but GitHub publish failed.
echo Backup: index_before_remove_two_banners.html
pause
exit /b 3
