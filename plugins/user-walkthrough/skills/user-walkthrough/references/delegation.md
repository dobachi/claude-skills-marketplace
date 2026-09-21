# Delegating the walk to a separate agent

## Contents

- Why a separate agent
- The run, in order
- walk-policy.json
- What the walker gets, and what must not leak
- Briefing template
- Other hosts and fallbacks
- Parallel walkers
- Receiving the result
- What is still not enforced

## Why a separate agent

Blindness cannot be instructed. "Pretend you have not read the code" does not remove
what is in context — the agent still knows the menu is under Settings and still reads
`tenant` as a meaningful word. A fresh agent that never saw the source is the only
first-time user an agent can provide. And a fresh agent *can* still go and look, so
its reach is enforced by the scripts below, not by the briefing alone.

## The run, in order

`$SK` is this skill's directory. Everything under `$RUN` is per walk.

```bash
RUN=$(mktemp -d); mkdir -p "$RUN/work" "$RUN/log"
cp "$SK/scripts/walk_driver.py" "$RUN/work/"          # the walker's only way in
# 1. Start the product yourself (dev server, seed data, test account). Never hand the
#    walker a start command — that is a path into the repo.
# 2. Write $RUN/walk-policy.json (below) and $RUN/work/briefing.md (template below).
#    Copy user-facing docs the walker may read into $RUN/work/docs/ if they are files.
# 3. Browser server — your side, outside the sandbox. Keep it running in the background.
python3 "$SK/scripts/walk_driver.py" serve --policy "$RUN/walk-policy.json" \
    --work "$RUN/work" --log "$RUN/log" [--chrome /usr/bin/google-chrome]
#    (needs Playwright: `uv run --with playwright python …` works without installing)
# 4. The walker, in the sandbox. Refuses to start if a forbidden path would be visible.
"$SK/scripts/walk_sandbox.sh" claude "$RUN/work" "$RUN/walk-policy.json" "$RUN/log"
# 5. Audit, then read the instruments, then verify (SKILL.md Step 3).
python3 "$SK/scripts/audit_walk.py" --policy "$RUN/walk-policy.json" --log "$RUN/log" --work "$RUN/work"
python3 "$SK/scripts/check_report.py" "$RUN/work/report.md"
```

Result layout:

| Path | Who can see it | Contents |
|---|---|---|
| `$RUN/work/` | walker + you | briefing, driver client, `evidence/step-NNN.png`, the walker's `report.md` |
| `$RUN/log/actions.jsonl` | you | every driver request with its result (`ok` / `failed` / `refused`) and URL |
| `$RUN/log/instruments.jsonl` | you | console errors/warnings, page errors, HTTP ≥ 400 — each tagged with the step |
| `$RUN/log/transcript.jsonl` | you | the walker's full tool-call record (stream-json) |

## walk-policy.json

```json
{
  "start_url": "http://localhost:3000/",
  "allowed_urls": ["http://localhost:3000/help/*", "http://localhost:3000/docs/start"],
  "allowed_commands": [],
  "forbidden_paths": ["/home/me/src/acme", "/home/me/design-notes"],
  "forbidden_terms": ["TenantStore", "tenant_id", "feature_flag_v2"],
  "viewport": [1280, 800],
  "locale": "ja-JP"
}
```

| Field | Used by | Meaning |
|---|---|---|
| `start_url` | driver, audit | where the browser opens. Exact — it does not open the whole host |
| `allowed_urls` | driver, audit | URLs a user could know without a link (typed from the docs). Exact, or prefix when ending in `*` |
| `allowed_commands` | sandbox, audit | for CLI/API products — the product's documented commands (`acme`, `curl`). Empty for web |
| `forbidden_paths` | sandbox, audit | **required**. Must be invisible; appearing in a walker's command means it knew them |
| `forbidden_terms` | audit | internal names the UI never shows. A walker using one knew something a user cannot |

Any link visible on the current page is always reachable — a user can click it.

## What the walker gets, and what must not leak

| Give | Do not give |
|---|---|
| Persona, in one or two sentences, in the user's words | Repository path, file names, framework, component or route names |
| Tasks as goals ("export last month's invoices") — or, in procedure mode, the document | How to achieve them ("use the Export button in Reports") |
| The product URL / documented command | Internal or admin endpoints the persona would not know |
| Test credentials and seed context the persona would have | Known bugs, suspicions, what the developer is worried about |
| User-facing docs (README for users, help pages, tutorial) | Design docs, ADRs, tickets, commit messages |
| The report format | Your own candidate findings |

