---
name: user-walkthrough
description: >-
  Walks through an app or service AS ITS USER, actually launching and operating it
  (browser, CLI, API) with a persona and tasks, or following its README/manual
  procedure verbatim, to find usability friction, contradictions (screen vs screen,
  docs vs behaviour), unhelpful errors, and bugs. Preferably delegates the walk to a
  separate agent that has not read the source, then re-verifies each finding. Returns
  a severity-ranked report where every finding has reproduction steps, expected vs
  actual, and observed evidence, WITHOUT changing the code. Use when the user says
  "利用者目線で確認して", "ユーザー目線で触ってみて", "使いづらいところを探して",
  "不具合を探して", "動作確認して", "矛盾がないか見て", "手順に従って確認して",
  "手順どおりに動くか試して", "READMEの通りにやってみて", "UXレビュー",
  "walk through the app as a user", "follow the docs and see if it works", "dogfood
  this", "exploratory test". Read-only. Fixing goes to the developer or a dev skill,
  source review to code-reviewer, design to frontend-design, undefined behaviour to
  requirements-stories.
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# User Walkthrough

## Core idea: observe, don't imagine

A developer reading their own code cannot see the product the way a user does. This
skill closes that gap by **using the product** — clicking, typing, running commands,
reading the messages it prints — as a specific person trying to get something done,
and reporting where that person gets stuck, misled, or broken.

Two things separate this from "look at the code and tell me what's confusing":

1. **Every finding is observed.** It happened on screen, in the terminal, or in a
   response body, and it comes with the steps that make it happen again. "This could
   be confusing" without having watched it confuse is not a finding.
2. **Nothing is changed.** The deliverable is a report. Fixing is a separate step the
   developer approves — mixing the two hides what was found under what was changed.

| skill | job | boundary with this skill |
|-------|-----|--------------------------|
| **user-walkthrough** (this) | operate the product as a user, report what breaks | — |
| code-reviewer / `/code-review` | read the source for defects | you report symptoms; they find causes in code |
| web-frontend-dev / web-api-dev / cli-tool-dev | build and fix | accepted findings go to them (or the developer) |
| frontend-design | visual/aesthetic direction | you flag "users missed the button"; they redesign |
| requirements-stories | write acceptance criteria | "nobody defined what should happen here" goes to them |
| `run` (built-in) | launch the app | you may use it to start the app; the walkthrough is yours |

## Workflow

### Step 0 — Scope (ask only what you cannot find)

Establish, reading the README / package files / routes first and asking only for gaps:

- **Target and how to run it** — URL, start command, CLI entry point, API base.
  Test credentials or seed data if login is needed.
- **Persona** — who is the user? (first-time visitor / daily operator / admin /
  developer calling the API). Default to *a first-time user who has not read the code*.
