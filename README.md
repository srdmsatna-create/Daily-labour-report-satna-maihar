# Daily Report Portal V3 — Auto Update + Manual Fallback

Static portal ready for GitHub Pages. It supports **two modes**:

1. **AUTO:** GitHub Actions runs `scripts/update_daily_report.py`, reads the latest workbook, and rebuilds `auto-data.js`.
2. **MANUAL FALLBACK:** From the portal, choose the latest Excel and click **रिपोर्ट बनाएँ**. Processing remains local in the browser.

## Auto-update source
Choose either method:

### A. Source workbook URL (best)
Create GitHub repository secret `DAILY_REPORT_XLSX_URL` containing a direct downloadable `.xlsx` URL. The Action fetches it and updates the portal automatically.

### B. Workbook stored in repo
Put the current workbook at `incoming/Daily Report.xlsx`. If no secret URL is set, the updater uses this file.

> VB-G RAM G can be used directly only when a stable downloadable report URL is available without captcha/manual session. If the government portal requires interactive login/captcha, use an exported workbook URL/file as the automation source.

## Schedule
`.github/workflows/auto-update.yml` currently runs 5 times per day (IST approx 07:45, 10:45, 13:45, 16:45, 19:45) and can also be run manually with **Run workflow**.

## GitHub Pages
For a new repo, enable **Settings → Pages → Deploy from a branch → main / root**. The standard Pages URL will work immediately. A custom subdomain can be connected later.

## Views
- Official Janpad Daily
- Engineer / Upyantri-wise
- Full District Report
- GP Detail
- District / Janpad / Engineer / Cluster filters
- Print / PDF
- CSV export
- Last auto-update status
