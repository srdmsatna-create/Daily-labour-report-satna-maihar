@echo off
setlocal EnableExtensions
title SRDM SATNA - All Reports Auto Update
cd /d "%~dp0"

echo =====================================================
echo Starting SRDM ALL REPORTS update from %CD%
echo =====================================================

echo [1/8] Syncing latest repository code...
git pull --rebase --autostash
if errorlevel 1 goto :failpull

echo [2/8] Updating Official R6.9 dashboard data...
python scripts_local\local_auto_update.py
if errorlevel 1 goto :faildata

echo [3/8] Updating Muster Roll and e-MB report...
python scripts_local\update_muster_emb_monitoring.py
if errorlevel 1 goto :faildata

echo [4/8] Updating live Persondays and Shramik Niyojan...
python scripts_local\update_shramik_niyojan.py
if errorlevel 1 goto :faildata

echo [5/8] Updating Yuktdhara and Bhuvan Planning reports...
python scripts_local\update_yuktdhara_monitoring.py
if errorlevel 1 goto :faildata

echo [6/8] Updating VB-G RAM G block statistics...
python scripts_local\update_satna_block_statistics.py
if errorlevel 1 goto :faildata

echo [7/8] Updating MIS Report 6.12 work details...
python scripts_local\update_mis_612_work_details.py
if errorlevel 1 goto :faildata

echo [8/8] Publishing verified report files...
git add auto-data.js auto-status.js data\official-summary.csv data\fetch-status.json data\Ongoing_Works_dynamic_work_details_latest.csv data\mis-6.12-status.json ongoing-details.js muster-emb-data.js shramik-niyojan-data.js yuktdhara-data.js yuktdhara-official-data.js vbg-block-stats.js index.html app.js scripts\update_ongoing_csv.py scripts_local\update_mis_612_work_details.py scripts_local\update_shramik_niyojan.py run_daily_update.bat
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
