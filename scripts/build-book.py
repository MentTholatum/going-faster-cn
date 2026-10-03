"""Build the static reader and portable edition from book data and assets."""
from pathlib import Path
import json,html,re,hashlib,sys,collections,base64,mimetypes
ROOT=Path(__file__).resolve().parents[1]
publish='--publish' in sys.argv
META={0:('序言、前言与导言','Foreword, Preface and Introduction'),1:('制定驾驶策略','A Plan of Attack'),2:('三项基本功：路线、出弯速度与制动','The Three Basics: Line, Corner Exit Speed, Braking'),3:('真实赛道中的行驶路线','The Real-World Line'),4:('掌握车辆控制','Mastering Car Control'),5:('制动与入弯','Braking and Entering'),6:('换挡','Shifting'),7:('学会一条赛道：从地图到实跑','Working Up a Track: From Map to Laps'),8:('寻找圈速','Finding Lap Time'),9:('超车','Passing'),10:('真实的比赛','The Reality of Racing'),11:('事故','Accidents'),12:('雨中赛车','Racing in the Rain'),13:('轮胎','Tires'),14:('底盘调校','Chassis Adjustments'),15:('不同赛车的比较','Comparing Cars'),16:('走进赛车世界','Inside the World of Racing'),17:('附录：赛车资源','Racing Resources'),18:('参考书目','Bibliography'),19:('术语表','Glossary'),20:('图片来源、致谢与作者','Credits, Acknowledgments and About')}
chapters=collections.defaultdict(list)
for d in json.loads((ROOT/'content/book.json').read_text())['chapters']:
 chapters[d['chapter']].extend(d['pages'])
# Move original part title pages to the first chapter in their part.
for source_pdf,dest in {19:1,53:3,119:7,207:13}.items():
 for key in list(chapters):
  found=[p for p in chapters[key] if p['pdf']==source_pdf]
  if found and key!=dest:
   chapters[key]=[p for p in chapters[key] if p['pdf']!=source_pdf];chapters[dest].extend(found);break
assets=json.loads((ROOT/'content/figures.json').read_text())
for ident,a in assets.items():
 assert hashlib.sha256((ROOT/a['path']).read_bytes()).hexdigest()==a['sha256'],ident
all_pages=[p['pdf'] for ps in chapters.values() for p in ps];assert len(all_pages)==len(set(all_pages)),'Duplicate source pages'
figures={f[0]:f[1] for ps in chapters.values() for p in ps for f in p['figures']}
missing_pages=sorted(set(range(21,275))-set(all_pages));missing_figures=sorted(set(figures)-set(assets))
if publish:
 assert not missing_pages,missing_pages
 assert not missing_figures,missing_figures
 assert set(range(1,17))<=set(chapters)
esc=html.escape

def text(s):
 t=esc(str(s));return re.sub(r'图\s*(\d{1,2}-\d{1,2})(?!\d)',lambda m:f'<a class="figure-link" href="#fig-{m[1]}">{m[0]}</a>' if m[1] in figures else m[0],t)

def block(b,ident):
 kind,body=b[:2];attr=f' id="{ident}" data-search'
 if kind in ('h2','h3','h4'):return f'<{kind}{attr}>{text(body)}</{kind}>'
 if kind in ('ul','ol'):return f'<{kind}{attr}>'+''.join(f'<li>{text(v)}</li>' for v in body)+f'</{kind}>'
 if kind=='quote':return f'<blockquote{attr}>'+''.join(f'<p>{text(p)}</p>' for p in str(body).split('\n\n'))+f'<cite>{text(b[2] if len(b)>2 else "")}</cite></blockquote>'
 if kind=='note':return f'<aside class="editor-note" data-supplement{attr}><strong>编校注记</strong><p>{text(body)}</p></aside>'
 if kind=='callout':return f'<p class="source-callout"{attr}>{text(body)}</p>'
 assert isinstance(body,str),(kind,body)
 return f'<p{attr}>{text(body)}</p>'

def figure(f):
 num,caption=f[:2];a=assets.get(num);numbered=bool(re.fullmatch(r'\d+-\d+',num));visual=''
 if a:
  portrait=num.startswith('p') and a['height']>a['width']
  visual=f'<button class="figure-image-button" data-figure="{num}" aria-label="放大{("图 "+num) if numbered else "插图"}"><img src="{esc(a["path"])}" width="{a["width"]}" height="{a["height"]}" loading="lazy" decoding="async" alt="{esc(caption or "插图")}"></button>'
 else:portrait=False
 cap=(f'<span class="figure-number">图 {num}</span>' if numbered else '')+text(caption)
 return f'<figure class="figure-note{" portrait" if portrait else ""}" id="fig-{num}">{visual}'+(f'<figcaption id="caption-{num}" data-search><p>{cap}</p></figcaption>' if cap else '')+'</figure>'

