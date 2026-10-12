from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
start='<!-- ===== FIX BACK TO LAUNCHER V1 ===== -->'
end='<!-- ===== END FIX BACK TO LAUNCHER V1 ===== -->'
while start in s and end in s:
    a=s.index(start); b=s.index(end,a)+len(end); s=s[:a]+s[b:]

block=r'''
<!-- ===== FIX BACK TO LAUNCHER V1 ===== -->
<script>
(function(){
  const HOME='/';
  function isBackLauncher(el){
    if(!el) return false;
    const t=String(el.textContent||'').replace(/\s+/g,' ').trim();
    return /वापस जाएँ|वापस जाएं|BACK/i.test(t) && /एसआरडीएम|SRDM|अनुप्रयोग|APPLICATION/i.test(t);
  }
  function fixLinks(){
    document.querySelectorAll('a,button').forEach(el=>{
      if(!isBackLauncher(el)) return;
      el.setAttribute('data-srdm-home-fixed','1');
      if(el.tagName==='A') el.setAttribute('href',HOME);
      el.title='SRDM Applications Home';
    });
  }
  document.addEventListener('click',function(ev){
    const el=ev.target && ev.target.closest ? ev.target.closest('a,button') : null;
    if(!isBackLauncher(el)) return;
    ev.preventDefault();
    ev.stopPropagation();
    if(ev.stopImmediatePropagation) ev.stopImmediatePropagation();
    window.location.assign(HOME);
  },true);
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',fixLinks); else fixLinks();
  setTimeout(fixLinks,500);
  setTimeout(fixLinks,1500);
})();
</script>
<!-- ===== END FIX BACK TO LAUNCHER V1 ===== -->
'''
if '</body>' not in s: raise SystemExit('index.html has no </body>')
s=s.replace('</body>',block+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('DONE: Back-to-SRDM Applications button now always opens site home /')
