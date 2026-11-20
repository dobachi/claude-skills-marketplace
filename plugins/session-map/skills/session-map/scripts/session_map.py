#!/usr/bin/env python3
"""session_map.py — map the Claude Code sessions running on this machine.

Facts come from files Claude Code already writes, not from guessing:
  ~/.claude/sessions/<pid>.json         name, status, cwd, tmux pane, entrypoint
  ~/.claude/projects/*/<sessionId>.jsonl the conversation (title, prompts, replies)
  ps                                     alive or not, stopped (Ctrl-Z) or not
  tmux list-panes -a                     session / window / pane names

With --summarize, each session's conversation is cut down to a few thousand
characters (first ask, recent asks, recent replies, edited files, commits) and a
cheap model (haiku by default) turns it into five lines. Results are cached by
transcript mtime, so an unchanged session costs nothing the second time.

Standard library only. Exit codes: 0 = listed, 1 = listed but some summaries
failed, 2 = precondition missing (no sessions directory) or usage error.
"""
import argparse
import glob
import hashlib
import json
import os
import re
import socket
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

SUMMARY_SYSTEM = """あなたは Claude Code の作業セッションの記録を読み、持ち主が一目で状況をつかめるよう要約する。
記録にないことは書かない。推測には「らしい」を付ける。固有名（ファイル、成果物、コミット）はそのまま残す。
出力は次の5行だけ。各行60字以内。見出し語は変えない。
目的: このセッションは何のためか（成果物・対象を具体名で）
いま: 直近で取り組んでいること
状態: 終わった／途中／止まっている、と最後に何が起きたか（コミット・プッシュ済みか等）
待ち: 持ち主の返事や判断を待っているならその中身。なければ「なし」
次: 次にやること（記録から分かる範囲で）"""

DEEP_SYSTEM = """あなたは Claude Code の作業セッションの記録を読み、持ち主が作業に戻れるよう要約する。
記録にないことは書かない。推測には「らしい」を付ける。固有名（ファイル、成果物、コミット）はそのまま残す。
次の見出しで、各項目は箇条書き3つ以内、1つ80字以内。
目的:
経緯: これまでに終わったこと（古い順）
決めたこと: 理由つき
いま:
待ち: 持ち主の返事や判断を待っているならその中身。なければ「なし」
次:
注意: 未コミット・未検証・止まっている処理など。なければ「なし」"""

LIMITS = {
    "normal": dict(first=2, first_chars=500, asks=12, ask_chars=300, replies=4, reply_chars=700, files=12, cmds=6),
    "deep": dict(first=3, first_chars=800, asks=30, ask_chars=400, replies=10, reply_chars=1200, files=25, cmds=12),
}
SKIP_PREFIX = ("<", "This session is being continued", "[Request interrupted", "Caveat:")
EDIT_TOOLS = ("Write", "Edit", "MultiEdit", "NotebookEdit")
COMMIT_RE = re.compile(r"git (commit|push|tag)|gh (pr|release)")


def claude_dir(arg):
    return arg or os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")


def read_lines(path_or_cmd, cmd):
    """Read a fixture file when given, else run the command. Missing command → empty."""
    if path_or_cmd:
        with open(path_or_cmd, encoding="utf-8") as f:
            return f.read().splitlines()
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=20).stdout.splitlines()
    except (OSError, subprocess.SubprocessError):
        return []


def process_table(ps_file):
    table = {}
    for line in read_lines(ps_file, ["ps", "-eo", "pid=,ppid=,stat=,tty=,args="]):
        parts = line.split(None, 4)
        if len(parts) >= 4 and parts[0].isdigit():
            table[int(parts[0])] = {"stat": parts[2], "tty": parts[3], "args": parts[4] if len(parts) > 4 else ""}
    return table


TMUX_FIELDS = ("pane_id", "session", "attached", "window_index", "window_name", "pane_index", "pane_cmd", "pane_cwd")


def tmux_panes(tmux_file):
    fmt = "\t".join("#{%s}" % f for f in ("pane_id", "session_name", "session_attached", "window_index",
                                          "window_name", "pane_index", "pane_current_command", "pane_current_path"))
    panes = {}
    for line in read_lines(tmux_file, ["tmux", "list-panes", "-a", "-F", fmt]):
        vals = line.split("\t")
        if len(vals) == len(TMUX_FIELDS):
            panes[vals[0]] = dict(zip(TMUX_FIELDS, vals))
    return panes


def pane_of(tmux_ref):
    """'8:@61.%61' → '%61'. Session names may contain ':' and '.', so take the tail."""
    if not tmux_ref:
        return None
    m = re.search(r"(%\d+)$", tmux_ref)
    return m.group(1) if m else None


