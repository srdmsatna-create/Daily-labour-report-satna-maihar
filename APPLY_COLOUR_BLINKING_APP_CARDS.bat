@echo off
setlocal EnableExtensions
title SRDM SATNA - Colour Blinking Application Cards
color 0A
cd /d "%~dp0"
if not exist "index.html" (color 0C& echo ERROR: Put this BAT in the dashboard project folder.& pause& exit /b 1)

copy /y "index.html" "index_before_colour_blink_cards.html" >nul
powershell -NoProfile -ExecutionPolicy Bypass -Command "$p='index.html';$s=[IO.File]::ReadAllText($p);$s=$s.Replace(' new MutationObserver(()=>ensureButton()).observe(document.body,{subtree:true,childList:true});','').Replace(' ensureButton();','');$s=[regex]::Replace($s,'(?s)<!-- SRDM_APP_COLOUR_BLINK_START -->.*?<!-- SRDM_APP_COLOUR_BLINK_END -->','');$css=@'
<!-- SRDM_APP_COLOUR_BLINK_START -->
<style>
.srdm-app-grid .srdm-app-card{position:relative;overflow:hidden;border:2px solid var(--app-accent,#1464d2)!important;background:linear-gradient(135deg,var(--app-soft,#eef5ff),#fff 72%)!important;animation:srdmAppGlow 2.2s ease-in-out infinite;animation-delay:var(--app-delay,0s);transform-origin:center;}
.srdm-app-grid .srdm-app-card .srdm-app-icon{background:var(--app-accent,#1464d2)!important;color:#fff!important;box-shadow:0 7px 18px var(--app-shadow,#1464d244)!important;}
.srdm-app-grid .srdm-app-card:nth-child(1){--app-accent:#0b63db;--app-soft:#eaf3ff;--app-shadow:#0b63db55;--app-delay:0s}
.srdm-app-grid .srdm-app-card:nth-child(2){--app-accent:#7b3fc6;--app-soft:#f4edff;--app-shadow:#7b3fc655;--app-delay:.18s}
.srdm-app-grid .srdm-app-card:nth-child(3){--app-accent:#15905a;--app-soft:#e9fbf2;--app-shadow:#15905a55;--app-delay:.36s}
.srdm-app-grid .srdm-app-card:nth-child(4){--app-accent:#e07816;--app-soft:#fff3e6;--app-shadow:#e0781655;--app-delay:.54s}
.srdm-app-grid .srdm-app-card:nth-child(5){--app-accent:#d22e52;--app-soft:#fff0f4;--app-shadow:#d22e5255;--app-delay:.72s}
.srdm-app-grid .srdm-app-card:nth-child(6){--app-accent:#008b9a;--app-soft:#e8fbfd;--app-shadow:#008b9a55;--app-delay:.90s}
.srdm-app-grid .srdm-app-card:nth-child(7){--app-accent:#b8860b;--app-soft:#fff9df;--app-shadow:#b8860b55;--app-delay:1.08s}
.srdm-app-grid .srdm-app-card:nth-child(8){--app-accent:#3956c6;--app-soft:#edf0ff;--app-shadow:#3956c655;--app-delay:1.26s}
.srdm-app-grid .srdm-app-card:nth-child(9){--app-accent:#b83bb1;--app-soft:#fff0fe;--app-shadow:#b83bb155;--app-delay:1.44s}
.srdm-app-grid .srdm-app-card:hover{animation-play-state:paused;transform:translateY(-4px) scale(1.015)!important;box-shadow:0 14px 30px var(--app-shadow)!important;}
.srdm-app-grid .srdm-app-new{animation:srdmNewBlink 1.05s ease-in-out infinite!important;}
@keyframes srdmAppGlow{0%,100%{box-shadow:0 4px 12px #173f6b14;filter:brightness(1)}50%{box-shadow:0 0 0 4px var(--app-shadow),0 12px 26px var(--app-shadow);filter:brightness(1.06)}}
@keyframes srdmNewBlink{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.48;transform:scale(.92)}}
@media(prefers-reduced-motion:reduce){.srdm-app-grid .srdm-app-card,.srdm-app-grid .srdm-app-new{animation:none!important}}
</style>
<!-- SRDM_APP_COLOUR_BLINK_END -->
'@;$s=$s.Replace('</head>',$css+[Environment]::NewLine+'</head>');[IO.File]::WriteAllText($p,$s,(New-Object Text.UTF8Encoding($false)))"
if errorlevel 1 (color 0C& echo ERROR: Card styling could not be applied.& pause& exit /b 2)

where git >nul 2>&1 || (echo SUCCESS - colourful blinking cards applied locally.& pause& exit /b 0)
git add -- index.html
git commit -m "Add distinct colour pulse to application cards"
if errorlevel 1 (echo Nothing new to commit.& pause& exit /b 0)
git pull --rebase --autostash
if errorlevel 1 goto :fail
git push
if errorlevel 1 goto :fail
echo SUCCESS - colourful blinking cards published.
echo Wait 1-3 minutes, then press Ctrl+Shift+R.
pause
exit /b 0
:fail
color 0C
echo ERROR: Styling applied locally, but GitHub publish failed.
pause
exit /b 3
