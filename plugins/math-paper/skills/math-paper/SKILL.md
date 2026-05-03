---
name: math-paper
description: Mathematical paper writing support — notation consistency, theorem/proof structure, equation cross-references, and journal/arXiv submission preparation. Works with LaTeX and Markdown+math (pandoc-crossref / MyST). Triggers on .tex/.bib files, math-heavy Markdown, journal class files (elsarticle, IEEEtran, acmart, siamart, amsart), and user requests about theorems, proofs, equation numbering, or arXiv submission.
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Mathematical Paper Writing Support

Targeted assistance for authors writing mathematical papers in LaTeX or Markdown+math. Covers notation consistency, theorem/proof structure, equation cross-referencing, and journal/arXiv submission preparation.

This skill **delegates** to other plugins for adjacent concerns instead of duplicating them — see *Integration with Other Skills* below.

## When to Activate

Activate this skill when any of the following is true:

- The user is editing `.tex`, `.bib`, or `.bbl` files.
- A Markdown file contains `$...$`, `$$...$$`, `\begin{equation}`, `\begin{align}`, or `\begin{theorem}`.
- A repository contains a journal class file: `elsarticle.cls`, `IEEEtran.cls`, `acmart.cls`, `siamart.cls`, `amsart.cls`, `revtex4-2.cls`, etc.
- The user asks about: theorems, lemmas, proofs, equation numbers, `\label`/`\ref`/`\eqref`, MSC codes, arXiv submission, journal style, double-blind review, `latexdiff`, response to reviewers.

When activating, briefly state which workflow you're using (e.g., "Running notation consistency check") so the user can redirect.

## Workflow 1: Notation Consistency (Symbol Ledger)

Maintain a **Symbol Ledger** — a running table of every mathematical symbol used in the paper. Update it as you read the source.

| Symbol | Meaning | First use | Font convention |
|--------|---------|-----------|-----------------|
| $X$ | Banach space | Sec. 2, Def. 2.1 | italic uppercase |
| $\mathbf{x}$ | element of $X$ | Sec. 2, Def. 2.1 | bold lowercase |
| $\mathcal{F}$ | $\sigma$-algebra on $\Omega$ | Sec. 3 | calligraphic |
| $\mathbb{R}$ | real numbers | Sec. 1 | blackboard bold |

### Checks to perform

1. **Polysemy detection** — flag any symbol used with two or more incompatible meanings (e.g., `\sigma` as both standard deviation and a permutation in the same paper).
2. **Use-before-definition** — flag symbols that appear before their formal definition. Suggest forward references (e.g., "(see Definition 3.4)") or reorder.
3. **Font convention drift** — compare each occurrence of a symbol against its first-use convention. Flag drift (e.g., $X$ as italic in §2 but $\mathbf{X}$ as bold in §5).
4. **LaTeX macros** — read `\newcommand`, `\renewcommand`, `\DeclareMathOperator`, `\providecommand`. Report:
   - Duplicate definitions (`\newcommand` redeclared)
   - Unused macros
   - Inline `\mathbb{R}` etc. that should be promoted to a macro for consistency
5. **Markdown variant** — extract symbols from `$...$` / `$$...$$` blocks and run the same checks.

### Conventional fonts (default suggestions)

- Vectors: bold lowercase `\mathbf{x}` (or `\boldsymbol{x}` for Greek)
- Matrices: bold uppercase `\mathbf{A}` or italic uppercase `A`
- Sets: blackboard bold for canonical sets (`\mathbb{R}`, `\mathbb{N}`); calligraphic for ad-hoc families (`\mathcal{F}`)
- Operators: roman via `\operatorname{...}` or `\DeclareMathOperator`
- Probability: $\mathbb{P}$, $\mathbb{E}$, $\mathrm{Var}$ (declared as operator)

State the chosen convention up front and apply it consistently.

## Workflow 2: Theorem and Proof Structure

### Recommended environment setup (LaTeX, amsthm)

```latex
\usepackage{amsthm,amsmath,amssymb}
\theoremstyle{plain}
\newtheorem{theorem}{Theorem}[section]
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{proposition}[theorem]{Proposition}
\newtheorem{corollary}[theorem]{Corollary}
\theoremstyle{definition}
\newtheorem{definition}[theorem]{Definition}
\newtheorem{example}[theorem]{Example}
\theoremstyle{remark}
\newtheorem{remark}[theorem]{Remark}
```

Sharing the counter (`[theorem]`) makes Lemma 2.3 follow Theorem 2.2 — recommended for most math journals.

