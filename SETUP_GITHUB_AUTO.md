# srdmsatna.online — One-time GitHub setup

यह package GitHub Pages पर **automatic daily report** के लिए तैयार है। रोज़ Excel upload नहीं करना है।

## One-time deployment
1. इस ZIP की files अपने `srdmsatna.online` GitHub Pages repository की root में replace/upload करें.
2. GitHub → **Actions** में `VB-G RAM G Daily Auto Report` workflow enable करें.
3. पहली बार **Run workflow** दबाएँ.
4. सफल run के बाद `auto-data.js` bot द्वारा update होगा और site अपने-आप नया data दिखाएगी.

## Official source access
Script पहले official Home/MIS/Ongoing URLs real Chromium browser में खोलता है और Excel/Export control खोजता है।

अगर official site session/login माँगती है तो Repository → Settings → Secrets and variables → Actions में केवल आवश्यक secret जोड़ें:
- `VBGRAM_DAILY_REPORT_URL` — अगर आपके पास direct Daily Report page/export URL है.
- `VBGRAM_COOKIE` — session cookie, अगर report browser session पर निर्भर है.
- `VBGRAM_USERNAME`, `VBGRAM_PASSWORD` — केवल तभी जब official login credentials से automatic login आवश्यक हो.

Secrets website code में expose नहीं होते; वे केवल GitHub Action runner में रहते हैं.

## Safety
- `Muster Rolls = 0`, `Works with MR = 0`, invalid GP total आदि होने पर नया data publish नहीं होगा.
- ऐसी स्थिति में पिछला valid report live रहेगा.
- `data/fetch-status.json` और website status line में fetch result दिखेगा.

## Schedule
IST 06:15, 09:15, 12:15, 15:15, 18:15, 21:15 पर automatic refresh; Actions से कभी भी manual Run भी कर सकते हैं.


## V35 Git Push Fix
If GitHub Action showed `main -> main (fetch first)`, the remote `main` branch changed after the runner checked it out.
V35 fixes this by:
- checkout with full history (`fetch-depth: 0`)
- syncing to `origin/main` before report generation
- rebasing again immediately before push
- retrying push up to 4 times if `main` changes during the run

Schedule remains only 07:00 AM and 08:00 AM IST.
