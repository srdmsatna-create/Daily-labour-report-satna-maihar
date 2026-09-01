Run only:
RUN_EXCEL_DOWNLOAD_FIX.bat

The Excel button was visible, but the current external print JS had no Excel click handler.

This fix adds a separate external Excel script:
srdm-excel-download-final.js

It downloads the CURRENT visible report as an Excel-compatible .xls file.

It does not change:
- Print/PDF
- PMAY-G
- Ek Bagiya
- Recovery
- dashboard data
