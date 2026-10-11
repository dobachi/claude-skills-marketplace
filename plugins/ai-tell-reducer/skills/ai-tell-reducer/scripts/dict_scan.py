#!/usr/bin/env python3
"""辞書で「見るべき場所」を洗い出す。

これは判定器ではない。当たった箇所は候補であり、直すかどうかは各カテゴリの
test（読み手への効果）で決める。SKILL.md の「Effect over count」を参照。

使い方:
  dict_scan.py FILE...                 候補を一覧する
  dict_scan.py FILE... --summary       見出し語ごとの件数だけ
  dict_scan.py FILE... --format tsv    台帳（判断欄つき）として出力
  dict_scan.py FILE... --headings      見出しを一覧し、文になっているものに印を付ける
  dict_scan.py --selftest              辞書の各見出し語が自分の example に当たるか

  --dict PATH    プロジェクト辞書を重ねる（同じ id は上書き）。複数可
  --allow PATH   残すと決めた語句。1行1語句、`id:<id>` で見出し語ごと無効化
  --only NAME    カテゴリまたは id で絞る。複数可
  --evidence LV  根拠の強さで絞る（measured/guideline/curated/observed/folk）。複数可
  --lang CODE    同梱辞書の言語（既定 ja）

  カレントディレクトリに .ai-tell-dict.ini / .ai-tell-allow.txt があれば自動で読む。

終了コード: 0=候補なし / 1=候補あり / 2=引数・読み取り・辞書のエラー
"""
import argparse
import configparser
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
DICT_DIR = HERE.parent / "dict"
LOCAL_DICT = ".ai-tell-dict.ini"
LOCAL_ALLOW = ".ai-tell-allow.txt"
SCOPES = ("any", "heading", "body")
# 根拠の強さ。辞書の語が「AIの癖」だという主張は、多くが実測で裏付けられていない。
# だから各見出し語に、何を根拠に載せたのかを持たせる（references/dictionary.md）。
EVIDENCE = ("measured", "guideline", "curated", "observed", "folk")
CAT_PREFIX = "category:"

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
# 本文として読まない部分。桁位置を保つため同じ長さの空白に置き換える。
MASKS = [
    re.compile(r"`[^`]*`"),                 # インラインコード
    re.compile(r"<!--.*?-->"),              # HTML コメント
    re.compile(r"https?://[^\s)>\]]+"),     # URL
    re.compile(r"\[@[^\]]*\]"),             # 引用キー
    re.compile(r"@[A-Za-z][\w:-]*"),        # 相互参照
    re.compile(r"\{[#.][^}]*\}"),           # 見出し・スパンの属性
]
# 見出しが文になっているか: 主題の助詞を含み、述語の終止形で終わる
SENTENCE_END_RE = re.compile(r"(る|た|い|だ|す|ぬ|う|く|つ|む|ぶ|ぐ)$")
SUBJECT_RE = re.compile(r"[^、。]+(は|が|も)[^、。]*")


class DictError(Exception):
    pass


def die(msg):
    print(f"dict_scan: {msg}", file=sys.stderr)
    sys.exit(2)


def read_ini(path):
    cp = configparser.ConfigParser(
        interpolation=None, delimiters=("=",), comment_prefixes=("#",),
        strict=True)
    cp.optionxform = str
    try:
        with open(path, encoding="utf-8") as f:
            cp.read_file(f)
    except OSError as e:
        raise DictError(f"{path}: 読めない ({e.strerror})")
    except configparser.Error as e:
        raise DictError(f"{path}: 書式エラー: {str(e).splitlines()[0]}")
    return cp