### Theorem statement style

Separate **hypotheses** and **conclusion** explicitly:

```
Theorem 2.5. Let X be a compact Hausdorff space and f : X -> R continuous.
Then f attains its maximum.
```

For applied/ML papers, an explicit "Assumptions" block before the theorem improves reusability.

### Proof structure

- For proofs longer than ~10 lines, label steps: **Step 1 (Reduction).** ... **Step 2 (Estimate).** ...
- Or number internal claims: "**Claim 1.** ... *Proof of Claim 1.* ..."
- End with `\qed` or `\end{proof}` (amsthm inserts $\square$ automatically).
- Cross-reference within proof: "by (\ref{eq:bound}), $f(x) \le \dots$".

### Dependency graph

When the user asks "what does Theorem 4.2 depend on?" or before reorganizing, extract the dependency chain:

```
Theorem 4.2  ← Lemma 4.1, Proposition 3.5, Definition 2.3
Lemma 4.1    ← Definition 2.3, [Knuth 1973, Thm. 2]
Proposition 3.5 ← Lemma 3.4, Definition 2.3
```

Surface dependencies that span sections — those are the most likely to break under reorganization.

### QED / proof-end audit

Search for `\begin{proof}` without matching `\end{proof}`, and for paragraphs that look like proofs but lack the environment.

## Workflow 3: Equation Cross-References and Numbering

### LaTeX

- **Label naming**: prefix by kind — `eq:`, `thm:`, `lem:`, `prop:`, `cor:`, `def:`, `fig:`, `tab:`, `alg:`, `sec:`. Makes search and audit trivial.
- **Reference**: use `\eqref{eq:foo}` for equations (renders as `(2.3)`), `\cref` (cleveref) elsewhere if loaded.
- **Numbering scheme**: per-section (`\numberwithin{equation}{section}`) is standard for math journals; flat numbering acceptable for short notes.
- **Suppress trivial numbers**: use `\nonumber`, `\notag`, or `equation*`/`align*` for equations never referenced.

### Audit checks

1. **Unreferenced labels** — `\label{X}` with no matching `\ref`/`\eqref`/`\cref`. Either reference it or drop the label (and possibly suppress the number).
2. **Dangling references** — `\ref{X}` / `\eqref{X}` with no matching `\label`. Likely typo or removed equation.
3. **Label collisions** — duplicate `\label{X}`. LaTeX warns but the warning is easily missed.
4. **Inline-vs-display** — single-symbol displayed equations (`\[ x \]`) should usually be inline (`$x$`) unless emphasis is intended.

### Markdown variants

- **pandoc-crossref**: label with `{#eq:foo}` after the equation, reference with `[@eq:foo]` or `$$...$$ {#eq:foo}`.
- **MyST**: label with `(label)=` line, reference with `` {eq}`label` `` or `[](label)`.
- **Quarto**: same as pandoc-crossref.

Apply the same audit rules (unreferenced, dangling, collision) translated to the chosen syntax.

## Workflow 4: Journal and arXiv Submission

### arXiv submission checklist

When the user says they're submitting to arXiv, work through this checklist (also available in `templates/arxiv-checklist.md`):

1. **Source bundle**
   - Single `.tex` (or main + inputs flattened via `latexpand`).
   - `.bbl` file embedded; do not include `.bib` (arXiv runs BibTeX but `.bbl` is more reliable).
   - All figures present, in `figures/` or top level. Accepted: PDF, PNG, JPG, EPS. Avoid `.bmp`/`.tif`.
   - Custom `.cls` / `.sty` included if not on arXiv's standard list.
2. **Cleanup**
   - No `\todo{}`, `\TODO`, `\fixme`, `% XXX` comments visible in PDF (use `\usepackage[disable]{todonotes}` for final).
   - `\usepackage{microtype}` is fine; `\usepackage[final]{showkeys}` or similar debug packages disabled.
   - No absolute file paths in `\includegraphics`.
3. **Metadata**
   - Title, abstract, authors, affiliations.
   - **MSC2020 codes** (Mathematical Subject Classification) — required by most math journals; arXiv field accepts them.
   - Keywords (5–8 typical).
   - ACM CCS for CS papers.
4. **Compile cleanly**
   - `pdflatex` (or `xelatex`/`lualatex`) → BibTeX → `pdflatex` × 2, no errors, no unresolved `??` references.
   - File size under arXiv's limit (10MB by default; higher caps available).

### Journal class detection

Identify the journal class from `\documentclass`:

