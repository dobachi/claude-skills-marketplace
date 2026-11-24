"""preview_review.py — the opt-in review bar for preview_web.py (`--comments`).

Imported by preview_web.py only when `--comments` is given; without it the page is exactly
what it was before. Adds, under each slide image, status buttons and a comment box; in the
header a filter, a counter, a storage notice and an Export button.

Storage, decided in the browser at load time:
  * Claude Artifact published with `capabilities: {db: {}}` → `claude.use("db")` resolves,
    and each slide is one document in collection "reviews" (doc id = the spec's slide id,
    else a key made from the slide title, else "p<N>"; see doc_keys), body {status, comment,
    updated, page, slide, title}, live via onSnapshot.
  * served by preview_server.py (`preview_web.sh --serve`) → the same documents as JSON files in
    OUT/reviews/<doc id>.json, through GET _reviews / PUT and DELETE _reviews/<id>, polled every
    5 s so every reader sees the others' comments.
  * anything else (file, a plain static server, an Artifact without db) → localStorage, one key per slide
    ("pptx-preview-review:<deck title>|<doc id>"), with a notice that it stays in this browser.
Export (both cases): Markdown in the review-roundtrip comment style, one line per slide
("p12 [slide-id] 要修正: …"), copied to the clipboard and offered as a download.
assets/preview_comments.py reads that Markdown, or a JSON dump of the collection, back.
"""
import hashlib
import html
import json
import re

COLLECTION = "reviews"
DOC_ID = re.compile(r"^(?!\.\.?$)[A-Za-z0-9_\-.~:@+]{1,200}$")  # the Artifact db segment grammar

DEFAULT_LABELS = {"ja": ["OK", "要修正", "質問"], "en": ["OK", "Fix", "Question"]}

UI = {
    "ja": {
        "f_all": "すべて", "f_has": "記入あり", "f_none": "未記入", "f_label": "絞り込み",
        "count": "{n} / {t} 枚に記入", "export": "書き出し",
        "ph": "p.{p} へのコメント", "saved": "保存",
        "connecting": "保存先を確認しています…",
        "local": "コメントはこのブラウザの中だけに保存されます。ほかの人や端末には届かないので、渡すときは「書き出し」を使ってください",
        "memory": "このブラウザでは保存できません。閉じる前に「書き出し」で渡してください",
        "dbon": "コメントは自動で保存され、この Artifact を開ける人全員に見えます",
        "srvon": "コメントはプレビューのサーバに自動で保存され、このページを開ける人全員に見えます",
        "dbslow": "保存先に届いていません。書いた分は「書き出し」で控えてください",
        "saving": "保存しています…", "dbsaved": "保存しました",
        "dberr": "保存できませんでした（{e}）。このブラウザに控えたので「書き出し」で渡してください",
        "readonly": "この Artifact では書き込めません（閲覧のみ）。コメントはこのブラウザに控えます。「書き出し」で渡してください",
        "d_title": "コメントの書き出し", "copy": "コピー", "download": "ダウンロード", "close": "閉じる",
        "copied": "クリップボードにコピーしました", "copyfail": "自動でコピーできませんでした。下の文字を選んでコピーしてください",
        "dlfail": "ダウンロードできませんでした（{e}）。コピーを使ってください",
        "exp_title": "レビューコメント", "none": "（コメントはまだありません）",
        "unmatched": "いまのデッキに無いスライドへのコメント",
        "orph": "（どのスライドにも付けられないコメント {n} 件は、書き出しの末尾に入ります）",
    },
    "en": {
        "f_all": "All", "f_has": "Commented", "f_none": "Not reviewed", "f_label": "Filter",
        "count": "{n} / {t} slides reviewed", "export": "Export",
        "ph": "Comment on p.{p}", "saved": "saved",
        "connecting": "Checking where to save…",
        "local": "Comments are saved in this browser only; nobody else sees them. Use Export to hand them over",
        "memory": "This browser cannot save. Use Export before closing the page",
        "dbon": "Comments save automatically and are visible to everyone who can open this artifact",
        "srvon": "Comments save automatically on the preview server and are visible to everyone who can open this page",
        "dbslow": "The store is not answering yet. Use Export to keep what you wrote",
        "saving": "Saving…", "dbsaved": "Saved",
        "dberr": "Could not save ({e}). Kept in this browser; use Export to hand it over",
        "readonly": "This artifact is view-only for you. Comments are kept in this browser; use Export to hand them over",
        "d_title": "Export comments", "copy": "Copy", "download": "Download", "close": "Close",
        "copied": "Copied to the clipboard", "copyfail": "Could not copy automatically; select the text below and copy it",
        "dlfail": "Download failed ({e}); use Copy",
        "exp_title": "Review comments", "none": "(no comments yet)",
        "unmatched": "Comments on slides that are not in this deck",
        "orph": " ({n} comment(s) match no slide in this deck; Export lists them at the end)",
    },
}


