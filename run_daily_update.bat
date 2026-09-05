@echo off
setlocal EnableExtensions
title SRDM SATNA - All Reports Auto Update
cd /d "%~dp0"

echo =====================================================
echo Starting SRDM ALL REPORTS update from %CD%
echo =====================================================

echo [1/7] Syncing latest repository code...
git pull --rebase --autostash
if errorlevel 1 goto :failpull

echo [2/7] Updating Official R6.9 dashboard data...
python scripts_local\local_auto_update.py
if errorlevel 1 goto :faildata

echo [3/7] Updating Muster Roll and e-MB report...
python scripts_local\update_muster_emb_monitoring.py
if errorlevel 1 goto :faildata

echo [4/7] Updating live Persondays and Shramik Niyojan...
python scripts_local\update_shramik_niyojan.py
if errorlevel 1 goto :faildata

echo [5/7] Updating Yuktdhara and Bhuvan Planning reports...
python scripts_local\update_yuktdhara_monitoring.py
if errorlevel 1 goto :faildata

echo [6/7] Updating VB-G RAM G block statistics...
python scripts_local\update_satna_block_statistics.py
if errorlevel 1 goto :faildata

echo [7/7] Publishing verified report files...
git add auto-data.js auto-status.js data\official-summary.csv data\fetch-status.json muster-emb-data.js shramik-niyojan-data.js yuktdhara-data.js yuktdhara-official-data.js vbg-block-stats.js index.html app.js scripts_local\update_shramik_niyojan.py run_daily_update.bat
git diff --cached --quiet
if not errorlevel 1 goto :success
git commit -m "Auto update all dashboard reports"
if errorlevel 1 goto :failpublish
git pull --rebase --autostash
if errorlevel 1 goto :failpublish
git push origin main
if errorlevel 1 goto :failpublish

:success
echo.
echo SUCCESS: All reports updated. GitHub Pages may take 1-3 minutes.
exit /b 0

:failpull
echo ERROR: Initial git pull/rebase failed. No update was published.
exit /b 25

:faildata
echo ERROR: Official portal update or validation failed. Existing live data was preserved.
exit /b 26

:failpublish
echo ERROR: Final publish failed. Check Git status and the update log.
exit /b 35
