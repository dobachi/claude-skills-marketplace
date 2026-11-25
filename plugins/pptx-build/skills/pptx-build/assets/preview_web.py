#!/usr/bin/env python3
"""preview_web.py — write a browser preview (PC or phone) index.html for slide JPEGs.

Reads  OUT_DIR/img/s-*.jpg  (one JPEG per slide, in order; preview_web.sh makes them)
and writes  OUT_DIR/index.html : one column of slides, each with "p.N" and its title,
a sticky header with section chips, a page-number jump box, the current page, and
`#pN` links (`index.html#p12` opens slide 12), keys on a PC (j/→ next, k/← previous,
g the page box, +/- zoom), zoom buttons (below 100% the slides flow into columns), a
full-window lightbox on tap with its own zoom and pan, light and dark. Self-contained:
inline CSS/JS, no external requests.

Titles, page labels and sections come from the spec when given (`slides[].title`,
`type: section`, `type: title`), otherwise from the .pptx itself (title placeholder,
section-like layout names). The deck is never hard-coded.

With --comments each slide also gets a review bar (status buttons and a comment box), the
header a filter, a counter and an Export button; comments go to the Claude Artifact `db`
(collection "reviews") when the page is published with it, else to this browser's
localStorage. See preview_review.py and references/web-preview.md.

Usage:
  preview_web.py OUT_DIR (--spec deck.yaml | --pptx deck.pptx) [--title T] [--subtitle S]
                   [--lang auto|ja|en] [--rev TEXT] [--comments [--review-labels "OK,要修正,質問"]]

Exit: 0 written / 1 image count does not match the slide count / 2 usage or input error.
"""
import argparse
import glob
import html
import os
import re
import subprocess
import sys

SECTION_WORDS = ("section", "セクション", "中扉", "章扉", "扉")
TITLE_WORDS = ("title slide", "タイトル スライド", "タイトルスライド", "表紙")

LABELS = {
    "ja": {"cover": "表紙", "go": "移動", "page": "ページ番号", "count": "{n} 枚", "lang": "ja",
           "keys": "j/→ 次 ・ k/← 前 ・ g ページ番号 ・ +/− 拡大縮小",
           "zin": "拡大", "zout": "縮小", "zreset": "標準の大きさに戻す", "zoom": "表示の大きさ",
           "lbopen": "大きく表示", "close": "閉じる", "prev": "前", "next": "次"},
    "en": {"cover": "Cover", "go": "Go", "page": "Page number", "count": "{n} slides", "lang": "en",
           "keys": "j/→ next · k/← previous · g page box · +/− zoom",
           "zin": "Zoom in", "zout": "Zoom out", "zreset": "Back to normal size", "zoom": "Slide size",
           "lbopen": "Open large", "close": "Close", "prev": "Previous", "next": "Next"},
}


def die(code, msg):
    print(f"preview_web: {msg}", file=sys.stderr)
    sys.exit(code)


def one_line(s):
    return " ".join(str(s or "").split())


def from_spec(path):
    try:
        import yaml
    except ImportError:
        die(2, "PyYAML is needed to read the spec (pip install -r requirements.txt)")
    try:
        with open(path, encoding="utf-8") as f:
            if path.endswith(".json"):
                import json
                doc = json.load(f)
            else:
                doc = yaml.safe_load(f)
    except (OSError, ValueError, yaml.YAMLError) as e:
        die(2, f"cannot read spec {path}: {e}")
    if not isinstance(doc, dict) or not isinstance(doc.get("slides"), list):
        die(2, f"{path} has no `slides:` list")
    meta = doc.get("meta") or {}
    slides, title, subtitle = [], "", ""
    for s in doc["slides"]:
        s = s if isinstance(s, dict) else {}
        if s.get("hidden"):
            continue
        kind = s.get("type", "")
        slides.append({"title": one_line(s.get("title")), "id": one_line(s.get("id")),
                       "section": kind == "section", "cover": kind == "title"})
        if kind == "title" and not title:
            title = one_line(s.get("title"))
            subtitle = one_line(s.get("date") or meta.get("date") or s.get("subtitle"))
    return slides, title or one_line(meta.get("title")), subtitle


