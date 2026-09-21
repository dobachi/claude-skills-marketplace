#!/usr/bin/env python3
"""walk_driver.py — a browser the walker can only use the way a user can.

Two halves, one file:

  serve   run by the CONDUCTOR, outside the walker's sandbox. Owns the browser
          (Playwright), records every action and every instrument event (console,
          page errors, HTTP >= 400) to a log directory the walker cannot see, and
          listens on a unix socket inside the walker's work directory.

  <verb>  run by the WALKER, inside the sandbox. Stdlib only — a thin client that
          sends one user action to the socket and prints what a user would perceive.

What the walker can do (the whole vocabulary):
  look | click | fill | press | select | check | uncheck | upload | goto | back |
  reload | viewport | shot | stop
Targets are what a user sees: --role R --name N | --label L | --text T | --placeholder P.

What it cannot do, by construction: run JavaScript, read the DOM or page source, use
CSS/XPath selectors, force-click a hidden or disabled element, navigate to a URL that
is neither linked on the current page nor listed in the policy, or see instrument
output. Console errors reach the report through the conductor, not the walker.

Usage (conductor):
  walk_driver.py serve --policy walk-policy.json --work <walker-dir> --log <log-dir>
Usage (walker, from inside <walker-dir>):
  python3 walk_driver.py look
  python3 walk_driver.py click --role button --name 保存
  python3 walk_driver.py fill --label 名前 --value ""
  python3 walk_driver.py goto http://localhost:3000/help

Exit codes: 0 action done / 1 action refused or failed (message says why, as a user
would experience it) / 2 usage error or no server.
"""
import argparse
import json
import os
import posixpath
import socket
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

SOCK_NAME = ".walk.sock"
ACTION_TIMEOUT_MS = 5000
SNAPSHOT_MAX_LINES = 250


def normalize(url):
    """Resolve ./ and ../ so a prefix cannot be escaped by path tricks."""
    u = urlparse(url)
    path = posixpath.normpath(u.path) if u.path else "/"
    if u.path.endswith("/") and not path.endswith("/"):
        path += "/"
    return u._replace(path=path, fragment="").geturl()


# ------------------------------------------------------------------ client side
def client(argv):
    ap = argparse.ArgumentParser(prog="walk_driver.py", add_help=True)
    sub = ap.add_subparsers(dest="verb", required=True)

    def target(p):
        p.add_argument("--role")
        p.add_argument("--name")
        p.add_argument("--label")
        p.add_argument("--text")
        p.add_argument("--placeholder")
        p.add_argument("--nth", type=int, help="0-based, when several visible elements match")
        p.add_argument("--exact", action="store_true", help="exact name/text match")

    sub.add_parser("look", help="what is on screen now")
    for v in ("click", "check", "uncheck"):
        p = sub.add_parser(v); target(p)
        p.add_argument("--dialog", choices=["accept", "dismiss"], default="accept",
                       help="how to answer a confirm/alert dialog this action opens")
    p = sub.add_parser("fill"); target(p); p.add_argument("--value", required=True)
    p = sub.add_parser("select"); target(p); p.add_argument("--option", required=True)
    p = sub.add_parser("upload"); target(p); p.add_argument("--file", required=True)
    p = sub.add_parser("press"); p.add_argument("key", help="e.g. Tab, Enter, Escape, Control+A")
    p = sub.add_parser("goto"); p.add_argument("url")
    sub.add_parser("back"); sub.add_parser("reload")
    p = sub.add_parser("viewport"); p.add_argument("size", help="WIDTHxHEIGHT, e.g. 375x740")
    p = sub.add_parser("shot"); p.add_argument("name")
    sub.add_parser("stop")
    a = ap.parse_args(argv)
    req = {k: v for k, v in vars(a).items() if v is not None and v is not False}

    sock_path = os.environ.get("WALK_SOCK", SOCK_NAME)
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        s.connect(sock_path)
    except OSError:
        print("walk_driver: no browser session at %s — ask the conductor to start one" % sock_path,
              file=sys.stderr)
        return 2
    s.sendall((json.dumps(req, ensure_ascii=False) + "\n").encode())
    buf = b""
    while not buf.endswith(b"\n"):
        chunk = s.recv(65536)
        if not chunk:
            break
        buf += chunk
    resp = json.loads(buf.decode() or '{"ok": false, "message": "no response"}')
    print(resp.get("message", ""))
    return 0 if resp.get("ok") else 1


