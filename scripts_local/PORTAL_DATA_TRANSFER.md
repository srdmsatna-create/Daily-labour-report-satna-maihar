# Government portal to SRDM website

The collector reads official reports, validates each complete report group, and commits the generated dashboard data. GitHub Pages then publishes the committed data. A browser-only cross-origin fetch is not the data pipeline.

The GitHub-hosted run on 9 October 2026 returned HTTP 401 from vbgramgrep.dord.gov.in. Changing dashboard JavaScript cannot grant source access. An accessible computer/server or a source-approved API/session is required.

## Existing Windows collection

SRDM_FINAL_8AM.bat already installs an 08:00 India Windows task and fetches the latest collector before each run. Keep it inside the Git repository and keep the computer connected when collecting. Git must be authenticated for publication. Source session cookies, when explicitly configured in VBGRAM_COOKIE, are used by the HTTP collector and Yuktdhara browser drill-down. Do not put cookie values in committed files.

## Server collection without the laptop

On a Linux computer/server where the official source opens, register a GitHub self-hosted runner from repository Settings > Actions > Runners. Give it the custom label srdm-portal. In Settings > Secrets and variables > Actions > Variables, set SRDM_RUNNER_LABELS to:

```
["self-hosted","linux","srdm-portal"]
```

The complete daily workflow keeps its 08:00 India schedule and will run on that machine. The runner must have working GitHub and official-portal connectivity. Configure required source URLs/session as repository secrets only when needed. Until this runner is registered and the variable is set, the default remains ubuntu-latest. This configuration alone does not bypass a 401 or guarantee source access.

Run the Complete SRDM daily reports workflow manually to verify. Success must include completed validation and a data commit; a successful Pages build alone does not prove fresh source data. A failed run keeps previously published reports and uploads failure JSON plus the diagnostic ZIP.