def from_pptx(path):
    try:
        from pptx import Presentation
        from pptx.enum.shapes import PP_PLACEHOLDER
    except ImportError:
        die(2, "python-pptx is needed to read the deck (pip install -r requirements.txt)")
    try:
        prs = Presentation(path)
    except Exception as e:  # python-pptx raises several types for a non-deck file
        die(2, f"cannot read {path} as a .pptx: {e}")
    title_types = (PP_PLACEHOLDER.TITLE, PP_PLACEHOLDER.CENTER_TITLE)
    slides = []
    for sl in prs.slides:
        if sl.element.get("show") == "0":  # hidden slides are not exported to PDF
            continue
        layout = (sl.slide_layout.name or "").lower()
        t = ""
        for ph in sl.placeholders:
            if ph.placeholder_format.type in title_types and ph.has_text_frame:
                t = one_line(ph.text_frame.text)
                break
        if not t:  # no title placeholder: the first non-empty text on the slide
            for sh in sl.shapes:
                if sh.has_text_frame and sh.text_frame.text.strip():
                    t = one_line(sh.text_frame.text)[:80]
                    break
        slides.append({"title": t,
                       "section": any(w in layout for w in SECTION_WORDS),
                       "cover": any(w in layout for w in TITLE_WORDS)})
    # The cover's title (a cover layout, else slide 1) beats core_properties.title, which is
    # often an app default ("PowerPoint Presentation") nobody set.
    cover = next((s["title"] for s in slides if s["cover"] and s["title"]), "")
    title = cover or (slides[0]["title"] if slides else "") or one_line(prs.core_properties.title)
    return slides, title, ""


def jpeg_size(path):
    """(width, height) from the JPEG's SOF marker; (0, 0) if not found."""
    with open(path, "rb") as f:
        data = f.read(1 << 16)
    i = 2
    while i + 9 < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        m = data[i + 1]
        if m in (0xC0, 0xC1, 0xC2):
            return int.from_bytes(data[i + 7:i + 9], "big"), int.from_bytes(data[i + 5:i + 7], "big")
        i += 2 + int.from_bytes(data[i + 2:i + 4], "big")
    return 0, 0