def transcript_path(cdir, sid):
    hits = glob.glob(os.path.join(cdir, "projects", "*", sid + ".jsonl"))
    return max(hits, key=os.path.getmtime) if hits else None


def _text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(x.get("text", "") for x in content if isinstance(x, dict) and x.get("type") == "text")
    return ""


def _cut(s, n):
    s = " ".join(s.split())
    return s if len(s) <= n else s[:n] + "…"


def _cut_mid(s, n):
    """Keep both ends. A reply's question to the user is usually at the end."""
    s = " ".join(s.split())
    if len(s) <= n:
        return s
    head = n // 3
    return s[:head] + " … " + s[-(n - head):]


SUMMARY_KEYS = ("目的", "いま", "状態", "待ち", "次")
KEY_RE = re.compile(r"^[\s>*#\-・]*(?:\*\*)?(%s)(?:\*\*)?\s*[:：]\s*(.*)$" % "|".join(SUMMARY_KEYS))
DEEP_KEYS = ("目的", "経緯", "決めたこと", "いま", "待ち", "次", "注意")
DEEP_RE = re.compile(r"^[\s#*]*(?:\*\*)?(%s)(?:\*\*)?\s*[:：]?" % "|".join(DEEP_KEYS))


def normalize(text, deep):
    """Hold the model to the format: the five lines in order, nothing else.
    A model that adds a preamble or drops a line should not change what the reader sees."""
    lines = [l.rstrip() for l in text.splitlines() if l.strip()]
    if deep:
        start = next((i for i, l in enumerate(lines) if DEEP_RE.match(l)), None)
        return "\n".join(lines[start:]) if start is not None else None
    found = {}
    for l in lines:
        m = KEY_RE.match(l)
        if m and m.group(1) not in found:
            found[m.group(1)] = m.group(2).strip().rstrip("*").strip()
    if not found:
        return None
    return "\n".join("%s: %s" % (k, found.get(k) or "（要約に無し）") for k in SUMMARY_KEYS)


def read_transcript(path):
    """One pass over the transcript: asks, replies, edited files, commit commands, title."""
    t = {"asks": [], "replies": [], "files": [], "cmds": [], "title": None, "last_prompt": None}
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if not isinstance(r, dict) or r.get("isSidechain"):
                continue
            kind = r.get("type")
            if kind == "ai-title":
                t["title"] = r.get("aiTitle") or t["title"]
            elif kind == "custom-title":
                t["title"] = r.get("customTitle") or t["title"]
            elif kind == "last-prompt":
                t["last_prompt"] = r.get("lastPrompt") or t["last_prompt"]
            elif kind == "user" and not r.get("isMeta") and not r.get("isCompactSummary"):
                s = _text((r.get("message") or {}).get("content")).strip()
                if s and not s.startswith(SKIP_PREFIX):
                    t["asks"].append(s)
            elif kind == "assistant":
                content = (r.get("message") or {}).get("content")
                s = _text(content).strip()
                if s:
                    t["replies"].append(s)
                for x in content if isinstance(content, list) else []:
                    if not isinstance(x, dict) or x.get("type") != "tool_use":
                        continue
                    inp = x.get("input") or {}
                    if x.get("name") in EDIT_TOOLS and inp.get("file_path"):
                        t["files"].append(inp["file_path"])
                    elif x.get("name") == "Bash" and COMMIT_RE.search(inp.get("command", "")):
                        t["cmds"].append(_cut(inp["command"], 160))
    return t


def _recent_unique(xs, n):
    return list(dict.fromkeys(reversed(xs)))[:n]


def material(s, t, depth):
    L = LIMITS[depth]
    out = ["セッション名: %s  状態: %s  作業ディレクトリ: %s" % (s.get("name") or "-", s.get("status"), s.get("cwd")),
           "やり取りの回数: %d" % len(t["asks"]), "## 最初の指示（目的）"]
    out += [_cut(a, L["first_chars"]) for a in t["asks"][:L["first"]]]
    out += ["## 直近の指示（古い順）"] + [_cut(a, L["ask_chars"]) for a in t["asks"][-L["asks"]:]]
    out += ["## 直近の返答（古い順）"] + [_cut_mid(a, L["reply_chars"]) for a in t["replies"][-L["replies"]:]]
    if t["files"]:
        out += ["## 最近編集したファイル（新しい順）"] + _recent_unique(t["files"], L["files"])
    if t["cmds"]:
        out += ["## 最近のコミット・プッシュ操作（新しい順）"] + _recent_unique(t["cmds"], L["cmds"])
    if s.get("screen"):
        out += ["## いまの画面（tmux）", s["screen"]]
    return "\n".join(out)


