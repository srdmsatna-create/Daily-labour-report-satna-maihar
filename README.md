# Daily Report Portal V12 — Automatic Update Fix

## Root cause found
1. The V11 package contained `auto-data.js` as `window.SAMPLE_REPORT`, so the page could remain on sample/static data.
2. The GitHub Action requires the repository secret `DAILY_REPORT_XLSX_URL`. Without that secret it can only use `incoming/Daily Report.xlsx`, which is a static fallback and cannot become fresh automatically.
3. The currently supplied workbook itself is mixed-date: Sheet1 = 22-08-2026, RepDay = 11-08-2026. The portal cannot create fresh engineer-wise values until the upstream workbook is refreshed.

## What V12 fixes
- `auto-data.js` is generated as `window.AUTO_REPORT`.
- Scheduled GitHub Action runs 6 times/day in IST.
- Clear Action diagnostic shows whether the URL secret or fallback workbook is being used.
- Dashboard auto-status shows Sheet1 and RepDay source dates.
- Manual Excel upload remains available.
- Existing alert/filter/table layout is retained.

## Required one-time GitHub setup for true automatic daily data
Repository → Settings → Secrets and variables → Actions → New repository secret

Name: `DAILY_REPORT_XLSX_URL`
Value: a direct-download URL that always returns the latest `Daily Report.xlsx`.

Then go to Actions → Daily Report Auto Update → Run workflow once.

If this secret is not configured, the workflow uses `incoming/Daily Report.xlsx`; that fallback is only static.
