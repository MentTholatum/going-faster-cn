'use strict';
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
const chapters=[...document.querySelectorAll('.book-chapter')], nav=document.getElementById('navigation'), menu=document.getElementById('menu-button');
let activeChapter=null;
const closeNav=()=>{nav.classList.remove('open');menu.setAttribute('aria-expanded','false')};
menu.onclick=()=>{const open=nav.classList.toggle('open');menu.setAttribute('aria-expanded',String(open))};
function navigate(){
 const id=decodeURIComponent(location.hash.slice(1));let target=id?document.getElementById(id):null;
 const ch=target?.closest('.book-chapter')||document.getElementById('chapter-01');
 if(!ch)return;
 pauseAll();activeChapter=ch;chapters.forEach(c=>c.hidden=c!==ch);
 document.getElementById('current-chapter').textContent=ch.dataset.title;
 document.title=ch.dataset.title+' · Going Faster!';
 nav.querySelectorAll('nav a').forEach(a=>{const on=a.hash==='#'+ch.id;a.classList.toggle('active',on);if(on)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current')});
 closeNav();requestAnimationFrame(()=>{if(target&&target!==ch&&target.closest('.book-chapter')===ch)target.scrollIntoView({behavior:'instant',block:'start'});else scrollTo({top:0,behavior:'instant'});updateProgress()});
}
addEventListener('hashchange',navigate);
nav.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{closeNav();if(a.hash===location.hash)navigate()}));
let fontSize=20;
function setFont(n){fontSize=Math.max(16,Math.min(24,n));document.documentElement.style.setProperty('--reader-size',fontSize+'px');document.getElementById('font-value').textContent=fontSize;document.getElementById('font-minus').disabled=fontSize===16;document.getElementById('font-plus').disabled=fontSize===24;try{localStorage.setItem('going-faster-font',fontSize)}catch{}}
try{const n=Number(localStorage.getItem('going-faster-font'));if(n>=16&&n<=24)setFont(n)}catch{}
document.getElementById('font-minus').onclick=()=>setFont(fontSize-1);document.getElementById('font-plus').onclick=()=>setFont(fontSize+1);
document.getElementById('toggle-supplements').onclick=()=>{pauseAll();const hidden=document.body.classList.toggle('hidden-supplements');const b=document.getElementById('toggle-supplements');b.textContent=hidden?'显示补充说明':'隐藏补充说明';b.setAttribute('aria-pressed',String(hidden))};
function updateProgress(){const max=document.documentElement.scrollHeight-innerHeight;const fraction=Math.max(0,Math.min(1,max?scrollY/max:0));document.querySelector('.progress').style.width=document.querySelector('.workspace').clientWidth*fraction+'px';document.getElementById('rail-progress').style.width=fraction*100+'%';document.getElementById('reading-percent').textContent=Math.round(fraction*100)+'%'}
let queued=false;function queueProgress(){if(!queued){queued=true;requestAnimationFrame(()=>{updateProgress();queued=false})}}addEventListener('scroll',queueProgress,{passive:true});addEventListener('resize',queueProgress);new ResizeObserver(queueProgress).observe(document.querySelector('main'));
const figureDialog=document.getElementById('figure-dialog'), figureScroller=document.getElementById('figure-scroller');let lastFigureFocus=null;
document.querySelectorAll('[data-figure]').forEach(b=>b.addEventListener('click',()=>{pauseAll();lastFigureFocus=b;const img=b.querySelector('img').cloneNode();img.removeAttribute('width');img.removeAttribute('height');img.loading='eager';document.getElementById('figure-image-holder').replaceChildren(img);document.getElementById('figure-dialog-title').textContent=b.dataset.figure.match(/^\d+-\d+$/)?'图 '+b.dataset.figure:'图片';figureScroller.classList.remove('zoomed');const z=document.getElementById('figure-zoom');z.setAttribute('aria-pressed','false');z.textContent='原始尺寸';figureDialog.showModal();figureScroller.scrollTop=0;figureScroller.scrollLeft=0}));
document.getElementById('figure-close').onclick=()=>figureDialog.close();figureDialog.addEventListener('close',()=>lastFigureFocus?.focus());
document.getElementById('figure-zoom').onclick=()=>{const on=figureScroller.classList.toggle('zoomed');figureScroller.querySelector('img').style.width=on?figureScroller.querySelector('img').naturalWidth+'px':'';const b=document.getElementById('figure-zoom');b.setAttribute('aria-pressed',String(on));b.textContent=on?'适合宽度':'原始尺寸'};
const searchDialog=document.getElementById('search-dialog'),searchInput=document.getElementById('book-search'),searchResults=document.getElementById('search-results'),searchSummary=document.getElementById('search-summary');
const searchIndex=[...document.querySelectorAll('[data-search]')].map(e=>({id:e.id,text:e.textContent,chapter:e.closest('.book-chapter').dataset.title}));
document.getElementById('search-open').onclick=()=>{pauseAll();searchDialog.showModal();searchInput.focus()};document.getElementById('search-close').onclick=()=>searchDialog.close();searchDialog.addEventListener('close',()=>document.getElementById('search-open').focus());
function search(){const raw=searchInput.value.trim();const q=raw.toLowerCase();searchResults.replaceChildren();if(!q){searchSummary.textContent='输入文字查找。';return}const found=searchIndex.filter(e=>e.text.toLowerCase().includes(q));searchSummary.textContent=found.length?'找到 '+found.length+' 处'+(found.length>100?'，显示前 100 处。':'。'):'未找到相关内容。';for(const f of found.slice(0,100)){const li=document.createElement('li'),a=document.createElement('a'),small=document.createElement('small');a.href='#'+f.id;small.textContent=f.chapter;a.append(small);const pos=f.text.toLowerCase().indexOf(q),start=Math.max(0,pos-30),end=Math.min(f.text.length,pos+q.length+90);a.append(document.createTextNode((start?'…':'')+f.text.slice(start,pos)));const mark=document.createElement('mark');mark.textContent=f.text.slice(pos,pos+q.length);a.append(mark,document.createTextNode(f.text.slice(pos+q.length,end)+(end<f.text.length?'…':'')));a.onclick=()=>{searchDialog.close();if(location.hash===a.hash)navigate()};li.append(a);searchResults.append(li)}}
searchInput.addEventListener('input',search);
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&nav.classList.contains('open')){closeNav();menu.focus()}});document.addEventListener('click',e=>{if(nav.classList.contains('open')&&!nav.contains(e.target)&&!menu.contains(e.target))closeNav()});
{{DEMO_SCRIPT}}
navigate();