def load_dicts(paths):
    """辞書を順に重ねる。後のものが同じ id・カテゴリを上書きする。"""
    cats, entries = {}, {}
    for path in paths:
        cp = read_ini(path)
        for sec in cp.sections():
            body = dict(cp[sec])
            body["_src"] = str(path)
            if sec.startswith(CAT_PREFIX):
                cats[sec[len(CAT_PREFIX):]] = body
            else:
                entries[sec] = body
    problems = []
    for eid, e in entries.items():
        where = f"{e['_src']} [{eid}]"
        for key in ("category", "pattern", "example"):
            if not e.get(key):
                problems.append(f"{where}: {key} が無い")
        if e.get("category") and e["category"] not in cats:
            problems.append(f"{where}: カテゴリ {e['category']} が未定義")
        cat = cats.get(e.get("category"), {})
        e.setdefault("scope", cat.get("scope", "any"))
        for key in ("evidence", "source"):
            if not e.get(key) and cat.get(key):
                e[key] = cat[key]
        # プロジェクト辞書は著者が決めた語なので、書かなければ observed とみなす。
        # 同梱辞書は必ず明記する。
        if not e.get("evidence") and e["_src"] != str(paths[0]):
            e["evidence"] = "observed"
        if e.get("evidence") not in EVIDENCE:
            problems.append(f"{where}: evidence は {'/'.join(EVIDENCE)} のいずれか")
        if e["scope"] not in SCOPES:
            problems.append(f"{where}: scope は {'/'.join(SCOPES)} のいずれか")
        try:
            e["_re"] = re.compile(e.get("pattern", ""))
        except re.error as err:
            problems.append(f"{where}: pattern が正規表現として不正 ({err})")
    for name, c in cats.items():
        for key in ("label", "test", "ref"):
            if not c.get(key):
                problems.append(f"{c['_src']} [category:{name}]: {key} が無い")
    if problems:
        raise DictError("\n  ".join(["辞書に不備がある"] + problems))
    return cats, entries


def selftest(cats, entries):
    """各見出し語が自分の example に当たり、counter に当たらないことを確かめる。"""
    bad = []
    for eid, e in entries.items():
        if not e["_re"].search(e["example"]):
            bad.append(f"[{eid}] example に当たらない: {e['example']}")
        if e.get("counter") and e["_re"].search(e["counter"]):
            bad.append(f"[{eid}] counter に当たってしまう: {e['counter']}")
        if e["_re"].search(""):
            bad.append(f"[{eid}] pattern が空文字列に当たる")
    for line in bad:
        print(line)
    print(f"selftest: 見出し語 {len(entries)} / カテゴリ {len(cats)} / 不備 {len(bad)}")
    return 1 if bad else 0


def load_allow(paths):
    phrases, ids = [], set()
    for path in paths:
        try:
            text = Path(path).read_text(encoding="utf-8")
        except OSError as e:
            die(f"{path}: 読めない ({e.strerror})")
        for raw in text.splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("id:"):
                ids.add(line[3:].strip())
            else:
                phrases.append(line)
    return phrases, ids


def mask(line):
    for rx in MASKS:
        line = rx.sub(lambda m: " " * len(m.group()), line)
    return line


def prose_lines(text):
    """(行番号, 種別, 検査対象の文字列, 元の行) を返す。コードと前付けは飛ばす。"""
    lines = text.splitlines()
    i = 0
    if lines and lines[0].strip() == "---":
        for j in range(1, len(lines)):
            if lines[j].strip() in ("---", "..."):
                i = j + 1
                break
    fence = None
    for n in range(i, len(lines)):
        raw = lines[n]
        m = FENCE_RE.match(raw)
        if m:
            fence = None if fence == m.group(1) else (fence or m.group(1))
            continue
        if fence:
            continue
        h = HEADING_RE.match(raw)
        if h:
            yield n + 1, "heading", mask(h.group(2)).rstrip(), raw
        else:
            yield n + 1, "body", mask(raw), raw


def allowed(span, target, phrases):
    s, e = span
    for p in phrases:
        start = target.find(p)
        while start != -1:
            if start <= s and e <= start + len(p):
                return True
            start = target.find(p, start + 1)
    return False


def scan(path, entries, phrases):
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as e:
        die(f"{path}: 読めない ({e.strerror})")
    except UnicodeDecodeError:
        die(f"{path}: UTF-8 として読めない")
    hits = []
    for lineno, kind, target, raw in prose_lines(text):
        for eid, e in entries.items():
            if e["scope"] not in ("any", kind):
                continue
            for m in e["_re"].finditer(target):
                if allowed(m.span(), target, phrases):
                    continue
                hits.append({
                    "file": str(path), "line": lineno, "kind": kind, "id": eid,
                    "category": e["category"], "match": m.group(),
                    "context": raw.strip(), "fix": e.get("fix", ""),
                    "evidence": e["evidence"], "source": e.get("source", ""),
                    "note": e.get("note", ""),
                })
    return hits


