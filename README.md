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

## 23-08-2026 Screen-2 matching fix
- Dashboard top daily metrics now use the lower `Sheet1` table headed `Total No. of Gram Panchayats (GPs)` (the Screen-2 source) for Total GP, GPs with Progress, Labour Engagement, Works with MR, Workers without e-KYC, and Muster Rolls.
- Total Ongoing Works continues to use the upper official `Sheet1` work-load table because Screen 2 does not contain that total.
- `SOHAWAL` from RepDay is normalized to `SATNA` so Janpad filters align with the official Screen-2 label.
- Engineer/Cluster/GP drill-down still uses RepDay, as intended.

## V14 — Top Navigation + Priority Alerts
- Main report tabs are moved to the upper dashboard area and remain sticky while scrolling.
- Added **Priority Alerts** view.
- Priority rules: CRITICAL = ongoing GP with zero Works with MR; HIGH = zero labour or MR coverage under 10%; WATCH = MR coverage under 20%.
- Existing Dysfunctional GP Alert remains available as a separate top tab.

## V15 — Category / Expenditure Buckets
- Added **Category-wise Work** top navigation bucket.
- Added **Exp % Buckets** top navigation bucket.
- Expenditure % for each ongoing VBG work = **Amount booked since inception (Wages + Material) / Total Sanction Amount × 100**.
- Buckets: **0%**, **1%-25%**, **26%-60%**, **61%-75%**, **76%-90%**, **More than 90%**.
- Category and expenditure views respect District, Janpad, Engineer and Cluster filters.
- 0% expenditure works are visually highlighted for priority review.


## V16 Final Work Category Mapping
Category-wise Work now uses the established Final Work Category rules on VBG Work Name + Work Type, not the raw VBG Work Type. Priority rules include strict Ek Bagiya, Boundary Wall, Pulya, Cement Concrete, Gravel Road, Water conservation & recharge, Farm Pond, Watershed Related Works, Dug Well Recharge, Plantation, Crematorium, Panchayat/Community Hall, SBM, Play Field, Anganwadi, Kapildhara and other established categories.


## V17 Engineer-wise correction
- Engineer-wise tab अब Janpad + Engineer / Upyantri पर consolidate होता है।
- एक Engineer के multiple clusters एक ही row में `Cluster(s)` के रूप में दिखते हैं।
- Duplicate engineer rows हटाए गए हैं; metrics engineer level पर sum होते हैं।


## V18 Engineer-wise official reconciliation
Engineer-wise GP, GP Progress, Ongoing Works, Works with MR, Labour and Muster Rolls are integer-apportioned within each Janpad using RepDay as the distribution basis so that each Janpad and district total exactly matches Sheet1 / Screen 2. District targets: GP 695, Progress 542, Ongoing 16,873, Works with MR 1,557, Labour 2,904, Muster Rolls 1,593.


V20 correction: Engineer-wise Dysfunctional GP now uses actual RepDay GP ownership and raw engineer dysfunctional pattern; only Janpad dysfunctional total is reconciled to Official Sheet1. Removed legacy duplicate JS functions that were overriding the corrected table.


V21 update: Added top tab “Ongoing Work All Summary” using current VBG ongoing work-level data, grouped by Janpad + Engineer + Cluster with PMAY-G, Ek Bagiya, Current FY Active, expenditure buckets, sanction/booked/remaining and Exp %. Added the three official VB-G RAM G source links in the dashboard. Note: the dynamic_work_details payload can be session/time-sensitive; current browser upload remains the reliable fallback when the government portal blocks direct fetch.


## V22 update
- Added **Ongoing Works Sheet** tab with 16,214 row-level ongoing works from dynamic_work_details/VBG export.
- Added Janpad/Engineer/Cluster filtering and work-level Sanction, Booked, Exp %, Mandays.
- Added packaged downloadable CSV at `data/Ongoing_Works_dynamic_work_details_Janpad_Wise_23-08-2026.csv`.


## V24 — 24-08-2026 Screen-2 / Sheet1 mapping fix
- Fixed lower Sheet1 embedded Screen-2 columns: Works with MR = column G, Workers without e-KYC = H, Muster Rolls = I.
- Fixed upper official Sheet1 metrics after the blank F column: Labour = G, Works with MR = H, Ongoing Works = I, and downstream category columns shifted correctly.
- Verified current workbook totals: GP 695, GP Progress 533, Labour 2,711, Works with MR 1,521, Muster Rolls 1,548, Official Ongoing Works 16,873.
- Bundled `incoming/Daily Report.xlsx` is the 24-08-2026 corrected workbook.

V25 Dysfunctional GP name/status correction (24-08-2026)
---------------------------------------------------------
- Engineer-wise Dysfunctional GP is now the exact count of RepDay GP rows where GP Progress = 0; no engineer-level apportionment is used.
- Added "Dysfunctional GP Name / Work Status" column.
- For every dysfunctional GP the report shows: GP Name, Ongoing Works, and MR Issued.
- Example: if an engineer has 3 dysfunctional GPs, all 3 names are listed separately with their Ongoing and MR Issued values (normally MR Issued = 0 for these rows).
- Janpad Official Dys GP remains visible for cross-check against Sheet1 / Screen-2.


## V28 IMPORTANT
Open this V28 folder's index.html. The top-right must show **V28 • DISTRICT-DYS FIX**. If not, you opened an older folder. Local CSS/JS are cache-busted with ?v=28.
