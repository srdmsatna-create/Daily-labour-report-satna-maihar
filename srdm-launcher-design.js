/* Local SVGs avoid broken thumbnails and keep every report recognisable. */
(()=>{
const icons={
 report:'<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 8h6M9 12h6M9 16h4"/>',
 payment:'<rect x="2" y="5" width="20" height="14" rx="3"/><path d="M2 10h20M6 15h4"/>',
 chart:'<path d="M4 3v18h17M9 16v-5M14 16V7M19 16v-8"/>',
 water:'<path d="M12 2C10 6 5 11 5 15a7 7 0 0 0 14 0c0-4-5-9-7-13Z"/>',
 road:'<path d="m7 3-4 18M17 3l4 18M12 3v3M12 10v4M12 18v3"/>',
 home:'<path d="m3 10 9-7 9 7M5 9v12h14V9M10 21v-7h4v7"/>',
 map:'<path d="m3 5 6-2 6 2 6-2v16l-6 2-6-2-6 2ZM9 3v16M15 5v16"/>',
 people:'<circle cx="9" cy="7" r="3"/><path d="M3 21v-3a6 6 0 0 1 12 0v3M16 4a3 3 0 0 1 0 6M18 14a5 5 0 0 1 3 4v3"/>',
 alert:'<path d="m12 3 10 18H2ZM12 9v5M12 17h.01"/>',
 clock:'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
 leaf:'<path d="M20 3C8 2 3 7 4 14c1 6 9 9 13 3 3-4 3-9 3-14ZM4 21 15 10"/>'
};
function paint(){document.querySelectorAll('.srdm-app-launcher .srdm-app-card').forEach(card=>{
 const el=card.querySelector('.srdm-app-icon');if(!el||el.dataset.designReady)return;
 const text=(card.querySelector('strong')?.textContent||'').toLowerCase();
 let key='report';
 if(/payment|भुगतान|wage/.test(text))key='payment';
 else if(/e-mb|e-mb|लंबित/.test(text))key='clock';
 else if(/ganga|गंगा|water/.test(text))key='water';
 else if(/rims|संपर्कता/.test(text))key='road';
 else if(/pmay/.test(text))key='home';
 else if(/dysfunctional|problem|निष्क्रिय/.test(text))key='alert';
 else if(/श्रमिक|labour|engineer|उपयंत्री/.test(text))key='people';
 else if(/yukt|master|मास्टर/.test(text))key='map';
 else if(/bagiya|बगिया/.test(text))key='leaf';
 else if(/planner|summary|category|monitoring|व्यय/.test(text))key='chart';
 el.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+icons[key]+'</svg>';
 el.dataset.designReady='true';el.removeAttribute('aria-label');
 });}
paint();new MutationObserver(paint).observe(document.body,{childList:true,subtree:true});
})();
