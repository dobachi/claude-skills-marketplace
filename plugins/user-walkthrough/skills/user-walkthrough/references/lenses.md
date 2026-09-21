# Lenses — concrete probes

Each lens lists probes and the finding shape it tends to produce. Use them as a sweep,
not a script: skip what does not apply to the product and say so under *Not checked*.

## Contents

- 1. Breakage
- 2. Contradiction
- 3. Feedback
- 4. Error recovery and input
- 5. Findability
- 6. Accessibility basics
- 7. Viewport

## 1. Breakage

- Console `error`, `pageerror`, HTTP 4xx/5xx during normal use (see driving.md listeners)
- Spinner or disabled button that never resolves; action that silently does nothing
- Data entered, saved, and not there after reload or re-login
- Crash / stack trace / raw exception text shown to the user
- Same action producing different results on repeat

## 2. Contradiction

The kind a developer misses because each screen is correct on its own.

- A count in a badge, tab, or heading vs the number of rows actually listed
- The same entity named differently across screens, menus, docs, and messages
  (「プロジェクト」 vs 「案件」, "Delete" vs "Remove" for the same action)
- A status shown in the list vs the status on the detail page
- A success message for an action that did not take effect
- Docs, README, `--help`, or on-screen hints that describe behaviour the product
  does not have — or omit a required step
- Dates, times, currencies, and units shown in different formats or time zones
- Mixed language in one UI (Japanese labels, English error messages)
- Settings that appear to save but are not applied

## 3. Feedback

- After each action, can the persona tell whether it succeeded, failed, or is running?
- Long operations — progress, or a frozen-looking screen?
- Destructive actions — confirmation, and a way to undo?
- Where does focus / scroll land after submit? Is the new item visible?

## 4. Error recovery and input

| Input | Probe |
|---|---|
| empty | submit with required fields blank; whitespace-only |
| long | 1,000+ characters; a very long word with no spaces (layout overflow) |
| non-ASCII | Japanese, emoji, combining characters, RTL text |
| format | email / phone / date in the formats real users type (全角数字, `2026/9/1`) |
| boundaries | 0, negative, max, max+1, decimal where integer expected |
| markup | `<b>x</b>`, `'"; --` — rendered as text, not interpreted |
| repetition | double submit, rapid clicks, the same name twice |
| navigation | back button mid-flow, reload mid-form, open in two tabs |
| session | expired login mid-task — is the entered data lost? |

For each error: does the message say **what** went wrong, **where**, and **what to do
next**, in the user's language and vocabulary (not `ValidationError: field_3`)? Is the
user's input preserved so they can correct it?

## 5. Findability

- From the first screen, can the persona find the entry point for each task without
  hints? Count the dead-end clicks.
- Labels in the persona's vocabulary, not the code's (`tenant`, `payload`, `null`)
- Icon-only controls without a label or tooltip
- Empty states — first-time user sees an empty list: does it say what to do?
- Required order that the UI does not reveal ("you must create a team first")

## 6. Accessibility basics

Not a full audit — the cheap checks that catch most real blocks.

- Tab through the whole task: every control reachable, focus visible, order sensible
- Form fields have labels (Playwright `get_by_label` finds them)
- Images and icon buttons have accessible names
- Text contrast obviously low (light grey on white)
- Nothing conveyed by colour alone (red/green status with no text)

## 7. Viewport

- 375px wide: horizontal scroll, overlapping elements, controls off-screen,
  tap targets too small, fixed headers covering content
- Zoom to 200%: does the layout still work?
