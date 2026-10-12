# Rejected Wage — verified workflow, 3 October 2026

Report: https://srdmsatna.online/rejected-wage-reconciliation.html

## Protected baseline
22.09.2026 is the fixed VBGRAMG FY 2026–27 baseline in BASELINE in rejected-wage-reconciliation.html. Do not overwrite it with current or previous snapshots. Compare it only with current VBGRAMG source rows, not combined MGNREGA + VBGRAMG totals.

## Sources and output
scripts/update_rejected_wage.py holds the user-provided official source URLs. FY 2024–25 and 2025–26 use MGNREGA. FY 2026–27 adds MGNREGA and VBGRAMG by normalized Janpad. Satna includes Majhgawan, Nagod, Rampur Baghelan, Sohawal (source SATNA), Unchahara. Maihar includes Amarpatan, Maihar, Ramnagar.
Output: data/rejected-wage-latest.json, 24 Janpad/FY rows, raw scheme snapshots retained in sources, fetchedAt in Asia/Kolkata.

## Proven execution method
Government sites were blocked in the assistant browser, but the user's Windows laptop Playwright updater returned HTTP 200. Run on the laptop. A local unresolved rebase exists in the main checkout; do not delete rebase state or reset user work. Use a clean detached worktree based on freshly fetched origin/main. Temporary worktrees are disposable execution locations, not the durable copy.

Run updater in that clean worktree; it validates all four summaries before replacing output. Review SUCCESS: 24 Janpad/FY rows and detail warnings. Stage only data/rejected-wage-latest.json, commit, and push HEAD:main without force. If push is rejected, fetch and reconcile in the clean worktree preserving the newly downloaded JSON. Verify remote JSON date, fetchedAt, 24 rows, per-scheme totals, and push success. Ctrl+F5 refreshes browser cache.

## Detail limitations
Linked pending detail tables supply reasons, unique Muster Roll counts and FTO counts. Missing fields remain null, not zero. Reasons only represent retrieved rows. On 3 October 22:11 update, combined FY 2026–27 coverage was Amarpatan 4/12, Ramnagar 32/65, Rampur Baghelan 151/158; do not claim complete coverage or invent remaining reasons. Other source data may change later.

## Verification
Successful detail publish commit: 08a0f8e. Remote output verified fetchedAt 2026-10-03T22:11:00+05:30. Updater and report code are versioned in GitHub. Do not overwrite other dashboard modules during this workflow.
