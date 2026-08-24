$ErrorActionPreference = 'Stop'

$folder = Split-Path -Parent $MyInvocation.MyCommand.Path
$workbookPath = Join-Path $folder 'Daily_Report_MASTER.xlsx'

if (!(Test-Path $workbookPath)) {
    throw "Daily_Report_MASTER.xlsx not found in package folder."
}

function ColLetter([int]$n) {
    $s = ""
    while ($n -gt 0) {
        $n--
        $s = [char](65 + ($n % 26)) + $s
        $n = [math]::Floor($n / 26)
    }
    return $s
}

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
$excel.AskToUpdateLinks = $false

try {
    $wb = $excel.Workbooks.Open($workbookPath)

    # Refresh all existing queries/connections first.
    try {
        $wb.RefreshAll()
        Start-Sleep -Seconds 2
        try { $excel.CalculateUntilAsyncQueriesDone() } catch {}
    } catch {
        Write-Host "RefreshAll warning: $($_.Exception.Message)"
    }

    $rep = $wb.Worksheets.Item('RepDay')
    $daily = $wb.Worksheets.Item('Daily Report')

    # Detect last used rows automatically every day.
    $xlUp = -4162
    $lastRep = $rep.Cells($rep.Rows.Count, 1).End($xlUp).Row
    $lastDaily = $daily.Cells($daily.Rows.Count, 4).End($xlUp).Row

    if ($lastRep -lt 4) { throw "RepDay sheet has no data rows." }
    if ($lastDaily -lt 3) { throw "Daily Report sheet has no data rows." }

    # Normalize headers so mapping is explicit.
    $daily.Cells(2,5).Value2  = 'Total Ongoing Work'
    $daily.Cells(2,6).Value2  = 'Ongoing Works for which Muster Rolls Issued'
    $daily.Cells(2,7).Value2  = 'No Of GPS'
    $daily.Cells(2,8).Value2  = 'Muster Issue GPS'
    $daily.Cells(2,9).Value2  = 'Dysfunctional GPS'
    $daily.Cells(2,10).Value2 = 'Unskilled Labour Engagement'
    $daily.Cells(2,11).Value2 = 'Muster Rolls'
    $daily.Cells(2,12).Value2 = 'Workers without e-KYC'

    # Robust key-based mapping:
    # Daily Report key = Janpad + Engineer + Cluster + Panchayat
    # RepDay key      = Janpad + Eng_Name + CFT_Name + Panchayats
    #
    # SUMIFS is used instead of row-to-row links, so sorting/order changes do not break the report.
    for ($r = 3; $r -le $lastDaily; $r++) {
        $rr = $r
        $daily.Cells($r,5).Formula  = "=IFERROR(SUMIFS(RepDay!`$D`$4:`$D`$$lastRep,RepDay!`$A`$4:`$A`$$lastRep,`$A$rr,RepDay!`$B`$4:`$B`$$lastRep,`$B$rr,RepDay!`$C`$4:`$C`$$lastRep,`$C$rr,RepDay!`$F`$4:`$F`$$lastRep,`$D$rr),0)"
        $daily.Cells($r,6).Formula  = "=IFERROR(SUMIFS(RepDay!`$J`$4:`$J`$$lastRep,RepDay!`$A`$4:`$A`$$lastRep,`$A$rr,RepDay!`$B`$4:`$B`$$lastRep,`$B$rr,RepDay!`$C`$4:`$C`$$lastRep,`$C$rr,RepDay!`$F`$4:`$F`$$lastRep,`$D$rr),0)"
        $daily.Cells($r,7).Formula  = "=IFERROR(SUMIFS(RepDay!`$G`$4:`$G`$$lastRep,RepDay!`$A`$4:`$A`$$lastRep,`$A$rr,RepDay!`$B`$4:`$B`$$lastRep,`$B$rr,RepDay!`$C`$4:`$C`$$lastRep,`$C$rr,RepDay!`$F`$4:`$F`$$lastRep,`$D$rr),0)"
        $daily.Cells($r,8).Formula  = "=IFERROR(SUMIFS(RepDay!`$H`$4:`$H`$$lastRep,RepDay!`$A`$4:`$A`$$lastRep,`$A$rr,RepDay!`$B`$4:`$B`$$lastRep,`$B$rr,RepDay!`$C`$4:`$C`$$lastRep,`$C$rr,RepDay!`$F`$4:`$F`$$lastRep,`$D$rr),0)"
        $daily.Cells($r,9).Formula  = "=MAX(0,G$rr-H$rr)"
        $daily.Cells($r,10).Formula = "=IFERROR(SUMIFS(RepDay!`$I`$4:`$I`$$lastRep,RepDay!`$A`$4:`$A`$$lastRep,`$A$rr,RepDay!`$B`$4:`$B`$$lastRep,`$B$rr,RepDay!`$C`$4:`$C`$$lastRep,`$C$rr,RepDay!`$F`$4:`$F`$$lastRep,`$D$rr),0)"
        $daily.Cells($r,11).Formula = "=IFERROR(SUMIFS(RepDay!`$L`$4:`$L`$$lastRep,RepDay!`$A`$4:`$A`$$lastRep,`$A$rr,RepDay!`$B`$4:`$B`$$lastRep,`$B$rr,RepDay!`$C`$4:`$C`$$lastRep,`$C$rr,RepDay!`$F`$4:`$F`$$lastRep,`$D$rr),0)"
        $daily.Cells($r,12).Formula = "=IFERROR(SUMIFS(RepDay!`$K`$4:`$K`$$lastRep,RepDay!`$A`$4:`$A`$$lastRep,`$A$rr,RepDay!`$B`$4:`$B`$$lastRep,`$B$rr,RepDay!`$C`$4:`$C`$$lastRep,`$C$rr,RepDay!`$F`$4:`$F`$$lastRep,`$D$rr),0)"
    }

    # Full workbook recalculation.
    $excel.CalculateFullRebuild()

    # Automatic validation totals from RepDay vs Daily Report.
    $repMR = $excel.WorksheetFunction.Sum($rep.Range("L4:L$lastRep"))
    $dailyMR = $excel.WorksheetFunction.Sum($daily.Range("K3:K$lastDaily"))
    $repWorksMR = $excel.WorksheetFunction.Sum($rep.Range("J4:J$lastRep"))
    $dailyWorksMR = $excel.WorksheetFunction.Sum($daily.Range("F3:F$lastDaily"))
    $repEng = $excel.WorksheetFunction.Sum($rep.Range("I4:I$lastRep"))
    $dailyEng = $excel.WorksheetFunction.Sum($daily.Range("J3:J$lastDaily"))

    # Create / refresh a validation sheet.
    try { $check = $wb.Worksheets.Item('AUTO CHECK') }
    catch {
        $check = $wb.Worksheets.Add()
        $check.Name = 'AUTO CHECK'
    }

    $check.Cells.Clear()
    $check.Range("A1:D1").Value2 = @('Metric','Source RepDay','Daily Report','Status')
    $check.Range("A2").Value2 = 'Muster Rolls'
    $check.Range("B2").Value2 = $repMR
    $check.Range("C2").Value2 = $dailyMR
    $check.Range("D2").Value2 = $(if ($repMR -eq $dailyMR) {'OK'} else {'MISMATCH'})

    $check.Range("A3").Value2 = 'Works with MR'
    $check.Range("B3").Value2 = $repWorksMR
    $check.Range("C3").Value2 = $dailyWorksMR
    $check.Range("D3").Value2 = $(if ($repWorksMR -eq $dailyWorksMR) {'OK'} else {'MISMATCH'})

    $check.Range("A4").Value2 = 'Unskilled Labour Engagement'
    $check.Range("B4").Value2 = $repEng
    $check.Range("C4").Value2 = $dailyEng
    $check.Range("D4").Value2 = $(if ($repEng -eq $dailyEng) {'OK'} else {'MISMATCH'})

    $check.Range("A6").Value2 = 'Last Auto Refresh'
    $check.Range("B6").Value2 = (Get-Date).ToString('dd-MM-yyyy HH:mm:ss')
    $check.Range("A7").Value2 = 'RepDay Rows'
    $check.Range("B7").Value2 = $lastRep
    $check.Range("A8").Value2 = 'Daily Report Rows'
    $check.Range("B8").Value2 = $lastDaily
    $check.Columns("A:D").AutoFit() | Out-Null

    $wb.Save()

    $stamp = Get-Date -Format 'dd-MM-yyyy'
    $outPath = Join-Path $folder ("Daily_Report_" + $stamp + ".xlsx")
    $wb.SaveCopyAs($outPath)

    $wb.Close($true)

    Write-Host ""
    Write-Host "SUCCESS - Daily Report automatically calculated."
    Write-Host "Muster Rolls: $dailyMR"
    Write-Host "Works with MR: $dailyWorksMR"
    Write-Host "Unskilled Labour Engagement: $dailyEng"
    Write-Host "Output: $outPath"
}
finally {
    if ($excel) {
        $excel.Quit()
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
    }
}
