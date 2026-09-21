# Answer key for evals/files/todo-app

Kept outside `files/todo-app/` because that directory is served to, and read by, the
walker. Nothing in the served files may hint at the defects.

| ID | Where | Defect | Lens |
|---|---|---|---|
| D1 | index.html, delete handler | 「残り n 件」 is not recalculated on delete (only on add / toggle) | contradiction |
| D2 | index.html, submit handler | whitespace-only title is accepted and adds a blank row | error recovery |
| D3 | index.html, submit handler | titles over 30 chars show English `Error: invalid length` with no guidance | contradiction (mixed language) / feedback |
| D4 | index.html, 「すべて完了」 | `ReferenceError: undefinedHelper is not defined` in the console | breakage |
| D5 | README.md step 3 | names a 「登録」 button; the app's button is 「追加」 | contradiction (docs vs behaviour) |
| D6 | README.md step 5 | promises a confirmation dialog on delete; the app deletes immediately | contradiction (docs vs behaviour) |

Found by the first sandboxed walk, not seeded: README.md shows as mojibake, because
`python3 -m http.server` serves `.md` as `text/markdown` with no charset. A legitimate
finding for this setup (a real static host can do the same); do not count it against
a report. D5/D6 were still found through the garbling.

Also expected in a run: a favicon 404 in the console. It is environment noise, not a
product finding worth more than Minor — a report that rates it Major is inflating.

Serve with `python3 -m http.server 8765` from `files/todo-app/`.