Before sending, check the briefing contains no `forbidden_paths` entry, no
`forbidden_terms` entry, no source file extension, and no feature named together with
the word "bug". Suspicions bias the walk — keep them for Step 3 or a second, labelled
targeted walk.

## Briefing template

Write it in the user's language; fill every `<…>`; delete what does not apply.

```text
You are <persona — e.g. "a small-shop owner using this invoicing service for the first
time. You have not read any code and do not know how it is built">.

Goal: use the product as this person and report what gets in their way.

Product: <URL — a browser is already open on it | command>
Documentation you may read: <URL, or docs/ in this directory>

<Task mode>
Tasks, in the persona's words:
1. <goal>
2. <goal>
<Procedure mode>
Follow <document> exactly, step by step. Type commands exactly as written and click
exactly the labels it names. If a step does not work as written, do not repair it —
record it as a finding, and continue only if the document itself offers a way forward.

How to act: every action goes through `python3 walk_driver.py <verb>` (run
`python3 walk_driver.py --help`). One action per command; read what it prints — that is
what is on screen. Screenshots it saves are in evidence/ and you may open them.
<CLI/API products: "You may also run: <allowed_commands>, as documented.">

After the tasks, try the mistakes real users make: empty and very long input, Japanese
and emoji, double submit, back, reload mid-form, a narrow screen (viewport 375x740).
Note where you hesitated or had to guess, even when you then succeeded.

Write report.md in this directory, in this format, and nothing else:
<paste the Deliverable template from SKILL.md, header walker: separate agent>
Write each step as what a user does ("click 「保存」", "reload the page"), not as a
walk_driver.py command. Actual = what you saw, not what you think caused it.
```

## Other hosts and fallbacks

| Situation | Run the walker with | Header says |
|---|---|---|
| Claude Code + bubblewrap (default) | `walk_sandbox.sh claude` | `walker: separate agent (sandboxed)` |
| Codex / Antigravity + bubblewrap | `walk_sandbox.sh exec <work> <policy> -- codex exec …` (or `agy …`), with `WALK_RO` for the agent's install dir. Make it emit the generic transcript (`{"tool","input","denied"}` per line) or keep its own log for the audit | `walker: separate agent (sandboxed)` |
| No bubblewrap (macOS, locked-down CI) | `claude -p` from an empty temp dir, same allowlist flags; driver and audit still apply | `walker: separate agent (no OS sandbox)` |
| No second agent | walk yourself through `walk_driver.py` anyway — the driver still keeps you to user verbs | `walker: same agent (had read the source)` |

`walk_sandbox.sh claude` gives the walker a config directory holding only a copy of
your credentials — never `~/.claude`, whose `projects/` keeps past transcripts that
quote this repository. The copy is deleted when the walker exits.

## Parallel walkers

One persona per walker, each with its **own** `$RUN` (own work dir, own driver server,
own socket, own log). Typical splits: first-time user vs daily operator vs admin; task
mode vs procedure mode; desktop vs 375px. Merge in Step 3; when two walkers hit the
same problem, keep one finding and note both personas — independent rediscovery raises
confidence.

## Receiving the result

1. `audit_walk.py`. Exit 1 → the walk left a user's reach; header says `not blind`,
   and findings that depend on the leak are unverified. `ATTEMPT` lines (denied or
   refused) are fine — they show where the walker pushed.
2. `check_report.py` on the walker's report. Incomplete findings go back to the walker
   once, not silently filled in by you.
3. `instruments.jsonl` → attach console / HTTP errors to the finding at the same step.
   An instrument event with no finding is a candidate of its own: something broke that
   the user did not see — check whether it matters.
4. Reproduce every candidate yourself from a fresh state; update `Reproduced:`.
5. Write the single merged report. Hesitation notes go into Coverage.

## What is still not enforced

- **The network is shared.** The walker must reach its model API and the product on
  localhost, so an agent that ignored its allowlist could fetch raw HTML with a script.
  The allowlist blocks that and the audit reports it; the OS does not.
- **What the model already knows.** A widely published product may be in the model's
  training data. Nothing here can remove that; a walker quoting behaviour it never
  observed is caught by `check_report.py` only if it words it as speculation.
- **The walker sees its own credentials.** It needs them to run.