content=[];nav=[];order=sorted(chapters)
for c in order:
 title,en=META[c];label=f'第 {c} 章' if 1<=c<=16 else ('卷首' if c==0 else '附文');cid=f'chapter-{c:02}'
 if c in (0,1,3,7,13,17):nav.append('<p class="nav-group">'+{0:'开始阅读',1:'第一部分 · 基本功',3:'第二部分 · 深化基本功',7:'第三部分 · 锤炼技能与策略',13:'第四部分 · 硬件的作用',17:'附录与参考'}[c]+'</p>')
 nav.append(f'<a href="#{cid}">{c:02}　{esc(title)}</a>' if 1<=c<=16 else f'<a href="#{cid}">{esc(title)}</a>')
 ps=sorted(chapters[c],key=lambda p:p['pdf']);out=[];outline=[]
 for p in ps:
  n=p['pdf'];bs=[]
  for i,b in enumerate(p['blocks']):
   ident=f'p{n}-b{i}'
   if b[0] in ('h2','h3'):outline.append(f'<li><a href="#{ident}">{esc(b[1])}</a></li>')
   bs.append(block(b,ident))
  if n==27:bs.append('<aside class="editor-note" data-supplement><strong>阅读说明</strong><p>本页保留原书 20%／80% 的表述，不据此建立连续的轮胎力计算模型；图内数值按原书具体例子理解。</p></aside>')
  if n==34:bs.append('<aside class="editor-note" data-supplement><strong>编校注记</strong><p>原书正文将转向动作指向图 1-18、踏板转换指向图 1-19，而这两幅图的图题分别说明踏板转换、转向动作。这里保留原图号和原文引用，请结合图题对照。</p></aside>')
  fs=''.join(figure(f) for f in p['figures'])
  demo={23:'exit',24:'grip',28:'brake'}.get(n)
  if bs or fs:out.append(f'<section class="page-section" id="page-{n}" aria-label="第 {esc(str(p.get("print",n-18)))} 页"><article class="translation">'+''.join(bs)+(f'<div class="figure-notes">{fs}</div>' if fs else '')+'</article>'+((ROOT/f'scripts/{demo}_demo.html').read_text() if demo else '')+'</section>')
 hero=f'<div class="hero"><div class="hero-copy"><p class="chapter-label">{label}</p><h1>{esc(title)}</h1><p class="english-title" lang="en">{esc(en)}</p></div></div>'
 toc=f'<details class="chapter-outline"><summary>本章小节</summary><ul>{"".join(outline)}</ul></details>' if outline else ''
 i=order.index(c);turn=[]
 if i:pc=order[i-1];turn.append(f'<a href="#chapter-{pc:02}"><small>← 上一章</small>{esc(META[pc][0])}</a>')
 if i+1<len(order):nc=order[i+1];turn.append(f'<a href="#chapter-{nc:02}"><small>下一章 →</small>{esc(META[nc][0])}</a>')
 content.append(f'<section class="book-chapter" id="{cid}" data-title="{esc(label+" · "+title)}">{hero}{toc}'+''.join(out)+f'<nav class="chapter-turn" aria-label="翻章">{"".join(turn)}</nav></section>')
demojs=(ROOT/'scripts/reading-demos.js').read_text()
script=(ROOT/'scripts/book-reader.js').read_text().replace('{{DEMO_SCRIPT}}',demojs)
styles=(ROOT/'scripts/reader.css').read_text()+'\n'+(ROOT/'scripts/book-reader.css').read_text()
font_manifest=json.loads((ROOT/'assets/reader-fonts/manifest.json').read_text())
for font_asset in font_manifest['files']:
 assert hashlib.sha256((ROOT/font_asset['path']).read_bytes()).hexdigest()==font_asset['sha256'],font_asset['path']
font_paths=[a['path'] for a in font_manifest['files'] if a['path'].endswith('.woff2')]
font_license=(ROOT/'assets/reader-fonts/MiSans-LICENSE.txt').read_text()
output=(ROOT/'scripts/book-reader.html').read_text().replace('{{CONTENT}}','\n'.join(content)).replace('{{NAV}}',''.join(nav)).replace('{{STYLES}}',styles).replace('{{SCRIPT}}',script).replace('{{STATS}}',f'{len([c for c in chapters if 1<=c<=16])} 章').replace('{{FONT_LICENSE}}',esc(font_license))
assert '{{' not in output
outpath=ROOT/('index.html' if publish else 'book-preview.html');outpath.write_text(output)
manifest={'chapters':len(chapters),'pages':len(all_pages),'figures':len(figures),'html':outpath.name,'html_bytes':len(output.encode()),'external_network_dependencies':[]}
if publish:
 portable=output
 for path in font_paths:
  assert "url('"+path+"')" in portable,path
  portable=portable.replace("url('"+path+"')","url('data:font/woff2;base64,"+base64.b64encode((ROOT/path).read_bytes()).decode()+"')")
 for ident in figures:
  path=assets[ident]['path']
  mime=mimetypes.guess_type(path)[0];assert mime in ('image/png','image/jpeg')
  portable=portable.replace('src="'+path+'"','src="data:'+mime+';base64,'+base64.b64encode((ROOT/path).read_bytes()).decode()+'"')
 portable_path=ROOT/'Going-Faster-全书中文阅读版.html'
 portable_path.write_text(portable)
 manifest['portable_html']=portable_path.name
 manifest['portable_html_bytes']=portable_path.stat().st_size
manifest.update(reader_font=font_manifest['family'],reader_font_files=font_paths,default_reader_size=20,reader_line_height=1.6,portable_fonts_embedded=publish)
report_dir=ROOT/'output';report_dir.mkdir(exist_ok=True)
(report_dir/'build-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print(f'Built {outpath.name}: {len(all_pages)} source pages, {len(figures)} figures; missing {len(missing_pages)} body pages / {len(missing_figures)} figures; {len(output.encode())/1024:.0f} KiB')
