from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
start='<!-- ===== SRDM R6.12 VERIFIED COUNTS V1 ===== -->'
end='<!-- ===== END SRDM R6.12 VERIFIED COUNTS V1 ===== -->'
if start in s and end in s:
    a=s.index(start); b=s.index(end,a)+len(end); s=s[:a]+s[b:]

block=r'''
<!-- ===== SRDM R6.12 VERIFIED COUNTS V1 ===== -->
<script>
(function(){
  const VERIFIED_R612={
    'AMARPATAN':       {ongoingAll:1383, pmayOngoing:865,  ekOngoing:109},
    'MAIHAR':          {ongoingAll:2482, pmayOngoing:1512, ekOngoing:86},
    'MAJHGAWAN':       {ongoingAll:2204, pmayOngoing:1255, ekOngoing:85},
    'NAGOD':           {ongoingAll:2311, pmayOngoing:1637, ekOngoing:99},
    'RAMNAGAR':        {ongoingAll:1166, pmayOngoing:910,  ekOngoing:105},
    'RAMPUR BAGHELAN': {ongoingAll:3264, pmayOngoing:2713, ekOngoing:75},
    'SATNA':            {ongoingAll:1048, pmayOngoing:422,  ekOngoing:94},
    'UNCHAHARA':        {ongoingAll:1829, pmayOngoing:1185, ekOngoing:102}
  };
  function applyVerified(){
    if(!Array.isArray(official)) return;
    for(const r of official){
      const j=String(r.janpad||'').trim().toUpperCase();
      const v=VERIFIED_R612[j];
      if(!v) continue;
      r.ongoingAll=v.ongoingAll;
      r.pmayOngoing=v.pmayOngoing;
      r.ekOngoing=v.ekOngoing;
    }
  }
  applyVerified();
  const oldRender=render;
  render=function(){applyVerified(); return oldRender();};
})();
</script>
<!-- ===== END SRDM R6.12 VERIFIED COUNTS V1 ===== -->
'''

if '</body>' not in s: raise SystemExit('index.html has no </body>')
s=s.replace('</body>',block+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('DONE: R6.12 verified counts applied: Ongoing 15,687 | PMAY-G 10,499 | Ek Bagiya Ongoing 755')