def summarizer_cmd(model, system):
    """The cheap call: no tools, no MCP, no settings, no saved session."""
    override = os.environ.get("SESSION_MAP_SUMMARIZER")
    if override:
        return ["/bin/sh", "-c", override]
    return ["claude", "-p", "--model", model, "--tools", "", "--strict-mcp-config", "--disable-slash-commands",
            "--no-session-persistence", "--setting-sources", "", "--system-prompt", system, "--output-format", "json"]


def summarize(s, t, args):
    # A session waiting on the user gets the deep material (and its screen) but the short format:
    # the question it is waiting on is exactly what a short excerpt tends to miss.
    depth = "deep" if args.deep or s.get("status") == "waiting" else "normal"
    system = DEEP_SYSTEM if args.deep else SUMMARY_SYSTEM
    mat = material(s, t, depth)
    key = hashlib.sha1(("%s|%s|%s|%s|%s" % (s["transcript"], s["transcript_mtime"], args.model, depth,
                                            hashlib.sha1(mat.encode()).hexdigest())).encode()).hexdigest()[:20]
    cpath = os.path.join(args.cache_dir, key + ".json")
    if not args.no_cache and os.path.exists(cpath):
        with open(cpath, encoding="utf-8") as f:
            res = json.load(f)
        # Entries written before a format change are held to the current format too.
        norm = normalize(res.get("summary") or "", args.deep)
        if norm:
            return dict(res, summary=norm, cached=True)
    try:
        p = subprocess.run(summarizer_cmd(args.model, system), input=mat, capture_output=True, text=True,
                           cwd=args.cache_dir, timeout=args.timeout)
    except (OSError, subprocess.SubprocessError) as e:
        return {"error": "要約に失敗: %s" % e}
    if p.returncode != 0:
        return {"error": "要約に失敗 (exit %d): %s" % (p.returncode, _cut(p.stderr or p.stdout, 200))}
    out = p.stdout.strip()
    cost = 0.0
    try:
        d = json.loads(out)
        out, cost = (d.get("result") or "").strip(), d.get("total_cost_usd") or 0.0
        if d.get("is_error"):
            return {"error": "要約に失敗: %s" % _cut(out, 200)}
    except ValueError:
        pass  # a plain-text summarizer (SESSION_MAP_SUMMARIZER) is fine
    norm = normalize(out, args.deep)
    if not norm:
        return {"error": "要約の形式が崩れている: %s" % _cut(out, 120)}
    res = {"summary": norm, "cost_usd": cost, "material_chars": len(mat)}
    tmp = cpath + ".tmp"
    with open(os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False)
    os.replace(tmp, cpath)
    return dict(res, cached=False)


def capture_screen(pane, lines, screen_file=None):
    if screen_file:
        with open(screen_file, encoding="utf-8") as f:
            return f.read().strip() or None
    try:
        out = subprocess.run(["tmux", "capture-pane", "-p", "-t", pane, "-S", "-%d" % lines],
                             capture_output=True, text=True, timeout=10).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    out = "\n".join(l.rstrip() for l in out.splitlines() if l.strip())
    return out[-4000:] or None


