# Driving the product and capturing evidence

## Contents

- Evidence rules
- Web UI (Playwright)
- CLI
- HTTP API
- Things you cannot drive

## Evidence rules

- Save evidence under `walkthrough-evidence/` next to the report, named by finding
  (`F1-step3.png`, `F2-console.txt`). Reference the path in **Evidence:**.
- Quote messages verbatim. A paraphrased error message cannot be searched for in the
  code, and paraphrasing is where "it said something like" becomes invention.
- Record the build you tested (commit hash, URL, `--version`). A report without it
  cannot be re-checked after the next deploy.
- Start each reproduction from a fresh state (new browser context, clean temp dir,
  re-seeded data). "It happens after I clicked around for a while" is not reproducible.

## Web UI (Playwright)

**The walker does not use this.** A separate walker drives the browser only through
`scripts/walk_driver.py` (user verbs, no JavaScript, no selectors — see
`delegation.md`). The raw Playwright below is for **you**: Step 3 reproduction, and
walks where you are the walker and have accepted that the walk is not blind.

Prefer the project's own Playwright if it has one. Otherwise a throwaway script is
enough — do not add Playwright to the project's dependencies.

Every page gets three listeners. Console errors and failed requests are the bugs a user
never reports but always suffers:

```python
# walk.py — uv run --with playwright python walk.py   (or the project's Playwright)
# mkdir -p walkthrough-evidence first
from playwright.sync_api import sync_playwright

log = []
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 1280, "height": 800}, locale="ja-JP")
    page = ctx.new_page()
    page.on("console", lambda m: m.type in ("error", "warning") and log.append(f"console.{m.type}: {m.text}"))
    page.on("pageerror", lambda e: log.append(f"pageerror: {e}"))
    page.on("response", lambda r: r.status >= 400 and log.append(f"HTTP {r.status} {r.request.method} {r.url}"))

    page.goto("http://localhost:3000/")
    page.get_by_role("button", name="新規作成").click()      # find by what the user sees
    page.get_by_label("名前").fill("")                        # empty input probe
    page.get_by_role("button", name="保存").click()
    page.screenshot(path="walkthrough-evidence/F1-step3.png", full_page=True)
    b.close()
print("\n".join(log) or "no console errors / failed requests")
```

- **Locate by role and visible label** (`get_by_role`, `get_by_label`, `get_by_text`),
  not CSS selectors from the source. If you cannot find an element the way a user
  would, that is itself a finding (unlabeled control, icon-only button).
- Mobile probe: `viewport={"width": 375, "height": 740}`, `has_touch=True`.
- Keyboard probe: `page.keyboard.press("Tab")` repeatedly and screenshot where focus
  lands; check that every action is reachable and focus is visible.
- Double submit: click the submit button twice quickly, then count what was created.
- Back / reload: `page.go_back()`, `page.reload()` mid-form, and see what survives.
- `Executable doesn't exist at .../chromium_headless_shell-NNNN` means the Playwright
  package and the downloaded browsers are different versions. Do not reinstall; pass
  `executable_path=` to an existing Chrome/Chromium (`which google-chrome chromium`), or
  point `PLAYWRIGHT_BROWSERS_PATH` at a matching preinstalled set.

## CLI

Run it the way a new user would, and read every word it prints.

| Probe | What to watch |
|---|---|
| no arguments, `--help`, `-h`, `help` | does it say what to do next? are all three consistent? |
| a typo'd subcommand | suggestion, or a stack trace? |
| missing / wrong-type / out-of-range argument | message names the argument and the fix |
| a path that does not exist, no permission, a directory instead of a file | error, not traceback |
| non-ASCII and spaces in paths and values | |
| stdin closed / piped / not a TTY | colour codes and prompts in a pipe |
| Ctrl-C mid-operation | partial output files left behind? |
| exit code after success and after each failure | `echo $?` — failures must be non-zero |
| running the same command twice | idempotent, or duplicates / clobbers? |
| docs examples, copied verbatim | README examples that do not run are contradictions |

Capture with `cmd > out.txt 2> err.txt; echo "exit=$?" >> out.txt`.

## HTTP API

The persona is a developer integrating against it. Use `curl -sS -i` so status and
headers are in the evidence.

- Every documented example request, verbatim — does it work as written?
- Missing field, wrong type, extra field, empty body, wrong content type.
- No auth, expired token, another user's resource ID (should be 403/404, not the data).
- Error body shape: is it the same across endpoints? Does it say which field and why?
- Status codes that contradict bodies (`200` with `{"error": ...}`).
- Pagination edges: page 0, the page after the last, a huge `limit`.
- Same request twice (idempotency of POST/PUT where the docs promise it).

## Things you cannot drive

Native mobile, desktop apps without automation hooks, hardware-backed flows, or an
environment you cannot reach. Do not guess. Options, in order:

1. Ask the user for a way in (staging URL, a build, a test account).
2. Ask the user to perform specific steps and paste screenshots or output; you then
   analyse what they show. Mark findings `Reproduced: observed by user`.
3. If the user accepts a static pass, mark every finding `Reproduced: not run (static)`.
   The checker refuses a Blocker on that basis — a static guess is at most Major.