def git_rev(where):
    try:
        r = subprocess.run(["git", "-C", where, "log", "-1", "--format=%h %cd",
                            "--date=format:%Y-%m-%d %H:%M"], capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else ""
    except OSError:
        return ""


CSS = """
:root { --bg:#f3f4f6; --fg:#16202e; --muted:#5b6575; --line:#d5d9e0; --accent:#0b5cad; --card:#ffffff;
  --sans:"Noto Sans JP","Hiragino Sans",system-ui,sans-serif; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg:#11161d; --fg:#e6eaf0; --muted:#9aa4b2; --line:#2a323d; --accent:#6aa9ec; --card:#1a212b; color-scheme:dark } }
:root[data-theme="dark"] { --bg:#11161d; --fg:#e6eaf0; --muted:#9aa4b2; --line:#2a323d; --accent:#6aa9ec; --card:#1a212b; color-scheme:dark }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--fg); font-family:var(--sans); -webkit-text-size-adjust:100%; }
body::before { content:""; position:fixed; inset:0 0 auto; height:env(safe-area-inset-top,0px); z-index:10; background:var(--card); }
header { position:sticky; top:env(safe-area-inset-top,0px); z-index:5; background:var(--card); border-bottom:1px solid var(--line);
  padding-block:8px; padding-left:max(16px,env(safe-area-inset-left,0px),calc((100% - 1068px) / 2)); padding-right:max(16px,env(safe-area-inset-right,0px),calc((100% - 1068px) / 2)); }
header h1 { margin:0 0 2px; font-size:15px; line-height:1.3; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
header p { margin:0; font-size:12px; color:var(--muted); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.bar { display:flex; align-items:center; gap:8px; margin:0 0 6px; }
.bar .meta { flex:1; min-width:0; }
nav { display:flex; gap:6px; overflow-x:auto; padding-bottom:2px; }
nav a { flex:none; font-size:12px; color:var(--accent); text-decoration:none; border:1px solid var(--line); border-radius:999px; padding:3px 10px; white-space:nowrap; }
#go { display:flex; gap:4px; align-items:center; flex:none; margin:0; }
#go input { width:64px; font:inherit; font-size:16px; padding:3px 6px; border:1px solid var(--line); border-radius:6px; background:var(--bg); color:var(--fg); }
#go button { font:inherit; font-size:13px; padding:4px 10px; border:1px solid var(--accent); border-radius:6px; background:var(--accent); color:#fff; }
#keys { display:none; font-size:11px; color:var(--muted); flex:none; white-space:nowrap; }
@media (min-width:900px) { #keys { display:inline; } }
#cur { font-size:12px; color:var(--muted); font-variant-numeric:tabular-nums; flex:none; }
main { display:grid; gap:20px; max-width:1100px; margin:0 auto; padding-block:16px 48px;
  padding-left:max(16px,env(safe-area-inset-left,0px)); padding-right:max(16px,env(safe-area-inset-right,0px)); }
figure { margin:0; scroll-margin-top:110px; min-width:0; }
figcaption { font-size:13px; color:var(--muted); margin-bottom:6px; }
figcaption .n { font-variant-numeric:tabular-nums; font-weight:700; color:var(--fg); margin-right:4px; }
figure.sec figcaption .n { color:var(--accent); }
img { display:block; width:100%; height:auto; border:1px solid var(--line); background:#fff; }
main > figure > img { cursor:zoom-in; }
/* Column zoom: below 100% the slides flow into several columns across the whole window (an
   overview); above it the column widens up to the window. */
main { --z:1; grid-template-columns:repeat(auto-fill,minmax(min(100%,calc(1068px * var(--z))),1fr)); }
main.zs { max-width:none; }
main.zl { max-width:calc(1100px * var(--z)); }
#zm { display:flex; gap:2px; align-items:center; flex:none; }
#zm button { font:inherit; font-size:13px; min-width:30px; padding:3px 6px; border:1px solid var(--line); border-radius:6px; background:var(--bg); color:var(--fg); cursor:pointer; }
#zm #zp { min-width:52px; font-variant-numeric:tabular-nums; }
/* Lightbox: one slide over the whole window, zoomable and pannable. */
#lb { width:100vw; height:100vh; max-width:none; max-height:none; margin:0; padding:0; border:0; background:rgba(10,12,16,.95); color:#e6eaf0; overflow:hidden; }
#lb::backdrop { background:rgba(0,0,0,.6); }
#lbb { position:absolute; inset:0 0 auto; height:44px; display:flex; gap:6px; align-items:center; padding:0 max(12px,env(safe-area-inset-right,0px)) 0 max(12px,env(safe-area-inset-left,0px)); background:rgba(0,0,0,.4); }
#lbt { flex:1; min-width:0; font-size:13px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
#lbb button { font:inherit; font-size:13px; min-width:34px; padding:4px 8px; border:1px solid #4a5462; border-radius:6px; background:#1a212b; color:#e6eaf0; cursor:pointer; }
#lbb #lbp { min-width:56px; font-variant-numeric:tabular-nums; }
#lbv { position:absolute; inset:44px 0 0; overflow:auto; display:flex; overscroll-behavior:contain; cursor:grab; }
#lbv.drag { cursor:grabbing; }
#lbv img { margin:auto; flex:none; max-width:none; width:auto; border:0; cursor:inherit; user-select:none; -webkit-user-drag:none; }
"""

JS = """
(function(){
  var N=%d;
  var want=0;  // last jump target: near the end the page cannot scroll that slide to the top
  function go(n){ n=Math.max(1,Math.min(N,parseInt(n,10)||0)); if(!n) return; want=n;
    var el=document.getElementById('s'+n); if(el){ var hb=document.querySelector('header').getBoundingClientRect().bottom;
      window.scrollTo(0, el.getBoundingClientRect().top+scrollY-hb-8); try{history.replaceState(null,'','#p'+n);}catch(e){} } }
  document.getElementById('go').addEventListener('submit',function(e){ e.preventDefault(); var i=document.getElementById('pn'); go(i.value); i.blur(); });
  document.getElementById('pn').addEventListener('keydown',function(e){ if(e.key==='Escape') this.blur(); });
  document.querySelector('nav').addEventListener('click',function(e){ var a=e.target.closest('a'); if(!a) return; e.preventDefault(); go(a.getAttribute('href').slice(2)); });
  function fromHash(){ var m=location.hash.match(/^#(?:p|s)(\\d+)$/); if(m) go(m[1]); }
  window.addEventListener('hashchange',fromHash);
  if(document.readyState==='complete') fromHash(); else window.addEventListener('load',fromHash);
  // Current page = the slide whose caption sits just under the sticky header, i.e. the one a
  // reviewer is reading at the top of the screen (they quote it as "pN" in comments).
  var cur=document.getElementById('cur'), head=document.querySelector('header'),
      figs=document.querySelectorAll('main figure'), busy=false, now=1;
  function mark(){ busy=false; var edge=head.getBoundingClientRect().bottom+24, k=1;
    for(var i=0;i<figs.length;i++){ if(figs[i].getBoundingClientRect().top<=edge) k=i+1; else break; }
    if(want>k && innerHeight+scrollY>=document.documentElement.scrollHeight-4) k=want;
    now=k; cur.textContent='p.'+k+' / '+N; }
  window.addEventListener('scroll',function(){ if(!busy){ busy=true; requestAnimationFrame(mark); } },{passive:true});
  window.addEventListener('resize',mark); mark();
  window.__pv={go:go, now:function(){ return now; }};
  // Keys on a PC. Ignored while typing in a field and with a modifier held, so the page box,
  // browser shortcuts and screen readers keep their keys.
  document.addEventListener('keydown',function(e){
    if(e.ctrlKey||e.metaKey||e.altKey||e.isComposing) return;
    if(document.getElementById('lb').open) return;  // the lightbox has its own keys
    var t=e.target; if(t&&(t.tagName==='INPUT'||t.tagName==='TEXTAREA'||t.tagName==='SELECT'||t.isContentEditable)) return;
    if(e.key==='j'||e.key==='ArrowRight'){ e.preventDefault(); go(now+1); }
    else if(e.key==='k'||e.key==='ArrowLeft'){ e.preventDefault(); go(now-1); }
    else if(e.key==='g'){ e.preventDefault(); var i=document.getElementById('pn'); i.focus(); i.select(); }
  });
})();
"""


ZOOM_JS = """
(function(){
  // Column zoom (header buttons, + / - / 0 keys); the level is kept per browser when allowed.
  var Z=[0.34,0.5,0.67,0.8,1,1.25,1.5,2], m=document.querySelector('main'), zp=document.getElementById('zp'), zi=4;
  function setZ(i,keep){ var p=window.__pv.now(); zi=Math.max(0,Math.min(Z.length-1,i)); var z=Z[zi];
    m.style.setProperty('--z',z); m.classList.toggle('zs',z<1); m.classList.toggle('zl',z>1);
    zp.textContent=Math.round(z*100)+'%';
    try{ localStorage.setItem('pv-zoom',String(z)); }catch(e){}
    if(keep) window.__pv.go(p); }
  try{ var v=parseFloat(localStorage.getItem('pv-zoom')); if(Z.indexOf(v)>=0) setZ(Z.indexOf(v),false); }catch(e){}
  document.getElementById('zm').addEventListener('click',function(e){ var b=e.target.closest('button'); if(!b) return;
    setZ(b.id==='zp'?4:zi+parseInt(b.getAttribute('data-d'),10),true); });
  // Lightbox: tap a slide to open it over the whole window.
  var lb=document.getElementById('lb'), lv=document.getElementById('lbv'), li=lv.querySelector('img'),
      lt=document.getElementById('lbt'), lp=document.getElementById('lbp'), L=[1,1.5,2,3,4], li_=0, cur=0;
  function figs(){ return Array.prototype.filter.call(document.querySelectorAll('main > figure'),function(f){ return !f.hidden; }); }
  function fit(){ var w=lv.clientWidth, h=lv.clientHeight, r=(li.naturalWidth||16)/(li.naturalHeight||9); return Math.min(w,h*r); }
  function setL(i,cx,cy){ var old=li.getBoundingClientRect().width||1; li_=Math.max(0,Math.min(L.length-1,i));
    if(cx==null){ cx=lv.clientWidth/2; cy=lv.clientHeight/2; }
    var ax=(lv.scrollLeft+cx)/old, ay=(lv.scrollTop+cy)/old, w=fit()*L[li_];
    li.style.width=w+'px'; lp.textContent=Math.round(L[li_]*100)+'%';
    lv.scrollLeft=ax*w-cx; lv.scrollTop=ay*w-cy; }
  function show(n){ var f=document.getElementById('s'+n); if(!f) return; cur=n; var im=f.querySelector('img');
    li.onload=function(){ setL(0); }; li.src=im.getAttribute('src'); li.alt=im.alt;
    lt.textContent=f.querySelector('figcaption').textContent; if(li.complete&&li.naturalWidth) setL(0); }
  function move(d){ var fs=figs(), i=fs.indexOf(document.getElementById('s'+cur)); var f=fs[i+d]; if(f) show(parseInt(f.id.slice(1),10)); }
  function close(){ lb.close(); }
  lb.addEventListener('close',function(){ window.__pv.go(cur); });
  m.addEventListener('click',function(e){ var im=e.target.closest('main > figure > img'); if(!im||!lb.showModal) return;
    show(parseInt(im.parentNode.id.slice(1),10)); lb.showModal(); });
  document.getElementById('lbb').addEventListener('click',function(e){ var b=e.target.closest('button'); if(!b) return;
    if(b.id==='lbx') close(); else if(b.id==='lbp') setL(0); else if(b.hasAttribute('data-m')) move(parseInt(b.getAttribute('data-m'),10));
    else setL(li_+parseInt(b.getAttribute('data-d'),10)); });
  lv.addEventListener('wheel',function(e){ if(!(e.ctrlKey||e.metaKey)) return; e.preventDefault();
    var r=lv.getBoundingClientRect(); setL(li_+(e.deltaY<0?1:-1),e.clientX-r.left,e.clientY-r.top); },{passive:false});
  lv.addEventListener('dblclick',function(e){ var r=lv.getBoundingClientRect(); setL(li_?0:2,e.clientX-r.left,e.clientY-r.top); });
  var dr=null;  // drag to pan with a mouse; touch scrolls natively
  lv.addEventListener('pointerdown',function(e){ if(e.pointerType!=='mouse'||e.button) return; dr={x:e.clientX,y:e.clientY,l:lv.scrollLeft,t:lv.scrollTop}; lv.classList.add('drag'); e.preventDefault(); });
  window.addEventListener('pointermove',function(e){ if(!dr) return; lv.scrollLeft=dr.l-(e.clientX-dr.x); lv.scrollTop=dr.t-(e.clientY-dr.y); });
  window.addEventListener('pointerup',function(){ dr=null; lv.classList.remove('drag'); });
  window.addEventListener('resize',function(){ if(lb.open) setL(li_); });
  document.addEventListener('keydown',function(e){
    if(e.ctrlKey||e.metaKey||e.altKey||e.isComposing) return;
    var t=e.target; if(t&&(t.tagName==='INPUT'||t.tagName==='TEXTAREA'||t.tagName==='SELECT'||t.isContentEditable)) return;
    var k=e.key, d=(k==='+'||k==='=')?1:(k==='-'||k==='_')?-1:0;
    if(lb.open){
      if(d){ e.preventDefault(); setL(li_+d); } else if(k==='0'){ e.preventDefault(); setL(0); }
      else if(k==='j'||k==='ArrowRight'){ e.preventDefault(); move(1); } else if(k==='k'||k==='ArrowLeft'){ e.preventDefault(); move(-1); }
      return; }
    if(document.querySelector('dialog[open]')) return;
    if(d){ e.preventDefault(); setZ(zi+d,true); } else if(k==='0'){ e.preventDefault(); setZ(4,true); }
  });
})();
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("out_dir", help="folder holding img/s-*.jpg; index.html is written here")
    ap.add_argument("--spec", help="deck spec (YAML/JSON) — labels and sections come from it")
    ap.add_argument("--pptx", help="the deck — labels and sections come from it when no --spec")
    ap.add_argument("--title", help="page title (default: the title slide's title)")
    ap.add_argument("--subtitle", help="line under the title (default: the title slide's date)")
    ap.add_argument("--lang", choices=("auto", "ja", "en"), default="auto",
                    help="UI words (default: ja if the titles contain Japanese)")
    ap.add_argument("--rev", help="revision text in the header (default: git log of the input's folder)")
    ap.add_argument("--comments", action="store_true",
                    help="add a review bar per slide (status + comment), a filter and Export")
    ap.add_argument("--review-labels",
                    help='status buttons, comma-separated (default: "OK,要修正,質問" / "OK,Fix,Question")')
    a = ap.parse_args()
    if a.review_labels is not None and not a.comments:
        die(2, "--review-labels only applies with --comments")

    if not os.path.isdir(a.out_dir):
        die(2, f"no such folder: {a.out_dir}")
    if a.spec:
        if not os.path.isfile(a.spec):
            die(2, f"no such spec: {a.spec}")
        slides, title, subtitle = from_spec(a.spec)
    elif a.pptx:
        if not os.path.isfile(a.pptx):
            die(2, f"no such deck: {a.pptx}")
        slides, title, subtitle = from_pptx(a.pptx)
    else:
        die(2, "give --spec deck.yaml or --pptx deck.pptx (labels come from one of them)")

    imgs = sorted(glob.glob(os.path.join(a.out_dir, "img", "s-*.jpg")))
    if not imgs:
        die(2, f"no images in {a.out_dir}/img (expected s-*.jpg; run preview_web.sh)")
    if len(imgs) != len(slides):
        die(1, f"{len(imgs)} image(s) in {a.out_dir}/img but {len(slides)} slide(s) in "
               f"{a.spec or a.pptx}. The rendered deck and the label source disagree: rebuild the "
               f".pptx from this spec, or re-run preview_web.sh so img/ holds exactly this deck's pages.")

    title = a.title if a.title is not None else (title or "Slides")
    subtitle = a.subtitle if a.subtitle is not None else subtitle
    lang = a.lang
    if lang == "auto":
        text = title + "".join(s["title"] for s in slides)
        lang = "ja" if re.search(r"[぀-ヿ一-鿿]", text) else "en"
    L = LABELS[lang]
    rev = a.rev if a.rev is not None else git_rev(os.path.dirname(os.path.abspath(a.spec or a.pptx)))
    n = len(slides)
    js, rv_css, rv_head, rv_tail, keys = JS % n, "", "", "", [""] * n
    if a.comments:
        import preview_review as rv
        try:
            labels = rv.parse_labels(a.review_labels, lang)
        except ValueError as e:
            die(2, str(e))
        keys = rv.doc_keys(slides)
        js, rv_css = rv.patch_js(js), rv.CSS
        rv_head = rv.header_html(labels, lang)
        rv_tail = rv.tail_html(slides, keys, labels, lang, title)

    nav, items = [], []
    for i, (s, p) in enumerate(zip(slides, imgs), 1):
        t = s["title"]
        if s["section"] or i == 1:
            label = t if s["section"] and t else (L["cover"] if i == 1 else f"p.{i}")
            nav.append(f'<a href="#s{i}">{html.escape(label)}</a>')
        w, h = jpeg_size(p)
        dims = f' width="{w}" height="{h}"' if w and h else ""
        cap = f"p.{i} {t}".strip()
        cls = ' class="sec"' if s["section"] else ""
        lazy = "" if i <= 2 else ' loading="lazy"'
        items.append(
            f'<figure id="s{i}"{cls}>'
            f'<figcaption><span class="n">p.{i}</span> {html.escape(t)}</figcaption>'
            f'<img src="img/{os.path.basename(p)}" alt="{html.escape(cap)}"'
            f'{lazy}{dims}>{rv.bar_html(keys[i - 1], i, labels, lang) if a.comments else ""}</figure>')

    meta_line = " ・ ".join(x for x in (subtitle, rev, L["count"].format(n=n)) if x)
    page = f"""<!doctype html>
<html lang="{L['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="claude:viewport-fit-sides" content="cover">
<title>{html.escape(title)}</title>
<style>{CSS}{rv_css}</style>
</head>
<body>
<header><div class="bar"><div class="meta"><h1>{html.escape(title)}</h1><p>{html.escape(meta_line)}</p></div>
<span id="keys">{L['keys']}</span><span id="cur"></span>
<span id="zm" role="group" aria-label="{L['zoom']}"><button type="button" data-d="-1" aria-label="{L['zout']}" title="{L['zout']}">−</button><button type="button" id="zp" aria-label="{L['zreset']}" title="{L['zreset']}">100%</button><button type="button" data-d="1" aria-label="{L['zin']}" title="{L['zin']}">＋</button></span>
<form id="go" action="#"><input id="pn" type="number" inputmode="numeric" min="1" max="{n}" placeholder="p." aria-label="{L['page']}"><button type="submit">{L['go']}</button></form></div>
<nav>{''.join(nav)}</nav>{rv_head}</header>
<main>{''.join(items)}</main>
<dialog id="lb" aria-label="{L['lbopen']}"><div id="lbb"><span id="lbt"></span><button type="button" data-m="-1" aria-label="{L['prev']}">‹</button><button type="button" data-m="1" aria-label="{L['next']}">›</button><button type="button" data-d="-1" aria-label="{L['zout']}">−</button><button type="button" id="lbp" aria-label="{L['zreset']}">100%</button><button type="button" data-d="1" aria-label="{L['zin']}">＋</button><button type="button" id="lbx">{L['close']}</button></div><div id="lbv"><img alt=""></div></dialog>
<script>{js}{ZOOM_JS}</script>
{rv_tail}</body>
</html>
"""
    with open(os.path.join(a.out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    secs = sum(1 for s in slides if s["section"])
    extra = ", review bar on" if a.comments else ""
    print(f"{n} slide(s), {secs} section(s){extra} -> {os.path.join(a.out_dir, 'index.html')}")


if __name__ == "__main__":
    main()