def collect(args):
    cdir = claude_dir(args.claude_dir)
    sdir = os.path.join(cdir, "sessions")
    if not os.path.isdir(sdir):
        print("session_map: %s がありません。Claude Code が動いているマシンで実行してください" % sdir, file=sys.stderr)
        sys.exit(2)
    procs = process_table(args.ps_file)
    panes = tmux_panes(args.tmux_file)
    now = args.now or time.time()
    live, stale = [], []
    for f in sorted(glob.glob(os.path.join(sdir, "*.json"))):
        try:
            with open(f, encoding="utf-8") as fh:
                r = json.load(fh)
        except (OSError, ValueError):
            continue
        if not isinstance(r, dict) or not isinstance(r.get("pid"), int) or not r.get("sessionId"):
            continue
        s = {k: r.get(k) for k in ("pid", "sessionId", "name", "status", "waitingFor", "cwd", "tmux", "entrypoint",
                                   "kind", "bridgeSessionId", "version", "startedAt", "updatedAt")}
        s["idle_days"] = round((now - (r.get("updatedAt") or r.get("startedAt") or now * 1000) / 1000) / 86400, 1)
        p = procs.get(s["pid"])
        if not p:
            stale.append(s)
            continue
        s["stopped"] = "T" in p["stat"]
        s["tty"] = p["tty"]
        pane = pane_of(s["tmux"])
        if pane in panes:
            s["where"] = "tmux"
            s["pane"] = panes[pane]
        elif s["entrypoint"] == "sdk-cli" or (s["tty"] in ("?", "") and s["bridgeSessionId"]):
            s["where"] = "remote-control"
        elif s["kind"] == "background" or s["tty"] in ("?", ""):
            s["where"] = "background"
        else:
            s["where"] = "terminal"
        tp = transcript_path(cdir, s["sessionId"])
        s["transcript"] = tp
        s["transcript_mtime"] = os.path.getmtime(tp) if tp else None
        live.append(s)

    # Flags are facts the summary writer should not have to rediscover.
    by_name, by_sid, by_pane = {}, {}, {}
    for s in live:
        if s["name"]:
            by_name.setdefault(s["name"], []).append(s)
        by_sid.setdefault(s["sessionId"], []).append(s)
        if s["where"] == "tmux":
            by_pane.setdefault(s["pane"]["pane_id"], []).append(s)
    for s in live:
        flags = []
        if s["status"] == "waiting":
            flags.append("入力待ち" + ("（%s）" % s["waitingFor"] if s.get("waitingFor") else ""))
        if s["stopped"]:
            flags.append("一時停止中（Ctrl-Z）")
        if s["idle_days"] >= args.stale_days and s["status"] != "busy":
            flags.append("%d日更新なし" % int(s["idle_days"]))
        if not s["transcript"]:
            flags.append("会話ログなし")
        if s["name"] and len(by_name[s["name"]]) > 1:
            flags.append("同名のセッションが%d個" % len(by_name[s["name"]]))
        if len(by_sid[s["sessionId"]]) > 1:
            flags.append("同じ会話を%d個のプロセスが開いている" % len(by_sid[s["sessionId"]]))
        if s["where"] == "tmux" and len(by_pane[s["pane"]["pane_id"]]) > 1:
            flags.append("同じペインに claude が%d個" % len(by_pane[s["pane"]["pane_id"]]))
        s["flags"] = flags
    return cdir, live, stale, panes


def select(live, query):
    q = query.lower()
    hits = [s for s in live if q in (str(s["pid"]), s["sessionId"][:len(q)], s["sessionId"])
            or q in (s["name"] or "").lower() or (s["where"] == "tmux" and q == s["pane"]["pane_id"].lower())]
    return hits


def run_summaries(live, args):
    os.makedirs(args.cache_dir, mode=0o700, exist_ok=True)
    jobs, done = {}, {}
    # One summary per conversation, even if two processes hold it. The running, most recently
    # updated process owns it; the others point at it instead of repeating it.
    for s in sorted(live, key=lambda s: (s["stopped"], -(s.get("updatedAt") or 0))):
        if not s["transcript"]:
            continue
        if s["sessionId"] in jobs:
            s["same_as"] = jobs[s["sessionId"]][0]["pid"]
            continue
        t = read_transcript(s["transcript"])
        s["title"] = t["title"]
        jobs[s["sessionId"]] = (s, t)
    with ThreadPoolExecutor(max(1, args.jobs)) as ex:
        futs = {sid: ex.submit(summarize, s, t, args) for sid, (s, t) in jobs.items()}
        for sid, fu in futs.items():
            done[sid] = fu.result()
    failed = 0
    for s in live:
        r = done.get(s["sessionId"])
        if r and not s.get("same_as"):
            s.update({k: v for k, v in r.items() if k in ("summary", "error", "cost_usd", "cached")})
            failed += 1 if r.get("error") else 0
    return failed


def light_titles(live):
    for s in live:
        if s["transcript"] and "title" not in s:
            t = read_transcript(s["transcript"])
            s["title"], s["last_prompt"] = t["title"], t["last_prompt"] or (t["asks"][-1] if t["asks"] else None)


def label(s):
    return s["name"] or s.get("title") or s["sessionId"][:8]