def parse_labels(text, lang):
    """--review-labels "OK,要修正,質問" → list; None → the language's default."""
    if text is None:
        return list(DEFAULT_LABELS[lang])
    labels = [x.strip() for x in text.split(",") if x.strip()]
    if not 1 <= len(labels) <= 6:
        raise ValueError("--review-labels takes 1 to 6 comma-separated labels")
    for x in labels:
        if len(x) > 20 or re.search(r"[:：\[\]\n<>\"]", x) or x.lower().startswith("p") and x[1:].isdigit():
            raise ValueError(f"review label {x!r}: at most 20 characters, no colon, bracket, quote or < >")
    if len(set(labels)) != len(labels):
        raise ValueError("--review-labels has a duplicate")
    return labels


def title_key(title, nth):
    """"t-<10 hex>" from the slide title; the second slide with the same title gets ".2"."""
    h = "t-" + hashlib.sha1(title.encode("utf-8")).hexdigest()[:10]
    return h if nth == 1 else f"{h}.{nth}"


def doc_keys(slides):
    """One stable document id per slide, so a comment stays on its slide when slides are
    inserted or deleted before it: the spec's `id` when it is a valid, unique db segment, else
    a key made from the slide title (title_key), else — a slide with no title — "p<N>".
    The page re-homes records saved under an older "p<N>" key by their stored id or title."""
    ids = [s.get("id") or "" for s in slides]
    seen, keys, nth = set(), [], {}
    good = {i for i in ids if i and DOC_ID.match(i) and ids.count(i) == 1}
    for n, (i, s) in enumerate(zip(ids, slides), 1):
        t = s.get("title") or ""
        if i in good:
            k = i
        elif t:
            nth[t] = nth.get(t, 0) + 1
            k = title_key(t, nth[t])
        else:
            k = f"p{n}"
        while k in seen or (k != i and k in good):
            k = "_" + k
        seen.add(k)
        keys.append(k)
    return keys


CSS = """
:root { --ok:#1d7a3e; --fix:#b3261e; --ask:#8a5a00; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --ok:#5cc386; --fix:#f08a80; --ask:#e0b04a; } }
:root[data-theme="dark"] { --ok:#5cc386; --fix:#f08a80; --ask:#e0b04a; }
figure { scroll-margin-top:150px; }
figure[hidden] { display:none; }
#rv { display:flex; flex-wrap:wrap; align-items:center; gap:6px 10px; margin-top:6px; font-size:12px; }
#rv select, #rv button { font:inherit; font-size:13px; padding:3px 8px; border:1px solid var(--line); border-radius:6px; background:var(--bg); color:var(--fg); }
#rv button { border-color:var(--accent); color:var(--accent); cursor:pointer; }
#rvcount { font-variant-numeric:tabular-nums; color:var(--muted); }
#rvnote { flex:1 1 260px; min-width:0; color:var(--muted); font-size:11px; line-height:1.35; }
#rvnote.warn { color:var(--ask); }
.rb { display:flex; flex-wrap:wrap; gap:6px; align-items:flex-start; margin-top:0; padding:8px; border:1px solid var(--line); border-top:0; background:var(--card); }
.rb.has { border-left:3px solid var(--accent); }
.rbb { display:flex; flex-wrap:wrap; gap:6px; align-items:center; flex:1 1 100%; }
.rbb button { font:inherit; font-size:13px; padding:3px 12px; border-radius:999px; border:1px solid var(--line); background:var(--bg); color:var(--fg); cursor:pointer; }
.rbb button[aria-pressed="true"] { color:#fff; border-color:transparent; background:var(--accent); }
.rbb button[aria-pressed="true"][data-i="0"] { background:var(--ok); }
.rbb button[aria-pressed="true"][data-i="1"] { background:var(--fix); }
.rbb button[aria-pressed="true"][data-i="2"] { background:var(--ask); }
:root[data-theme="dark"] .rbb button[aria-pressed="true"] { color:#11161d; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) .rbb button[aria-pressed="true"] { color:#11161d; } }
.rbs { margin-left:auto; font-size:11px; color:var(--muted); }
.rb textarea { flex:1 1 100%; min-width:0; min-height:2.6em; resize:vertical; font:inherit; font-size:16px; line-height:1.45; padding:6px 8px; border:1px solid var(--line); border-radius:6px; background:var(--bg); color:var(--fg); }
@media (min-width:900px) { .rb textarea { font-size:14px; } }
#rvd { width:min(720px, calc(100vw - 32px)); border:1px solid var(--line); border-radius:10px; background:var(--card); color:var(--fg); padding:16px; }
#rvd::backdrop { background:rgba(0,0,0,.45); }
#rvd h2 { margin:0 0 8px; font-size:15px; }
#rvd textarea { width:100%; height:min(50vh, 420px); font:12px/1.5 ui-monospace,monospace; padding:8px; border:1px solid var(--line); border-radius:6px; background:var(--bg); color:var(--fg); }
#rvd .row { display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-top:8px; }
#rvd button { font:inherit; font-size:13px; padding:5px 12px; border:1px solid var(--accent); border-radius:6px; background:var(--accent); color:#fff; cursor:pointer; }
#rvd button.sub { background:transparent; color:var(--accent); }
#rvdmsg { font-size:12px; color:var(--muted); flex:1 1 200px; }
"""

