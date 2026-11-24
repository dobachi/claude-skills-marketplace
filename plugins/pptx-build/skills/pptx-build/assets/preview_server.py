#!/usr/bin/env python3
"""preview_server.py — serve a browser preview folder, and keep the comments a `--comments`
page collects on the server, so they are shared by every reader and readable by Claude.

What `preview_web.sh --serve` starts. Static files are served exactly as `python3 -m http.server
--directory OUT` would. In addition:

  GET    /_reviews        {"store": "pptx-preview-reviews", "docs": [{"id": ..., "data": {...}}]}
  PUT    /_reviews/<id>   store one slide's document (JSON object) as OUT/reviews/<id>.json
  DELETE /_reviews/<id>   remove it

The files have the layout ArtifactData `list` writes with `out_dir`, so
`preview_comments.py OUT [--spec deck.yaml] [--sheet SHEET]` reads them directly.
A page served by anything else (a plain static server, a file) falls back to localStorage.

Guards: the id must be a db-style segment (no slash, not . or ..); a body is at most 64 KiB and
only the known fields are kept; at most 5000 documents; a request whose Origin is another site
is refused (a write from another page in the reader's browser), and no CORS headers are sent.

usage: preview_server.py --directory OUT [--bind 127.0.0.1] [--port 8765]
"""
import argparse
import functools
import json
import os
import re
import sys
import tempfile
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlsplit

DOC_ID = re.compile(r"^(?!\.\.?$)[A-Za-z0-9_\-.~:@+]{1,200}$")  # same grammar as preview_review.py
FIELDS = {"status": str, "comment": str, "updated": str, "page": int, "slide": str, "title": str}
MAX_BODY = 64 * 1024
MAX_DOCS = 5000
STORE = "pptx-preview-reviews"
LOCK = threading.Lock()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, root, **kw):
        self.root = root
        super().__init__(*a, directory=root, **kw)

    # ---- helpers ----
    def reviews_dir(self):
        return os.path.join(self.root, "reviews")

    def route(self):
        """None for a static path, "" for /_reviews, the id for /_reviews/<id>, False if bad."""
        path = urlsplit(self.path).path
        if path == "/_reviews" or path == "/_reviews/":
            return ""
        if not path.startswith("/_reviews/"):
            return None
        doc = unquote(path[len("/_reviews/"):])
        return doc if DOC_ID.match(doc) else False

    def send_json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def foreign(self):
        """A request sent by a page from another site (Origin set and not this host)."""
        origin = self.headers.get("Origin")
        if not origin:
            return False
        return urlsplit(origin).netloc != (self.headers.get("Host") or "")

    # ---- verbs ----
    def do_GET(self):
        r = self.route()
        if r is None:
            return super().do_GET()
        if r is not False and r != "":
            return self.send_json(405, {"error": "GET /_reviews lists every document"})
        if r is False or self.foreign():
            return self.send_json(403, {"error": "refused"})
        docs = []
        d = self.reviews_dir()
        if os.path.isdir(d):
            for name in sorted(os.listdir(d)):
                if not name.endswith(".json") or not DOC_ID.match(name[:-5]):
                    continue
                try:
                    with open(os.path.join(d, name), encoding="utf-8") as f:
                        data = json.load(f)
                except (OSError, ValueError):
                    continue
                if isinstance(data, dict):
                    docs.append({"id": name[:-5], "data": data})
        self.send_json(200, {"store": STORE, "docs": docs})

    def do_HEAD(self):
        if self.route() is None:
            return super().do_HEAD()
        self.send_response(405)
        self.end_headers()

    def do_PUT(self):
        doc = self.route()
        if not doc or self.foreign():
            return self.send_json(403 if doc is not None else 405, {"error": "refused"})
        try:
            n = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            n = -1
        if n <= 0 or n > MAX_BODY:
            return self.send_json(413, {"error": f"body must be 1..{MAX_BODY} bytes"})
        try:
            data = json.loads(self.rfile.read(n).decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            return self.send_json(400, {"error": "body is not JSON"})
        if not isinstance(data, dict):
            return self.send_json(400, {"error": "body must be a JSON object"})
        clean = {k: data[k] for k, t in FIELDS.items()
                 if k in data and isinstance(data[k], t) and not isinstance(data[k], bool)}
        d = self.reviews_dir()
        path = os.path.join(d, doc + ".json")
        with LOCK:
            os.makedirs(d, exist_ok=True)
            if not os.path.exists(path) and len(os.listdir(d)) >= MAX_DOCS:
                return self.send_json(507, {"error": f"at most {MAX_DOCS} documents"})
            fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp-", suffix=".json")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(clean, f, ensure_ascii=False, indent=1)
            os.replace(tmp, path)
        self.send_json(200, {"id": doc})

    def do_DELETE(self):
        doc = self.route()
        if not doc or self.foreign():
            return self.send_json(403 if doc is not None else 405, {"error": "refused"})
        with LOCK:
            try:
                os.remove(os.path.join(self.reviews_dir(), doc + ".json"))
            except FileNotFoundError:
                pass
        self.send_json(200, {"id": doc})

    def do_POST(self):
        self.send_json(405, {"error": "use PUT /_reviews/<id>"})


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--directory", "-d", required=True, help="the preview folder (index.html, img/)")
    ap.add_argument("--bind", "-b", default="127.0.0.1", help="address (default 127.0.0.1: this machine only)")
    ap.add_argument("--port", "-p", type=int, default=8765)
    a = ap.parse_args()
    root = os.path.abspath(a.directory)
    if not os.path.isfile(os.path.join(root, "index.html")):
        print(f"preview_server.py: {root}/index.html does not exist; build first", file=sys.stderr)
        return 2
    try:
        srv = ThreadingHTTPServer((a.bind, a.port), functools.partial(Handler, root=root))
    except OSError as e:
        print(f"preview_server.py: cannot listen on {a.bind}:{a.port}: {e}", file=sys.stderr)
        return 2
    host, port = srv.server_address[:2]
    print(f"serving {root} on http://{host}:{port}/ (comments in {root}/reviews)", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
