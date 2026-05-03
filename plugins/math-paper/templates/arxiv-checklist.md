# arXiv Submission Checklist

Walk through this list before uploading. Mark each item.

## Source Bundle

- [ ] Single main `.tex` file (or main + `\input` files; consider flattening with `latexpand`).
- [ ] `.bbl` file is included alongside the `.tex`. Do **not** rely on uploading only `.bib` — arXiv runs BibTeX but `.bbl` is more reliable.
- [ ] All figures present in the bundle. Accepted: PDF (preferred for vector), PNG, JPG, EPS. Avoid `.bmp`, `.tif`.
- [ ] No absolute paths in `\includegraphics{...}`.
- [ ] Custom `.cls` / `.sty` files included if not on arXiv's standard list.
- [ ] Bundle size under arXiv's per-submission limit (default 10 MB; higher caps available on request).

## Cleanup

- [ ] No `\todo{...}`, `\TODO`, `\fixme`, `% XXX` notes visible in the rendered PDF. Use `\usepackage[disable]{todonotes}` for the final build.
- [ ] Debug packages disabled: `showkeys`, `showframe`, `lineno` (unless required by the journal).
- [ ] Comments removed if they contain author identification (e.g., `% by Alice Smith`).
- [ ] No leftover `\listoftodos`, `\printindex` placeholders.
- [ ] Hyperlink colors set tastefully (`\hypersetup{colorlinks=false}` or muted colors).
- [ ] PDF metadata sanitized if double-blind (`exiftool -all= file.pdf`).

## Compile Check

- [ ] `pdflatex` (or `xelatex` / `lualatex`) compiles with no errors.
- [ ] BibTeX runs cleanly; no "warning--I didn't find a database entry for..." messages.
- [ ] Final pass produces no `??` for `\ref`/`\eqref`/`\cref`/`\cite`.
- [ ] No "overfull hbox" warnings in critical regions (display equations, table cells).
- [ ] `pdftotext` output of the final PDF is sensible (a basic accessibility check).

## Metadata (entered on arXiv submission form)

- [ ] **Title** matches the `\title{...}` in the source.
- [ ] **Abstract** under arXiv's character limit (1920 chars typical). Plain text; convert math via Unicode or `$...$`.
- [ ] **Authors** with affiliations.
- [ ] **MSC2020 codes** (1–3 codes; primary first). Required by most math journals.
- [ ] **Keywords** (5–8). Some categories require ACM CCS or PACS in addition.
- [ ] **Primary category** + cross-lists. For math papers: `math.XX` primary; common cross-lists include `stat.ML`, `cs.LG`, `math-ph`.
- [ ] **Journal-ref** if accepted (leave blank for preprints).
- [ ] **DOI** added later if published.
- [ ] **Comments** field: number of pages, figures, version notes ("v2: fixed proof of Theorem 3").

## Double-Blind Submission Variant

If submitting to a double-blind venue (separate from arXiv):

- [ ] `\author{...}` and `\thanks{...}` stripped (or use `\anonymous` flag if class supports).
- [ ] Self-citations rewritten in third person ("Smith [12] proved..." not "We proved [12]").
- [ ] Acknowledgements section removed.
- [ ] PDF metadata stripped.
- [ ] Repository / dataset URLs anonymized (e.g., via `anonymous.4open.science`).
- [ ] Author-revealing filenames in figures or supplementary files renamed.

## After Upload

- [ ] Inspect the auto-generated PDF on arXiv before announcing — fonts, figures, TOC all rendered correctly.
- [ ] Verify the abstract preview on the submission page.
- [ ] Hold submission until midnight UTC (arXiv announcement window) if timing matters for priority.