# Patches to the base page script, applied only with --comments: a filtered-out slide is
# skipped by the current-page indicator and by j/k, a jump to one clears the filter, and the
# keys do nothing while the export dialog is open. Each must apply exactly once.
JS_PATCHES = [
    ("var el=document.getElementById('s'+n); if(el){",
     "var el=document.getElementById('s'+n); if(el&&el.hidden&&window.__rvShowAll) window.__rvShowAll(); if(el){"),
    ("for(var i=0;i<figs.length;i++){ if(figs[i].getBoundingClientRect().top<=edge) k=i+1; else break; }",
     "for(var i=0;i<figs.length;i++){ if(figs[i].hidden) continue; if(figs[i].getBoundingClientRect().top<=edge) k=i+1; else break; }"),
    ("if(e.ctrlKey||e.metaKey||e.altKey||e.isComposing) return;",
     "if(e.ctrlKey||e.metaKey||e.altKey||e.isComposing||document.querySelector('dialog[open]')) return;"),
    ("e.preventDefault(); go(now+1); }", "e.preventDefault(); go(step(1)); }"),
    ("e.preventDefault(); go(now-1); }", "e.preventDefault(); go(step(-1)); }"),
    ("  window.addEventListener('resize',mark); mark();",
     "  window.addEventListener('resize',mark); mark();\n"
     "  function step(d){ for(var n=now+d;n>=1&&n<=N;n+=d){ if(!document.getElementById('s'+n).hidden) return n; } return now; }"),
]


def patch_js(js):
    for old, new in JS_PATCHES:
        if js.count(old) != 1:
            raise RuntimeError(f"preview_review: base script changed; cannot patch {old[:40]!r}")
        js = js.replace(old, new)
    return js


def bar_html(key, page, labels, lang):
    btns = "".join(f'<button type="button" data-s="{html.escape(x)}" data-i="{i}" aria-pressed="false">'
                   f'{html.escape(x)}</button>' for i, x in enumerate(labels))
    ph = UI[lang]["ph"].format(p=page)
    return (f'<div class="rb" data-k="{html.escape(key)}"><div class="rbb">{btns}<span class="rbs"></span></div>'
            f'<textarea rows="2" placeholder="{html.escape(ph)}" aria-label="{html.escape(ph)}"></textarea></div>')


def header_html(labels, lang):
    u = UI[lang]
    opts = [("all", u["f_all"]), ("has", u["f_has"]), ("none", u["f_none"])]
    opts += [("s:" + x, x) for x in labels]
    sel = "".join(f'<option value="{html.escape(v)}">{html.escape(t)}</option>' for v, t in opts)
    return (f'<div id="rv"><select id="rvf" aria-label="{u["f_label"]}">{sel}</select>'
            f'<span id="rvcount"></span><button type="button" id="rvx">{u["export"]}</button>'
            f'<span id="rvnote" role="status">{u["connecting"]}</span></div>')