- **Tasks** — 3–7 concrete things that persona comes to do ("sign up and create the
  first project", "export last month's report as CSV"). Derive from README, nav, and
  routes if not given; show the list before starting.
- **Out of bounds** — production data, payments, sending real email. Never operate on
  production or trigger irreversible external effects without explicit permission.
- **Mode** — which of the two below.

| Mode | When | The script |
|---|---|---|
| **Task** (default) | "利用者目線で確認して", "使いづらいところを探して" | the persona's tasks; how to do them is up to the walker |
| **Procedure** | "手順に従って確認して", "READMEの通りにやってみて", a named manual / tutorial / runbook | the document's steps, executed **verbatim** in order. Copy commands exactly, click exactly the labels it names. The walker does not repair a step; a step that does not work as written is a finding (`contradiction`), and the walk records the fix only if the doc gives a way forward |

Procedure mode finds what task mode cannot: the missing prerequisite, the renamed
button, the command that changed flags, the screenshot from two versions ago. Quote
the document line in **Where:** alongside the screen or command.

If the app cannot be started in this environment, say so, ask how to reach it, and
do not silently fall back to reading code. A static pass is allowed only if the user
accepts it, and every finding from it is marked `Reproduced: not run (static)`.

### Who walks — a separate agent, by default

The agent that scoped the work has usually read the source, the routes, maybe the
fix history. It knows the hidden route and the intended meaning of every label, and
it cannot un-know them. That is exactly the blindness this skill exists to remove.

So when the host can start another agent (a subagent, `claude -p`, another CLI via
agent-delegate), **split the roles**:

| Role | Who | Sees | Does |
|---|---|---|---|
| Conductor | you | everything | Step 0 scope, launch the app, brief the walker, Step 3 verification, the report |
| Walker | a fresh agent | persona, tasks or the procedure document, entry URL/command, user-facing docs only | Steps 1–2; returns candidate findings in the report format. **No source, no repo tour, no edits** |

- Several personas or areas → several walkers in parallel, one persona each.
- The walker's findings are **candidates**. You reproduce each one yourself from a
  fresh state in Step 3; what you cannot reproduce is dropped or reported as `1/3`.
- The briefing is the whole trick: it must not leak what the source knows (internal
  names, where the feature "really" is, known bugs). Prompt template, leak checklist,
  and per-host invocation → `references/delegation.md`.

If no second agent is available, walk yourself and write
`walker: same agent (had read the source)` in the report header — the reader should
know the walk was not blind.

### Step 1 — Walk the happy path as the persona

(Done by the walker when roles are split.) Do each task — or each step of the
procedure — the way the persona would: from the entry point, using only what the UI,
`--help`, and user-facing docs tell you — not knowledge from the source. Record for each task
whether it was **completed / completed with friction / blocked**, and where you
hesitated. Hesitation is data: if you had to guess which button, the user will too.

How to drive each kind of product (Playwright, CLI, API), and how to capture
console errors, failed requests, and screenshots as evidence →
`references/driving.md`.

### Step 2 — Leave the happy path

Now probe like a real user who makes mistakes. Sweep the lenses in
`references/lenses.md`:

1. **Breakage** — crashes, 5xx, uncaught console errors, stuck spinners, lost data.
2. **Contradiction** — the same thing named, counted, or stated two ways (screen vs
   screen, UI vs docs, list count vs detail, message vs actual behaviour).
3. **Feedback** — did the user learn the action succeeded, failed, or is in progress?
4. **Error recovery** — empty / long / invalid / non-ASCII input, double submit,
   back button, reload mid-flow, expired session. Does the message say what to do next?
5. **Findability** — can the persona discover the feature and understand the labels?
6. **Accessibility basics** — keyboard-only operation, focus, labels, contrast.
7. **Viewport** — a narrow (mobile) width, if the product is a web UI.

### Step 3 — Reproduce and verify each candidate

(Done by the conductor, never by the walker that found it.) For every candidate:
reproduce it **from a fresh state** (new page / new session /
clean data) following your own written steps. Record `Reproduced: 2/2`, `1/3`, etc.
Then argue against it — is this a real user problem, or my taste? Is it the app, or
my environment (missing env var, wrong seed)? Drop what does not survive. An
environment problem is reported once under *Not checked*, not as a product bug.

**Findings are discovered, not allocated.** A solid product gets a short report. Never
inflate a Minor to a Major to make the walkthrough look productive.

### Step 4 — Report, then stop

Write the report (below), save it (default `walkthrough-report.md` in the project
root, or where the user says), and run the checker:

```bash
python3 <skill-dir>/scripts/check_report.py walkthrough-report.md
```

Exit 0 means every finding has steps, expected, actual, evidence, and reproduction
status, and no Blocker rests on an unobserved claim. Exit 1 lists what is missing —
fix the report, not the threshold. Then stop; do not edit the product.

## Severity

- **Blocker** — the persona cannot complete a core task, loses data, or hits a crash /
  5xx. Must be observed (`Reproduced` is not `0/…` or `not run`).
- **Major** — the task completes but the persona is misled (wrong number, contradictory
  state, success shown on failure) or needs a workaround they are unlikely to find.
- **Minor** — real friction that slows but does not mislead.

Classify the kind as well: `bug` / `contradiction` / `usability` / `a11y`.

## Deliverable — the walkthrough report

```markdown
# Walkthrough — <product> (persona: <who>, mode: task|procedure <doc>, walker: separate agent|same agent, build: <commit/URL/version>, date: <YYYY-MM-DD>)

**Verdict:** <1–2 sentences: can the persona do what they came for? the single biggest problem.>

## Coverage
| Task | Result | Note |
|---|---|---|
| Sign up and create first project | completed with friction | F2 |

## Findings (most severe first)
### [Blocker] <title> · bug
- **Where:** <screen / URL / command>
- **Steps:**
  1. <step>
  2. <step>
- **Expected:** <what the persona expected, and why they would expect it>
- **Actual:** <what happened — observed, not speculated>
- **Evidence:** <screenshot path / console line / response body / terminal output>
- **Reproduced:** 2/2
- **Direction:** <what should change, not the patch>

## Not checked
<tasks, lenses, browsers, roles not covered, and why — including environment blockers>

## Handoffs
- F1, F3 → developer / web-frontend-dev
- F4 (no defined behaviour for empty state) → requirements-stories
```

Japanese labels (場所 / 手順 / 期待 / 実際 / 証拠 / 再現 / 指摘 / 未確認) are accepted by
the checker when the report is written in Japanese.

## Anti-patterns

| Anti-pattern | Why it fails | Instead |
|---|---|---|
| Reading the code and guessing what users find confusing | Produces plausible opinions nobody observed; developers rightly ignore them | Run it; report only what happened |
| "The error message could be clearer" | No reader, no consequence, no steps | Quote the message, say what the persona tried next and failed |
| Using source knowledge to complete tasks | You find the hidden route; the user never will | Use only what the UI / `--help` exposes |
| Fixing bugs as you find them | The report loses the finding; the fix is unreviewed | Report first; fixing is a separate approved step |
| Reporting environment trouble as product bugs | Wastes the developer's time on a wrong lead | Put it under *Not checked* with what you tried |
| Padding with cosmetic nits to look thorough | Buries the one Blocker that matters | Short list, severity-ranked |
| Walking only the happy path | Most real bugs sit on the error and edge paths | Step 2 lenses, every time |
| Briefing the walker with the repo layout or "the button is under Settings" | The walker inherits your blindness; the walk is no longer a user's | Persona, tasks, entry point, user-facing docs — nothing else |
| Shipping the walker's findings unverified | A fresh agent also mis-clicks and misreads | Conductor reproduces every candidate in Step 3 |
| In procedure mode, silently fixing a broken step and moving on | The one finding the user asked for disappears | Report the step as written vs what happened, then continue only if the doc allows |
| Poking production or real payment/email flows | Irreversible side effects | Staging/local only unless explicitly permitted |

## References

- `references/driving.md` — how to operate web UIs (Playwright), CLIs, and APIs, and
  capture evidence (screenshots, console errors, failed requests, exit codes)
- `references/lenses.md` — concrete probes for each lens in Step 2
- `references/delegation.md` — briefing a separate walker agent: prompt template,
  what must not leak, parallel personas, how to invoke per host
- `scripts/check_report.py` — report checker; exit 0 complete / 1 findings / 2 not a walkthrough report