| Class | Journal family |
|-------|----------------|
| `elsarticle` | Elsevier |
| `IEEEtran` | IEEE |
| `acmart` | ACM |
| `siamart`, `siamart220329` | SIAM |
| `amsart` | AMS journals |
| `imsart` | IMS / Annals of Stats |
| `revtex4-2` | APS / AIP |
| `lipics-v2021` | Schloss Dagstuhl |
| `llncs` | Springer LNCS |

For each, check the required fields (title, authors, affiliations, abstract, keywords, MSC/CCS), and warn about page limits if specified in CFP.

### Double-blind submission

When the journal/conference is double-blind:

1. Strip `\author{...}` and `\thanks{...}` for the submission build (typically a class option like `acmart[anonymous]` or a custom flag).
2. Self-citations in third person: write "Smith [12] showed ..." not "We previously showed [12]".
3. Remove acknowledgements section.
4. Strip identifying metadata from PDF (`pdftk` or `exiftool`).
5. Anonymize repository URLs and dataset names if they reveal authorship.

### Revision and reviewer response

- Generate diff against the prior version using `latexdiff old.tex new.tex > diff.tex`. Submit `diff.pdf` alongside the clean version.
- Structure the response document as:
  ```
  Reviewer 1, Comment 1.1: <quote>
    Response: <what we changed and why>
    Location: §3.2, paragraph 2 (highlighted in diff)
  Reviewer 1, Comment 1.2: ...
  ```
- For each comment, classify: addressed in revision / addressed in response only / respectfully disagree (with reason).

## Integration with Other Skills

Do not reimplement — delegate:

| Concern | Delegate to | When to invoke |
|---------|-------------|----------------|
| Find references, format BibTeX, check for retractions | `literature-search` | User asks for citations, needs BibTeX entries, or you find an unsupported citation |
| Verify numerical claims, dates, statistics | `fact-checker` | User claims a number/result that isn't from their own derivation |
| Extract figures from prior PDFs, build a figure registry | `document-figures` | User imports figures or needs a Figure Ledger |
| Summarize related work / prior literature | `document-summary` | Drafting "Related Work" section |
| Translate the paper across languages | `faithful-translation` | Cross-language version. Remind: do NOT translate equation variables |

When delegating, hand off concrete inputs:

```
> [delegating to literature-search]
> Find peer-reviewed sources for: "Lipschitz continuity of the value function under convex constraints",
> 2018–present, math.OC or stat.ML categories. Return BibTeX with DOI and arXiv ID.
```

## Anti-patterns and Common Failures

- **Hypothesis bleed** — hypotheses scattered across surrounding paragraphs instead of inside the theorem statement. Fix: gather as a single clause beginning "Let ... Suppose ...".
- **Polysemy** — same symbol with multiple meanings (e.g., `\sigma` for σ-algebra and permutation). Fix: rename one (`\Sigma` for the algebra, `\sigma` for permutation, or vice versa).
- **Under-defined object** — quantities used without saying which space they live in. Always state "where $x \in X$".
- **Single-symbol display** — `\[ x \]` for one symbol. Use inline.
- **Label collisions** — `\label{eq:main}` reused. Use distinct names or section prefixes.
- **Self-identification in double-blind** — citing prior work in first person ("our earlier paper [3]") leaks identity. Use third person.
- **Forgotten `.bbl`** — submitting `.bib` alone to arXiv often fails BibTeX. Always embed `.bbl`.
- **`amsmath` align inside `equation`** — invalid nesting, breaks alignment. Use `align` directly.
- **Equation as image** — exporting an equation as PNG defeats accessibility, search, and reflow. Use LaTeX source.
- **`\eqref` to non-equation** — using `\eqref{thm:main}` produces `(Theorem 2.1)` with parens. Use `\ref` or `\cref` for non-equations.

## Quick Reference: Output Formats

When asked to produce a Symbol Ledger, output as a Markdown table (above format).

When asked for a dependency graph, output as a bullet list `A ← B, C` per node, plus a flat ordering: "Topological order: Def 2.3, Lem 3.4, Prop 3.5, Lem 4.1, Thm 4.2".

When asked for an arXiv prep report, output a numbered checklist with status:
- `[x]` passed
- `[ ]` action needed: `<concrete fix>`
- `[?]` cannot determine, ask user

## Templates

Available in `templates/` of this plugin:

- `article-amsthm.tex` — minimal LaTeX article scaffold with amsthm/amsmath, theorem environments, MSC field, and ready-to-edit sections.
- `arxiv-checklist.md` — the arXiv submission checklist as a standalone Markdown file the user can copy into their repo.