def headings(paths):
    for path in paths:
        try:
            text = Path(path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            die(f"{path}: 読めない ({e})")
        for lineno, kind, target, raw in prose_lines(text):
            if kind != "heading":
                continue
            body = target.strip().rstrip("。")
            sentence = bool(SENTENCE_END_RE.search(body) and SUBJECT_RE.search(body))
            level = len(raw) - len(raw.lstrip("#"))
            print(f"{path}:{lineno}\t{'文' if sentence else '  '}\t{'  ' * (level - 1)}{body}")
    return 0


def clip(s, width=90):
    return s if len(s) <= width else s[: width - 1] + "…"


def report(hits, cats, fmt, summary):
    if fmt == "json":
        print(json.dumps(hits, ensure_ascii=False, indent=1))
        return
    if fmt == "tsv":
        print("\t".join(["file", "line", "kind", "category", "id", "evidence", "match",
                         "context", "decision"]))
        for h in hits:
            print("\t".join([h["file"], str(h["line"]), h["kind"], h["category"], h["id"],
                             h["evidence"], h["match"], h["context"].replace("\t", " "), ""]))
        return
    if not summary:
        for h in hits:
            mark = " [見出し]" if h["kind"] == "heading" else ""
            print(f"{h['file']}:{h['line']}: {h['category']}/{h['id']}{mark} 「{h['match']}」"
                  f" ({h['evidence']})")
            print(f"    {clip(h['context'])}")
            if h["fix"]:
                print(f"    → {h['fix']}")
            if h["note"]:
                print(f"    ※ {h['note']}")
        if hits:
            print()
    by_cat = Counter(h["category"] for h in hits)
    by_id = Counter((h["category"], h["id"], h["evidence"]) for h in hits)
    print(f"候補 {len(hits)} 件（判定ではない。カテゴリごとの test で残すか直すかを決める）")
    for cat, n in by_cat.most_common():
        c = cats[cat]
        print(f"\n{c['label']}  {n} 件  [{cat}]  {c['ref']}")
        print(f"  test: {c['test']}")
        for (kc, eid, ev), k in by_id.most_common():
            if kc == cat:
                print(f"  {k:4d}  {eid}  ({ev})")
    by_ev = Counter(h["evidence"] for h in hits)
    if by_ev:
        print("\n根拠の強さ: " + " / ".join(f"{ev} {by_ev[ev]}" for ev in EVIDENCE if by_ev[ev]))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0], add_help=True)
    ap.add_argument("files", nargs="*")
    ap.add_argument("--dict", action="append", default=[], dest="dicts")
    ap.add_argument("--allow", action="append", default=[])
    ap.add_argument("--only", action="append", default=[])
    ap.add_argument("--evidence", action="append", default=[], choices=EVIDENCE)
    ap.add_argument("--lang", default="ja")
    ap.add_argument("--format", choices=("text", "tsv", "json"), default="text")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--headings", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--no-local", action="store_true",
                    help="カレントディレクトリの辞書・許可リストを自動で読まない")
    try:
        args = ap.parse_args()
    except SystemExit as e:
        sys.exit(0 if e.code == 0 else 2)

    bundled = DICT_DIR / f"{args.lang}.ini"
    if not bundled.is_file():
        die(f"同梱辞書が無い: {bundled}")
    dict_paths = [bundled] + [Path(p) for p in args.dicts]
    allow_paths = list(args.allow)
    if not args.no_local:
        if Path(LOCAL_DICT).is_file():
            dict_paths.append(Path(LOCAL_DICT))
        if Path(LOCAL_ALLOW).is_file():
            allow_paths.append(LOCAL_ALLOW)

    try:
        cats, entries = load_dicts(dict_paths)
    except DictError as e:
        die(str(e))

    if args.selftest:
        sys.exit(selftest(cats, entries))
    if not args.files:
        die("ファイルを指定する（--help で使い方）")
    if args.headings:
        sys.exit(headings(args.files))

    phrases, muted = load_allow(allow_paths)
    unknown = [x for x in list(muted) + args.only if x not in entries and x not in cats]
    if unknown:
        die(f"辞書に無い id・カテゴリ: {', '.join(unknown)}")
    active = {k: v for k, v in entries.items() if k not in muted}
    if args.only:
        active = {k: v for k, v in active.items()
                  if k in args.only or v["category"] in args.only}
    if args.evidence:
        active = {k: v for k, v in active.items() if v["evidence"] in args.evidence}

    if args.format == "text":
        extra = [str(p) for p in dict_paths[1:]] + [str(p) for p in allow_paths]
        if extra:
            print(f"dict_scan: 併用 {', '.join(extra)}", file=sys.stderr)

    hits = []
    for path in args.files:
        hits.extend(scan(path, active, phrases))
    report(hits, cats, args.format, args.summary)
    sys.exit(1 if hits else 0)


if __name__ == "__main__":
    main()
