#!/usr/bin/env python3
"""preview_server_check.py — preview_server.py over real HTTP, without a browser.

Serves a copy of OUT on a free port and checks: static files come back as with http.server;
GET /_reviews names the store; PUT keeps only the known fields in OUT/reviews/<id>.json and
preview_comments.py reads that folder; DELETE removes it; a bad id, a request from another
site's page, a non-object body and an oversize body are refused and write nothing.

usage: preview_server_check.py OUT      (OUT/index.html exists)
exit:  0 all good / 1 a check failed / 2 cannot run
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "..", "assets")
bad = []


def req(url, method="GET", body=None, headers=None):
    data = body if isinstance(body, bytes) or body is None else json.dumps(body).encode()
    r = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    if data is not None:
        r.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(r, timeout=5) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def main():
    if len(sys.argv) != 2 or not os.path.isfile(os.path.join(sys.argv[1], "index.html")):
        print(__doc__.strip().split("\n\n")[-2], file=sys.stderr)
        return 2
    out = tempfile.mkdtemp()
    try:
        shutil.copy(os.path.join(sys.argv[1], "index.html"), out)
        p = subprocess.Popen([sys.executable, os.path.join(A, "preview_server.py"), "--directory", out, "--port", "0"],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        m = re.search(r"on (http://[^/]+/)", p.stdout.readline())
        if not m:
            print("preview_server.py did not start", file=sys.stderr)
            p.kill()
            return 2
        u = m.group(1)
        try:
            code, body = req(u + "index.html")
            if code != 200 or body != open(os.path.join(out, "index.html"), "rb").read():
                bad.append(f"index.html not served as is ({code})")
            code, body = req(u + "_reviews")
            if code != 200 or json.loads(body) != {"store": "pptx-preview-reviews", "docs": []}:
                bad.append(f"GET /_reviews on an empty store: {code} {body[:200]!r}")
            doc = {"status": "要修正", "comment": "矢印の向き", "updated": "2026-11-24T00:00:00Z",
                   "page": 3, "slide": "", "title": "id の無い枚", "extra": "<script>", "page_x": True}
            code, _ = req(u + "_reviews/t-80f740bb28", "PUT", doc)
            f = os.path.join(out, "reviews", "t-80f740bb28.json")
            saved = json.load(open(f, encoding="utf-8")) if os.path.isfile(f) else None
            if code != 200 or saved != {k: doc[k] for k in ("status", "comment", "updated", "page", "slide", "title")}:
                bad.append(f"PUT did not store exactly the known fields: {code} {saved}")
            code, body = req(u + "_reviews")
            docs = json.loads(body).get("docs", [])
            if [d["id"] for d in docs] != ["t-80f740bb28"]:
                bad.append(f"GET /_reviews after PUT: {docs}")
            r = subprocess.run([sys.executable, os.path.join(A, "preview_comments.py"), out],
                               capture_output=True, text=True)
            if "p3 要修正: 矢印の向き" not in r.stdout:
                bad.append(f"preview_comments.py OUT did not read the server's files: {r.stdout}{r.stderr}")
            for what, args in (("a bad id", (u + "_reviews/..%2Fescape", "PUT", {"status": "OK"})),
                               ("another site's page", (u + "_reviews/x1", "PUT", {"status": "OK"}, {"Origin": "http://evil.example"})),
                               ("a non-object body", (u + "_reviews/x2", "PUT", [1, 2])),
                               ("an oversize body", (u + "_reviews/x3", "PUT", {"comment": "x" * 70000}))):
                code, _ = req(*args)
                if code < 400:
                    bad.append(f"{what} was accepted ({code})")
            left = sorted(os.listdir(os.path.join(out, "reviews")))
            if left != ["t-80f740bb28.json"]:
                bad.append(f"refused requests wrote files: {left}")
            if os.path.exists(os.path.join(os.path.dirname(out), "escape.json")):
                bad.append("a path outside OUT/reviews was written")
            code, _ = req(u + "_reviews/t-80f740bb28", "DELETE")
            if code != 200 or os.path.exists(f):
                bad.append(f"DELETE did not remove the file ({code})")
        finally:
            p.kill()
            p.wait()
    finally:
        shutil.rmtree(out, ignore_errors=True)
    for b in bad:
        print("NG " + b)
    if not bad:
        print("OK preview_server: static files, GET/PUT/DELETE /_reviews, field filter, refusals, preview_comments reads OUT")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
