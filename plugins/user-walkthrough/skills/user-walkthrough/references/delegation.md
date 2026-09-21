# Delegating the walk to a separate agent

## Contents

- Why a separate agent
- Before briefing — the conductor launches the app
- What the walker gets, and what must not leak
- Briefing template
- Invoking per host
- Parallel walkers
- Receiving the result

## Why a separate agent

Blindness cannot be instructed. "Pretend you have not read the code" does not remove
what is in context — the agent still knows the menu is under Settings and still
reads `tenant` as a meaningful word. A fresh agent that never saw the source is the
only reliable first-time user an agent can provide. The split also separates finding
from verifying: the walker proposes, the conductor reproduces.

Be honest about the isolation: on the same machine a walker *could* open the source.
Keeping it blind is done by the briefing, the working directory, and tool limits, not
by a sandbox. If the walker's transcript shows it read source files, report the walk
as `walker: separate agent (read source — not blind)`.

## Before briefing — the conductor launches the app

Start the app, seed data, create test accounts **yourself**, then hand over only the
entry point. A walker told "run `npm run dev` in ~/src/acme" has been given the repo.

## What the walker gets, and what must not leak

| Give | Do not give |
|---|---|
| Persona, in one or two sentences, in the user's words | Repository path, file names, framework, component or route names |
| Tasks as goals ("export last month's invoices") — or, in procedure mode, the document itself | How to achieve them ("use the Export button in Reports") |
| Entry point — URL, installed command name, API base URL + public API docs | Internal / admin endpoints the persona would not know |
| Test credentials and seed context the persona would have | Known bugs, suspicions, what the developer is worried about |
| User-facing docs (README for users, help pages, tutorial) | Design docs, ADRs, tickets, commit messages |
| Evidence directory and the report format | Your own candidate findings |
| Out-of-bounds list (payments, real email, production) | |

Leak check before sending — the briefing must not contain: a path under the repo,
a source file extension, an identifier in `camelCase` / `snake_case` that the UI does
not display, or the word "bug" attached to a specific feature.

Suspicions are not useless — they bias the walk. If the developer has one, keep it
for yourself and check it in Step 3 or in a second, targeted walk labelled as such.

## Briefing template

Write it in the user's language. Fill every `<…>`; delete lines that do not apply.

```text
You are <persona — e.g. "a small-shop owner using this invoicing service for the first
time. You have not read any code and you do not know how it is built">.

Goal: use the product as this person and report what gets in their way.

Product: <URL | installed command | API base URL>
Credentials / starting data: <…>
User-facing documentation you may read: <URL or file of the user README / help>

<Task mode>
Tasks, in the persona's words:
1. <goal>
2. <goal>

<Procedure mode>
Follow this document exactly, step by step: <doc>. Type commands exactly as written
and click exactly the labels it names. If a step does not work as written, do not
repair it on your own — record it as a finding, then continue only if the document
itself offers a way forward.

Rules:
- Use only what the product and the documentation above show you. Do not open,
  search, or read any source code, repository, configuration, or logs on disk.
- Do not edit any file except inside <evidence dir>.
- Never touch: <out-of-bounds list>.
- After the tasks, try the mistakes a real user makes: empty and very long input,
  Japanese and emoji, double submit, back button, reload mid-form, narrow screen.
- Record where you hesitated or had to guess, even if you then succeeded.
- A finding must be something you saw. Quote messages verbatim. Save screenshots and
  console output to <evidence dir> and reference them.

How to drive: <paste the relevant part of references/driving.md — the Playwright
listener snippet for web, the probe table for CLI, the curl rules for API>.

Return a report in this format and nothing else:
<paste the Deliverable template from SKILL.md, with walker: separate agent>
```

## Invoking per host

| Host | How | Keeping it blind |
|---|---|---|
| Claude Code | Agent tool, `general-purpose` (it needs Bash for the browser) | The briefing only. Its cwd is the repo, so the "do not read source" rule carries the weight — check its transcript afterward |
| Claude Code, stronger | `claude -p "<briefing>"` run from an empty temp directory (agent-delegate `claude-code-delegate`) | Working directory is not the repo; nothing in context points at it |
| Codex / Antigravity | agent-delegate `codex-delegate` / `agy-delegate`, from an empty temp directory | Same; the walker needs write access only to the evidence directory |
| No second agent | Walk yourself | Header says `walker: same agent (had read the source)` |

The walker needs to run a browser and write evidence files, so a pure read-only mode
is not enough. Limit writes to the evidence directory rather than forbidding them.

## Parallel walkers

One persona per walker. Typical splits:

- first-time user vs daily operator vs admin — different tasks, different vocabulary
- task mode vs procedure mode over the same product — they find different things
- desktop vs 375px viewport

Give each its own evidence subdirectory (`walkthrough-evidence/admin/`). Merge in
Step 3; when two walkers hit the same problem, keep one finding and note both
personas in **Where:** — independent rediscovery raises confidence.

## Receiving the result

1. Run `scripts/check_report.py` on each walker's report. Incomplete findings go back
   to the walker once ("F3 has no evidence — add the screenshot or drop it"), not
   silently filled in by you.
2. Skim the walker's transcript for source reads (paths under the repo). If any,
   mark the walk not blind.
3. Reproduce every candidate yourself from a fresh state (SKILL.md Step 3). Update
   `Reproduced:` with your count; drop what does not reproduce.
4. Write the single merged report. The walker's hesitation notes go into Coverage.