def render(live, stale, panes, args, cost):
    home = os.path.expanduser("~")
    short = lambda p: (p or "-").replace(home, "~", 1)
    counts = {}
    for s in live:
        counts[s["where"]] = counts.get(s["where"], 0) + 1
    out = ["%s  %s  動いている claude %d（%s）  終了済みの記録 %d" % (
        socket.gethostname(), time.strftime("%Y-%m-%d %H:%M", time.localtime(args.now or time.time())), len(live),
        " / ".join("%s %d" % (k, v) for k, v in sorted(counts.items())), len(stale))]
    if cost:
        out.append("要約の費用: $%.4f" % cost)

    def entry(s, ind):
        head = "%s● %s  [%s]  pid %d  %s前  %s" % (ind, label(s), s["status"], s["pid"],
                                                  "%.0f日" % s["idle_days"] if s["idle_days"] >= 1 else "%.0f時間" % (s["idle_days"] * 24),
                                                  short(s["cwd"]))
        lines = [head]
        if s["flags"]:
            lines.append(ind + "  ! " + " / ".join(s["flags"]))
        if s.get("same_as"):
            lines.append(ind + "  （pid %d と同じ会話。要約はそちら）" % s["same_as"])
        elif s.get("summary"):
            lines += [ind + "  " + l for l in s["summary"].splitlines() if l.strip()]
        elif s.get("error"):
            lines.append(ind + "  (" + s["error"] + ")")
        else:
            if s.get("title"):
                lines.append(ind + "  題名: " + s["title"])
            if s.get("last_prompt"):
                lines.append(ind + "  直近の指示: " + _cut(s["last_prompt"], 80))
        return lines

    tm = [s for s in live if s["where"] == "tmux"]
    sessions = {}
    for s in tm:
        sessions.setdefault(s["pane"]["session"], []).append(s)
    for name in sorted(sessions, key=lambda n: (not n.isdigit(), int(n) if n.isdigit() else 0, n)):
        ss = sessions[name]
        att = ss[0]["pane"]["attached"]
        others = sum(1 for p in panes.values() if p["session"] == name) - len({s["pane"]["pane_id"] for s in ss})
        out.append("")
        out.append("tmux %s  (%s%s)" % (name, "接続中 %s" % att if att not in ("0", "") else "未接続",
                                         "、claude 以外のペイン %d" % others if others > 0 else ""))
        ss.sort(key=lambda s: (int(s["pane"]["window_index"]), int(s["pane"]["pane_index"]), s["stopped"]))
        last = None
        for s in ss:
            p = s["pane"]
            here = (p["window_index"], p["pane_index"])
            if here != last:
                out.append("  %s:%s.%s  %s  %s" % (name, p["window_index"], p["pane_index"], p["window_name"], p["pane_id"]))
                last = here
            out += entry(s, "    ")
    titles = {"terminal": "tmux の外の端末", "remote-control": "Remote Control から起動", "background": "バックグラウンド"}
    for where in ("terminal", "background", "remote-control"):
        ss = sorted((s for s in live if s["where"] == where), key=lambda s: s["idle_days"])
        if ss:
            out.append("")
            out.append(titles[where])
            for s in ss:
                out += entry(s, "  ")
    if stale:
        out.append("")
        out.append("終了済み（記録だけ残っている）: " + ", ".join("%s(pid %d)" % (label(s), s["pid"]) for s in stale))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Map running Claude Code sessions, tmux-aware.")
    ap.add_argument("--summarize", action="store_true", help="summarize each session with a cheap model")
    ap.add_argument("--session", metavar="Q", help="only sessions matching pid, sessionId prefix, name or %%pane")
    ap.add_argument("--deep", action="store_true", help="with --session: longer material, screen capture, longer summary")
    ap.add_argument("--model", default=os.environ.get("SESSION_MAP_MODEL", "haiku"))
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--stale-days", type=float, default=7)
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--cache-dir", default=os.path.join(os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache")),
                                                        "session-map"))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--claude-dir", help=argparse.SUPPRESS)
    ap.add_argument("--ps-file", help=argparse.SUPPRESS)
    ap.add_argument("--tmux-file", help=argparse.SUPPRESS)
    ap.add_argument("--now", type=float, help=argparse.SUPPRESS)
    ap.add_argument("--screen-file", help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    if args.deep and not args.session:
        ap.error("--deep は --session と一緒に使う")

    _, live, stale, panes = collect(args)
    if args.session:
        live = select(live, args.session)
        if not live:
            print("session_map: '%s' に当たるセッションがありません" % args.session, file=sys.stderr)
            return 2
        if args.deep:
            args.summarize = True
    if args.summarize:
        for s in live:
            if s["where"] == "tmux" and (args.deep or s["status"] == "waiting"):
                s["screen"] = capture_screen(s["pane"]["pane_id"], 60, args.screen_file)
    failed = run_summaries(live, args) if args.summarize else 0
    light_titles(live)
    cost = sum(s.get("cost_usd") or 0 for s in {s["sessionId"]: s for s in live}.values() if not s.get("cached"))
    if args.json:
        for s in live:
            s.pop("screen", None)
        print(json.dumps({"host": socket.gethostname(), "live": live, "stale": stale, "cost_usd": cost},
                         ensure_ascii=False, indent=1))
    else:
        print(render(live, stale, panes, args, cost))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
