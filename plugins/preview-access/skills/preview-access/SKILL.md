---
name: preview-access
description: >-
  Puts the current work in front of a user who may not be at this machine. Works out from the
  project and the conversation what "the thing to look at" is (a preview server, a built site,
  a dev server, a PDF, a release, a PR, a published page), finds or starts it the way THIS
  project does it, proves it is reachable from another device, and hands over direct links to
  what changed, labelled. Not tied to any one tool. Use when the user says "preview", "show me",
  "restart the preview", "give me the URL again", "I am on another PC / my phone",
  "where can I see this", 「プレビュー」「プレビュー再起動」「URL を示して」「再度 URL」
  「他の PC から見たい」「どこで見られる？」, and proactively at the end of any change the user
  will want to look at. Hands off launching and driving an app for verification to run, and
  build failures to auto-build.
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# preview-access

One job: after work is done, the user can open it — from wherever they are — without asking twice.

It exists because the same four requests kept coming back in one session: "preview it", "restart
it on the tailscale address", "restart the preview" (again, after every change), and "I am on
another PC, show me the URLs again". Each was answered by re-deriving the same steps.

## What "the thing to look at" is depends on the context

Do not assume a tool. Decide from the project and the conversation, in this order:

1. **What the conversation already used.** If a preview was started earlier in this session, that
   method and that address are the answer. Reuse them; do not invent a second one.
2. **What the project says.** `README`, `HANDOFF`, `CLAUDE.md`, `Makefile`, `package.json`
   scripts, `justfile`, a `scripts/` directory. A project that documents its preview command has
   usually already hit the problems you are about to hit.
3. **What kind of output it is.**

| Output | What the user opens |
|---|---|
| Site or book built to static files | The output directory, served over HTTP |
| App with a dev server | The dev server |
| A single file (PDF, image, deck) | The file, sent or served. A path on this machine is useless on another one |
| Something already published | Its real URL (release, PR, deployed page, artifact) |
| Nothing viewable (a library, a refactor) | Say so. Point at the diff or the test output instead |

If two answers are plausible and they differ in cost (a rebuild of several minutes versus a link
that already exists), give the cheap one first and offer the other.

## Procedure

```
1. STATE     What is already running? What does it serve, and from which address?
2. FRESH     Does it reflect the latest change? If not, rebuild by the project's method.
3. REACH     Is it reachable from where the user is? Bind accordingly.
4. PROVE     Fetch it yourself. A listening port is not a served page.
5. HAND OVER Root link, then direct links to what changed, each with its name.
```

### 1. State

Look before starting anything. A second server on a new port leaves the user with two addresses
and one of them stale.

```bash
ss -ltnp 2>/dev/null | grep -v '127.0.0.53'      # what listens, on which address, which PID
```

### 2. Fresh

If the output was built before the last edit, the link shows old content and the user will report
a bug that is not there. Rebuild first. If a live-reload server has stopped reflecting edits,
do not keep restarting it: switch to a plain build plus a static file server, and say that you did.

Deleting the output directory invalidates a server that was started inside it. Restart the server
afterwards.

### 3. Reach

`localhost` only works on this machine. When the user is, or might be, elsewhere:

- Find an address the other device can reach: a VPN/overlay address (`tailscale ip -4`), then a
  LAN address. Use what the user asked for earlier in the session if they named one.
- Bind the server to that address, not to `0.0.0.0`, unless the user asks for wider exposure.
  The preview may contain unpublished work.
- A tunnel or a public upload publishes the content. Ask first.

### 4. Prove

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://<addr>:<port>/<a page that changed>
```

Check a page that changed, not only the root. Report anything that is not a 200.

### 5. Hand over

- The root link.
- **A direct link for each thing that changed**, named the way the user names it ("Chapter 8,
  Identity"), not by file name alone. Derive the list from `git status` and the last commits, or
  from what was just edited.
- Where on the page to look, when the change is small.
- Whether what they see is committed, uncommitted, or released.

When the user only asks for the links again, do steps 1 and 4 and answer. Do not rebuild.

## Stopping and restarting

Find the PID from the listening socket and kill that PID.

```bash
ss -ltnp | grep ':<port> '        # -> pid=NNNN
kill NNNN
```

Never `pkill -f <pattern>` or `pgrep -f | xargs kill` with a pattern that also appears in your own
command line: the shell running the command matches the pattern and kills itself.

Start a server so that it outlives the command that launched it (background execution or
`nohup … &`), and do not wait on it with `sleep`.

## Rules

1. **Reuse before starting.** One address per project per session.
2. **Never hand over a link you did not fetch.**
3. **Never hand over `localhost` without saying it only works on this machine.**
4. **The project's own method wins** over the one you know best.
5. **Links are part of the report.** Any message that says "done" about something viewable ends
   with where to view it. The user should not have to ask.
6. **Keep the method.** When a project needed a workaround to preview, write it where the project
   keeps such notes, so the next session starts from it.

## Anti-patterns

| Anti-pattern | Why it fails | Instead |
|---|---|---|
| Assuming the tool from the last project | The preview command, port, and output directory differ per project | Read the project first |
| "The preview is running" with no link | The user is on another device and has no scrollback | Repeat the links every time |
| Root link only | The user hunts for the change through a 200-page site | Direct, named links to what changed |
| A new port on every restart | Bookmarks and open tabs on the other device break | Same address, same port |
| Restarting a live-reload server that keeps going stale | Same failure, a minute later | Plain build, static server |
| Binding to `0.0.0.0` by default | Unpublished work exposed to the whole network | Bind to the one address the user needs |
| Rebuilding when asked only for the URL | Minutes of waiting for an answer that was one line | Check it is up, answer |

## Hand-offs

- Launching and driving an app to verify that a change works: `run`.
- A build that fails: `auto-build`.
- Publishing a release with downloadable files: `commit-safe`.