def tail_html(slides, keys, labels, lang, title):
    u = UI[lang]
    cfg = {"title": title, "lang": lang, "coll": COLLECTION, "labels": labels, "ui": u,
           "slides": [{"k": k, "p": n, "id": s.get("id") or "", "t": s["title"]}
                      for n, (s, k) in enumerate(zip(slides, keys), 1)]}
    data = json.dumps(cfg, ensure_ascii=False).replace("</", "<\\/")
    dialog = (f'<dialog id="rvd" aria-labelledby="rvdh"><h2 id="rvdh">{u["d_title"]}</h2>'
              f'<textarea id="rvdt" readonly></textarea><div class="row"><span id="rvdmsg" role="status"></span>'
              f'<button type="button" id="rvdc">{u["copy"]}</button>'
              f'<button type="button" id="rvdd">{u["download"]}</button>'
              f'<button type="button" class="sub" id="rvdx">{u["close"]}</button></div></dialog>')
    return f"{dialog}\n<script>{JS.replace('__CFG__', data)}</script>\n"


JS = r"""
(function(){
  var C=__CFG__, U=C.ui, S=C.slides;
  var st={}, mode='pending', where='', db=null, dl=null, dirty={}, inflight={}, written={}, timers={}, orphans={}, locOrph={}, moving={};
  var PAGEKEY=/^_*p\d+$/, POLL=5000;
  var PFX='pptx-preview-review:'+C.title+'|';
  var $=function(s){ return document.querySelector(s); };
  var bars={}, byKey={};
  Array.prototype.forEach.call(document.querySelectorAll('.rb'),function(b){ bars[b.getAttribute('data-k')]=b; });
  S.forEach(function(s){ byKey[s.k]=s; st[s.k]={status:'',comment:'',updated:''}; });
  function note(t,warn){ var n=$('#rvnote'); n.textContent=t; n.className=warn?'warn':''; }
  function has(v){ return !!(v&&(v.status||String(v.comment||'').trim())); }
  function when(iso){ try{ var d=new Date(iso); if(isNaN(d)) return ''; return d.toLocaleString(C.lang==='ja'?'ja-JP':'en-US',{month:'numeric',day:'numeric',hour:'2-digit',minute:'2-digit'}); }catch(e){ return ''; } }
  function paint(k){ var b=bars[k], v=st[k]; if(!b) return;
    Array.prototype.forEach.call(b.querySelectorAll('button[data-s]'),function(x){ x.setAttribute('aria-pressed',String(v.status===x.getAttribute('data-s'))); });
    var ta=b.querySelector('textarea'); if(document.activeElement!==ta&&ta.value!==(v.comment||'')) ta.value=v.comment||'';
    b.classList.toggle('has',has(v));
    b.querySelector('.rbs').textContent=v.updated?U.saved+' '+when(v.updated):''; }
  function lost(){ var o={}; [orphans,locOrph].forEach(function(m){ Object.keys(m).forEach(function(k){ if(has(m[k])) o[k]=m[k]; }); }); return o; }
  function count(){ var n=0; S.forEach(function(s){ if(has(st[s.k])) n++; });
    var o=Object.keys(lost()).length;
    $('#rvcount').textContent=U.count.replace('{n}',n).replace('{t}',S.length)+(o?U.orph.replace('{n}',o):''); }
  function filt(){ var f=$('#rvf').value;
    S.forEach(function(s){ var v=st[s.k], show=true;
      if(f==='has') show=has(v); else if(f==='none') show=!has(v); else if(f.indexOf('s:')===0) show=v.status===f.slice(2);
      var fig=document.getElementById('s'+s.p); if(fig) fig.hidden=!show; });
    window.dispatchEvent(new Event('scroll')); }
  window.__rvShowAll=function(){ $('#rvf').value='all'; filt(); };
  function rec(k){ var s=byKey[k], v=st[k];
    return {status:v.status||'',comment:v.comment||'',updated:v.updated||'',page:s.p,slide:s.id||'',title:s.t||''}; }
  function val(v){ return {status:v.status||'',comment:v.comment||'',updated:v.updated||''}; }
  function newer(a,b){ return String(a.updated||'')>String(b.updated||''); }
  // Which slide of THIS deck a stored record belongs to. A spec id or title key is trusted. A
  // page-number key ("p3", older pages or untitled slides) is trusted only while the slide on
  // that page still has the title the record was written on; otherwise the record follows its
  // slide id, else its title (when exactly one slide has it). null: no slide here takes it.
  function home(k,v){ var s=byKey[k];
    if(s&&(!PAGEKEY.test(k)||v.title==null||String(v.title)===(s.t||''))) return k;
    var m=S.filter(function(x){ return v.slide?x.id===v.slide:(!!v.title&&x.t===v.title); });
    return m.length===1?m[0].k:null; }
  // ---- storage: localStorage (any browser) ----
  function keep(k){ try{ localStorage.setItem(PFX+k,JSON.stringify(rec(k))); return true; }catch(e){ return false; } }
  function local(k){ if(!keep(k)){ mode='memory'; note(U.memory,true); } }
  function localKeys(){ var ks=[]; try{ for(var i=0;i<localStorage.length;i++){ var x=localStorage.key(i);
      if(x&&x.indexOf(PFX)===0&&x!==PFX+'_probe') ks.push(x.slice(PFX.length)); } }catch(e){} return ks; }
  function localGet(k){ try{ var v=JSON.parse(localStorage.getItem(PFX+k)); return v&&typeof v==='object'?v:null; }catch(e){ return null; } }
  // Read every record of this deck, put each on its slide (records on their own key first, then
  // re-homed ones, which never overwrite a newer record), and move re-homed ones to their key.
  // into(h,v,k) applies one; it returns false when the record stays where it is.
  function sweepLocal(into){ var later=[];
    localKeys().forEach(function(k){ var v=localGet(k); if(!v) return; var h=home(k,v);
      if(h===null){ if(has(v)) locOrph[k]=v; return; }
      if(h===k) into(h,v,k); else later.push([k,h,v]); });
    later.forEach(function(x){ var k=x[0],h=x[1],v=x[2];
      if(dirty[h]||(has(st[h])&&!newer(v,st[h]))){ if(has(v)) locOrph[k]=v; return; }
      if(into(h,v,k)!==false){ try{ localStorage.removeItem(PFX+k); }catch(e){} } }); }
  function loadLocal(){ sweepLocal(function(h,v,k){ if(dirty[h]) return false; st[h]=val(v); paint(h); if(h!==k) keep(h); }); }
  // ---- storage: a shared store (the Artifact db, or the preview server), one document per slide ----
  function push(k){
    if(inflight[k]){ dirty[k]=1; return; }
    delete dirty[k];
    var body=rec(k), sig=JSON.stringify([body.status,body.comment]);
    if(written[k]===sig) return;            // write only on a real change
    inflight[k]=true; note(U.saving);
    db.collection(C.coll).doc(k).set(body).then(function(){ written[k]=sig; note(U.dbsaved); },function(e){
      var code=(e&&(e.code||e.message))||String(e); keep(k);
      if(e&&e.code==='invalid_argument'){ mode='local'; note(U.readonly,true); } else note(U.dberr.replace('{e}',code),true);
    }).then(function(){ inflight[k]=false; if(dirty[k]){ if(mode==='db') push(k); else { delete dirty[k]; local(k); } } });
  }
  function flush(){ Object.keys(dirty).forEach(function(k){ delete dirty[k]; if(mode==='db') push(k); else if(mode==='local') local(k); }); }
  function save(k){ st[k].updated=new Date().toISOString(); paint(k); count();
    if(mode==='pending'){ dirty[k]=1; } else if(mode==='db') push(k); else if(mode==='local') local(k); }
  // A record stored under an old key that belongs to another slide now: write it under that
  // slide's key, then delete the old document (only after the write succeeded).
  function rehome(k,h,v){
    if(timers[h]||inflight[h]||dirty[h]||(has(st[h])&&!newer(v,st[h]))){ orphans[k]=v; return; }
    st[h]=val(v); paint(h);
    if(moving[k]||mode!=='db') return; moving[k]=1;
    var body=rec(h); inflight[h]=true;
    db.collection(C.coll).doc(h).set(body).then(function(){ written[h]=JSON.stringify([body.status,body.comment]);
      return db.collection(C.coll).doc(k).delete(); }).then(null,function(){ delete moving[k]; })
      .then(function(){ inflight[h]=false; if(dirty[h]&&mode==='db') push(h); }); }
  // Comments this browser kept before a shared store was available (an older page, or the
  // server not running then): hand them to the store once, unless the store has newer ones.
  // The local copy goes once read: a failed write keeps it again (push → keep), and a copy
  // left behind would bring back a comment someone has since cleared in the store.
  function adoptLocal(){ sweepLocal(function(h,v,k){ try{ localStorage.removeItem(PFX+k); }catch(e){}
      if(!has(v)||dirty[h]||inflight[h]||timers[h]||(has(st[h])&&!newer(v,st[h]))) return;
      st[h]=val(v); paint(h); push(h); }); count(); }
  function subscribe(){
    var first=true, tm=setTimeout(function(){ note(U.dbslow,true); },10000);
    db.collection(C.coll).onSnapshot(function(snap){
      orphans={}; var later=[];
      snap.docs.forEach(function(d){ var v=d.data()||{}, k=d.id, h=home(k,v);
        if(h===null){ orphans[k]=v; return; }
        if(h!==k){ later.push([k,h,v]); return; }
        if(timers[k]||inflight[k]||dirty[k]) return;   // this page's own edit is newer
        st[k]=val(v); written[k]=JSON.stringify([st[k].status,st[k].comment]); paint(k); });
      later.forEach(function(x){ rehome(x[0],x[1],x[2]); });
      if(!snap.metadata||!snap.metadata.fromCache){ clearTimeout(tm); if(mode==='db') note(where==='server'?U.srvon:U.dbon); }
      if(first){ first=false; adoptLocal(); filt(); }
      count();
    },function(e){ clearTimeout(tm); note(U.dberr.replace('{e}',(e&&e.code)||e),true); });
  }
  // The preview server (preview_server.py, what `preview_web.sh --serve` starts) answers
  // GET _reviews with every document and PUT / DELETE _reviews/<id> for one. This wraps it in
  // the same shape as the Artifact db, polling for other readers' comments every POLL ms.
  function http(r){ if(!r.ok){ var e=new Error('HTTP '+r.status); e.code='http_'+r.status; throw e; } return r; }
  function serverDb(base){ return {collection:function(){ return {
    doc:function(id){ var u=base+'/'+encodeURIComponent(id); return {
      set:function(b){ return fetch(u,{method:'PUT',headers:{'content-type':'application/json'},body:JSON.stringify(b)}).then(http); },
      'delete':function(){ return fetch(u,{method:'DELETE'}).then(http); } }; },
    onSnapshot:function(next,err){ var stop=false;
      function tick(){ if(stop) return;
        fetch(base,{cache:'no-store'}).then(http).then(function(r){ return r.json(); }).then(function(j){
          next({docs:(j.docs||[]).map(function(d){ return {id:d.id,data:function(){ return d.data; }}; }),metadata:{fromCache:false}}); },
          function(e){ if(err) err(e); }).then(function(){ if(!stop) setTimeout(tick,POLL); }); }
      tick(); return function(){ stop=true; }; } }; }}; }
  function probeServer(){
    if(!/^https?:$/.test(location.protocol)||typeof fetch!=='function') return toLocal();
    fetch('_reviews',{cache:'no-store'}).then(function(r){ return r.ok?r.json():null; }).then(function(j){
      if(!j||j.store!=='pptx-preview-reviews') return toLocal();
      db=serverDb('_reviews'); where='server'; mode='db'; note(U.connecting); subscribe(); flush(); },toLocal); }
  function toLocal(){ if(mode!=='pending') return; mode='local';
    try{ localStorage.setItem(PFX+'_probe','1'); localStorage.removeItem(PFX+'_probe'); note(U.local,true); }
    catch(e){ mode='memory'; note(U.memory,true); }
    if(mode==='local') loadLocal(); flush(); count(); }
  // ---- input ----
  document.querySelector('main').addEventListener('click',function(e){
    var b=e.target.closest('.rbb button'); if(!b) return;
    var k=b.closest('.rb').getAttribute('data-k'), s=b.getAttribute('data-s');
    st[k].status=st[k].status===s?'':s; save(k); });
  document.querySelector('main').addEventListener('input',function(e){
    if(e.target.tagName!=='TEXTAREA') return; var k=e.target.closest('.rb').getAttribute('data-k');
    st[k].comment=e.target.value; clearTimeout(timers[k]);
    timers[k]=setTimeout(function(){ delete timers[k]; save(k); },700); });
  document.querySelector('main').addEventListener('focusout',function(e){
    if(e.target.tagName!=='TEXTAREA') return; var k=e.target.closest('.rb').getAttribute('data-k');
    if(timers[k]){ clearTimeout(timers[k]); delete timers[k]; save(k); } });
  document.querySelector('main').addEventListener('keydown',function(e){ if(e.key==='Escape'&&e.target.tagName==='TEXTAREA') e.target.blur(); });
  window.addEventListener('pagehide',function(){ Object.keys(timers).forEach(function(k){ clearTimeout(timers[k]); delete timers[k]; save(k); }); });
  $('#rvf').addEventListener('change',filt);
  // ---- export: review-roundtrip comment lines, grouped per slide ----
  function line(p,id,v){ var c=String(v.comment||'').replace(/\r\n?/g,'\n').trim().split('\n'), head='p'+p+(id?' ['+id+']':'');
    var first=head+(v.status?' '+v.status+(c[0]?': '+c[0]:''):(c[0]?' '+c[0]:''));
    return [first].concat(c.slice(1).map(function(x){ return '  '+x; })).join('\n'); }
  function md(){ var out=['# '+C.title+' — '+U.exp_title,'','<!-- review-labels: '+C.labels.join(',')+' -->',
      '<!-- exported: '+new Date().toISOString()+' from '+(mode==='db'?(where==='server'?'preview server':'artifact db'):'this browser')+' -->',''], n=0;
    S.forEach(function(s){ var v=st[s.k]; if(!has(v)) return; n++;
      out.push('## p.'+s.p+(s.t?' '+s.t:''),'',line(s.p,s.id,v),''); });
    var lo=lost(), ok=Object.keys(lo);
    if(ok.length){ out.push('## '+U.unmatched,'');
      ok.forEach(function(k){ var v=lo[k]; out.push(line(v.page||'?',v.slide||k,v)); }); out.push(''); }
    if(!n&&!ok.length) out.push(U.none,'');
    return out.join('\n'); }
  function fname(){ return (C.title.replace(/[\\\/:*?"<>|\s]+/g,'-').replace(/^-+|-+$/g,'').slice(0,60)||'slides')+'-review.md'; }
  function msg(t){ $('#rvdmsg').textContent=t; }
  function copy(text){
    var ta=$('#rvdt');
    function fallback(){ ta.focus(); ta.select(); var ok=false; try{ ok=document.execCommand('copy'); }catch(e){} msg(ok?U.copied:U.copyfail); }
    if(navigator.clipboard&&navigator.clipboard.writeText){ navigator.clipboard.writeText(text).then(function(){ msg(U.copied); },fallback); }
    else fallback(); }
  $('#rvx').addEventListener('click',function(){ Object.keys(timers).forEach(function(k){ clearTimeout(timers[k]); delete timers[k]; save(k); });
    var text=md(); $('#rvdt').value=text; msg('');
    var d=$('#rvd'); if(d.showModal) d.showModal(); else d.setAttribute('open',''); copy(text); });
  $('#rvdc').addEventListener('click',function(){ copy($('#rvdt').value); });
  $('#rvdx').addEventListener('click',function(){ var d=$('#rvd'); if(d.close) d.close(); else d.removeAttribute('open'); });
  $('#rvdd').addEventListener('click',function(){ var text=$('#rvdt').value, name=fname();
    if(dl){ dl.save({filename:name,data:text}).then(function(){},function(e){ if(!e||e.code!=='declined') msg(U.dlfail.replace('{e}',(e&&e.code)||e)); }); return; }
    try{ var a=document.createElement('a'); a.href=URL.createObjectURL(new Blob([text],{type:'text/markdown;charset=utf-8'}));
      a.download=name; document.body.appendChild(a); a.click(); setTimeout(function(){ URL.revokeObjectURL(a.href); a.remove(); },1000); }
    catch(e){ msg(U.dlfail.replace('{e}',e.message||e)); } });
  window.__rvExport=md;
  count();
  // ---- where to save: decided once per load ----
  var W=window.claude;
  if(W&&typeof W.use==='function'){
    W.use('downloads').then(function(x){ dl=x||null; },function(){});
    W.use('db').then(function(d){ if(!d) return toLocal(); db=d; where='artifact'; mode='db'; note(U.connecting); subscribe(); flush(); },toLocal);
  } else probeServer();
})();
"""