# ------------------------------------------------------------------ server side
class Session:
    def __init__(self, policy, work, log, chrome):
        from playwright.sync_api import sync_playwright
        self.policy, self.work, self.log = policy, work, log
        self.step = 0
        self.pending_dialog = "accept"
        self.dialogs = []
        self.pw = sync_playwright().start()
        launch = {"executable_path": chrome} if chrome else {}
        self.browser = self.pw.chromium.launch(**launch)
        w, h = policy.get("viewport", [1280, 800])
        self.ctx = self.browser.new_context(viewport={"width": w, "height": h},
                                            locale=policy.get("locale", "ja-JP"))
        self.page = self.ctx.new_page()
        self.page.on("console", lambda m: m.type in ("error", "warning") and
                     self.instrument("console." + m.type, m.text))
        self.page.on("pageerror", lambda e: self.instrument("pageerror", str(e)))
        self.page.on("response", lambda r: r.status >= 400 and
                     self.instrument("http", "%d %s %s" % (r.status, r.request.method, r.url)))
        self.page.on("dialog", self.on_dialog)
        (work / "evidence").mkdir(parents=True, exist_ok=True)
        self.page.goto(policy["start_url"])

    # -- logging (conductor-side only)
    def write(self, name, rec):
        with open(self.log / name, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def instrument(self, kind, text):
        self.write("instruments.jsonl", {"ts": time.time(), "step": self.step,
                                         "kind": kind, "text": text})

    def on_dialog(self, d):
        self.dialogs.append("%s dialog: %s" % (d.type, d.message))
        (d.accept if self.pending_dialog == "accept" else d.dismiss)()

    # -- what a user can perceive
    def snapshot(self):
        try:
            tree = self.page.locator("body").aria_snapshot()
        except Exception as e:                       # very old Playwright
            tree = "(accessibility snapshot unavailable: %s)" % e
        lines = tree.splitlines()
        if len(lines) > SNAPSHOT_MAX_LINES:
            lines = lines[:SNAPSHOT_MAX_LINES] + ["... (%d more lines)" % (len(lines) - SNAPSHOT_MAX_LINES)]
        shot = self.work / "evidence" / ("step-%03d.png" % self.step)
        self.page.screenshot(path=str(shot), full_page=True)
        head = ["url: " + self.page.url, "title: " + self.page.title(),
                "screenshot: evidence/" + shot.name]
        if self.dialogs:
            head += self.dialogs
            self.dialogs = []
        return "\n".join(head + ["", *lines])

    # -- policy
    def allowed_url(self, url):
        url = normalize(urljoin(self.page.url, url))
        # Exact match, unless the policy entry ends in "*" (then it is a prefix).
        # start_url is exact: "http://host/" must not open every path on the host.
        for entry in self.policy.get("allowed_urls", []) + [self.policy["start_url"]]:
            if entry.endswith("*") and url.startswith(normalize(entry[:-1])):
                return url, None
            if url == normalize(entry):
                return url, None
        for link in self.page.get_by_role("link").all():
            try:
                href = link.get_attribute("href")
                if href and normalize(urljoin(self.page.url, href)) == url and link.is_visible():
                    return url, None
            except Exception:
                pass
        return url, ("not reachable by a user: %s is neither a visible link on this page "
                     "nor in the documented URLs" % url)

    def locate(self, r):
        p = self.page
        exact = bool(r.get("exact"))
        if r.get("role"):
            loc = p.get_by_role(r["role"], name=r.get("name"), exact=exact) if r.get("name") \
                else p.get_by_role(r["role"])
        elif r.get("label"):
            loc = p.get_by_label(r["label"], exact=exact)
        elif r.get("placeholder"):
            loc = p.get_by_placeholder(r["placeholder"], exact=exact)
        elif r.get("text"):
            loc = p.get_by_text(r["text"], exact=exact)
        else:
            raise UserFacing("say what you are pointing at: --role/--name, --label, --text or --placeholder")
        n = loc.count()
        visible = [i for i in range(n) if loc.nth(i).is_visible()]
        if not visible:
            raise UserFacing("nothing like that is visible on screen")
        if r.get("nth") is not None:
            if r["nth"] >= len(visible):
                raise UserFacing("only %d visible matches" % len(visible))
            return loc.nth(visible[r["nth"]])
        if len(visible) > 1:
            raise UserFacing("%d visible elements match — add --nth 0..%d" % (len(visible), len(visible) - 1))
        return loc.nth(visible[0])

    def act(self, r):
        v = r.get("verb")
        self.pending_dialog = r.get("dialog", "accept")
        if v == "look":
            pass
        elif v in ("click", "check", "uncheck", "fill", "select", "upload"):
            el = self.locate(r)
            if v in ("click", "check", "uncheck", "fill", "select") and not el.is_enabled():
                raise UserFacing("it is shown but disabled — a user cannot use it")
            if v == "click":
                el.click(timeout=ACTION_TIMEOUT_MS)
            elif v == "check":
                el.check(timeout=ACTION_TIMEOUT_MS)
            elif v == "uncheck":
                el.uncheck(timeout=ACTION_TIMEOUT_MS)
            elif v == "fill":
                el.fill(r["value"], timeout=ACTION_TIMEOUT_MS)
            elif v == "select":
                el.select_option(label=r["option"], timeout=ACTION_TIMEOUT_MS)
            elif v == "upload":
                f = (self.work / r["file"]).resolve()
                if self.work.resolve() not in f.parents or not f.is_file():
                    raise UserFacing("upload only files from your own work directory")
                el.set_input_files(str(f), timeout=ACTION_TIMEOUT_MS)
        elif v == "press":
            self.page.keyboard.press(r["key"])
        elif v == "goto":
            url, why = self.allowed_url(r["url"])
            if why:
                raise Refused(why)
            self.page.goto(url)
        elif v == "back":
            self.page.go_back()
        elif v == "reload":
            self.page.reload()
        elif v == "viewport":
            try:
                w, h = (int(x) for x in r["size"].lower().split("x"))
            except ValueError:
                raise UserFacing("size is WIDTHxHEIGHT, e.g. 375x740")
            self.page.set_viewport_size({"width": w, "height": h})
        elif v == "shot":
            name = "".join(c for c in r["name"] if c.isalnum() or c in "-_") or "shot"
            self.page.screenshot(path=str(self.work / "evidence" / (name + ".png")), full_page=True)
            return "saved evidence/%s.png" % name
        else:
            raise UserFacing("unknown action %r" % v)
        try:
            self.page.wait_for_load_state("networkidle", timeout=2000)
        except Exception:
            pass
        return self.snapshot()

    def close(self):
        try:
            self.browser.close()
        finally:
            self.pw.stop()


class UserFacing(Exception):
    """The action failed the way it would fail for a user."""


class Refused(Exception):
    """The action is outside what a user can do. Logged for the audit."""


def serve(argv):
    ap = argparse.ArgumentParser(prog="walk_driver.py serve")
    ap.add_argument("--policy", required=True, type=Path)
    ap.add_argument("--work", required=True, type=Path, help="the walker's work directory")
    ap.add_argument("--log", required=True, type=Path, help="conductor-only log directory")
    ap.add_argument("--chrome", help="browser executable, if Playwright's own is missing")
    a = ap.parse_args(argv)
    if not a.policy.is_file() or not a.work.is_dir():
        print("walk_driver serve: need an existing --policy file and --work directory", file=sys.stderr)
        return 2
    policy = json.loads(a.policy.read_text(encoding="utf-8"))
    if "start_url" not in policy:
        print("walk_driver serve: policy has no start_url", file=sys.stderr)
        return 2
    work, log = a.work.resolve(), a.log.resolve()
    if log == work or work in log.parents:
        print("walk_driver serve: --log must be outside the walker's work directory", file=sys.stderr)
        return 2
    log.mkdir(parents=True, exist_ok=True)
    sess = Session(policy, work, log, a.chrome)
    sock_path = work / SOCK_NAME
    if sock_path.exists():
        sock_path.unlink()
    srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    srv.bind(str(sock_path))
    srv.listen(1)
    print("walk_driver: serving %s on %s (log: %s)" % (policy["start_url"], sock_path, log), flush=True)
    try:
        while True:
            conn, _ = srv.accept()
            with conn:
                buf = b""
                while not buf.endswith(b"\n"):
                    chunk = conn.recv(65536)
                    if not chunk:
                        break
                    buf += chunk
                try:
                    req = json.loads(buf.decode())
                except ValueError:
                    continue
                sess.step += 1
                rec = {"ts": time.time(), "step": sess.step, "request": req}
                if req.get("verb") == "stop":
                    rec["result"] = "ok"
                    sess.write("actions.jsonl", rec)
                    conn.sendall(b'{"ok": true, "message": "session closed"}\n')
                    break
                try:
                    msg, ok, rec["result"] = sess.act(req), True, "ok"
                except Refused as e:
                    msg, ok, rec["result"] = "refused: %s" % e, False, "refused"
                except UserFacing as e:
                    msg, ok, rec["result"] = str(e), False, "failed"
                except Exception as e:                   # timeouts and the like
                    msg, ok, rec["result"] = "that did not work: %s" % str(e).splitlines()[0], False, "failed"
                rec["url"] = sess.page.url
                sess.write("actions.jsonl", rec)
                conn.sendall((json.dumps({"ok": ok, "message": msg}, ensure_ascii=False) + "\n").encode())
    finally:
        srv.close()
        if sock_path.exists():
            sock_path.unlink()
        sess.close()
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        sys.exit(serve(sys.argv[2:]))
    sys.exit(client(sys.argv[1:]))
