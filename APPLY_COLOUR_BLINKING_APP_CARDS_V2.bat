@echo off
setlocal EnableExtensions
title SRDM SATNA - Colour Blinking Cards V2
color 0A
cd /d "%~dp0"
if not exist "index.html" (color 0C& echo ERROR: Put this BAT in C:\Users\welcome\Daily-labour-report-satna-maihar& pause& exit /b 1)
copy /y "index.html" "index_before_colour_cards_v2.html" >nul
powershell -NoProfile -ExecutionPolicy Bypass -Command "$p='index.html';$s=[IO.File]::ReadAllText($p);$s=$s.Replace(' new MutationObserver(()=>ensureButton()).observe(document.body,{subtree:true,childList:true});','').Replace(' ensureButton();','');$s=[regex]::Replace($s,'(?s)<!-- SRDM_COLOR_V2_START -->.*?<!-- SRDM_COLOR_V2_END -->','');$c='<!-- SRDM_COLOR_V2_START --><style>.srdm-app-grid .srdm-app-card{position:relative;border:3px solid var(--ac)!important;background:linear-gradient(135deg,var(--bg),#fff 75%%)!important;animation:srdmGlowV2 1.8s ease-in-out infinite;animation-delay:var(--dl);transform-origin:center}.srdm-app-grid .srdm-app-icon{background:var(--ac)!important;color:#fff!important}.srdm-app-grid .srdm-app-card:nth-child(1){--ac:#0866dc;--bg:#e7f1ff;--dl:0s}.srdm-app-grid .srdm-app-card:nth-child(2){--ac:#7b35c8;--bg:#f2eaff;--dl:.15s}.srdm-app-grid .srdm-app-card:nth-child(3){--ac:#09965d;--bg:#e5faef;--dl:.30s}.srdm-app-grid .srdm-app-card:nth-child(4){--ac:#e8750c;--bg:#fff0df;--dl:.45s}.srdm-app-grid .srdm-app-card:nth-child(5){--ac:#d82f56;--bg:#ffeaf0;--dl:.60s}.srdm-app-grid .srdm-app-card:nth-child(6){--ac:#008d9e;--bg:#e2f9fc;--dl:.75s}.srdm-app-grid .srdm-app-card:nth-child(7){--ac:#b58300;--bg:#fff6d7;--dl:.90s}.srdm-app-grid .srdm-app-card:nth-child(8){--ac:#344fc8;--bg:#e9edff;--dl:1.05s}.srdm-app-grid .srdm-app-card:nth-child(9){--ac:#b530ac;--bg:#ffeafb;--dl:1.20s}.srdm-app-grid .srdm-app-card:hover{animation-play-state:paused;transform:translateY(-5px) scale(1.02)!important}.srdm-app-new{animation:srdmNewV2 .8s ease-in-out infinite!important}@keyframes srdmGlowV2{0%%,100%%{box-shadow:0 4px 10px #173f6b18;filter:brightness(1)}50%%{box-shadow:0 0 0 5px color-mix(in srgb,var(--ac) 30%%,transparent),0 14px 30px color-mix(in srgb,var(--ac) 35%%,transparent);filter:brightness(1.1)}}@keyframes srdmNewV2{0%%,100%%{opacity:1}50%%{opacity:.35}}</style><!-- SRDM_COLOR_V2_END -->';$s=$s.Replace('</head>',$c+'</head>');[IO.File]::WriteAllText($p,$s,(New-Object Text.UTF8Encoding($false)))"
if errorlevel 1 (color 0C& echo ERROR: index.html styling failed.& pause& exit /b 2)
findstr /C:"SRDM_COLOR_V2_START" index.html >nul || (color 0C& echo ERROR: Styling verification failed.& pause& exit /b 3)
where git >nul 2>&1 || (echo SUCCESS locally. Git not found.& pause& exit /b 0)
git add -- index.html
git commit -m "Apply colourful blinking application cards V2"
if errorlevel 1 (echo Nothing new to commit.& pause& exit /b 0)
git pull --rebase --autostash
if errorlevel 1 goto :fail
git push
if errorlevel 1 goto :fail
echo SUCCESS - Colour cards V2 published.
echo Wait 1-3 minutes and press Ctrl+Shift+R.
pause
exit /b 0
:fail
color 0C
echo ERROR: Local file changed but GitHub publish failed.
pause
exit /b 4
