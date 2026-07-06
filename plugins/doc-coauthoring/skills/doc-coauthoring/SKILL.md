---
name: doc-coauthoring
description: Guided, knowledge-grounded co-authoring workflow for substantial documents (proposals, specs, decision docs, technical articles, whitepapers). Runs three optional, composable stages — context gathering, section-by-section drafting, and reader-testing — while grounding facts/definitions in a domain knowledge base with cited sources and consistent terminology. Drafts into a working file, preserves human "[人]" edits, and hands off critical review to doc-review, restructuring to doc-refactor, fact-checking to verify-content/evidence-check, de-AI restyle to ai-tell-reducer/humanize-prose, and translation to faithful-translation. Bilingual JA/EN. Trigger when the user wants to write or co-author a doc; ドキュメント・文章の共同執筆／たたき台づくり。
---

# Doc Co-Authoring (knowledge-grounded)

A guided workflow for co-authoring a substantial document with a human. Act as an active guide,
not an autopilot: the three stages below are **optional and composable** — offer them, let the
user skip, reorder, or drop out to freeform at any point. The value over freeform writing is
(1) closing the context gap before drafting, (2) grounding facts in a knowledge base with
citations, and (3) reader-testing the draft before others read it.

This skill is the **generative co-writing** partner. It deliberately does NOT do these — hand off:
critical review → `doc-review`; structure-only refactor → `doc-refactor`; fact/citation
verification → `verify-content` / `evidence-check`; de-AI restyle → `ai-tell-reducer` /
`humanize-prose`; translation → `faithful-translation`; figure extraction/creation → `document-figures`.

## Working surface & conventions

- **Draft into a file, not chat.** Prefer a per-document workspace: `works/<doc>/draft.md`
  (the body being grown) and `works/<doc>/notes.md` (a free scratchpad for dumped context,
  outline fragments, source links). If the host repo has `make new-doc DOC=<name>`, use it;
  otherwise create the two files. Build DOCX with `make build DOC=<name>` (or pandoc) when done.
- **Knowledge base (if present).** If a `knowledge/` static-RAG base is available, pick the
  document's domain and query it for definitions/facts: `make kb-query DOMAIN=<d> Q="…"`
  (or `make kb-search …`). Record every fact's source (source + heading / URL) in the draft.
- **Evidence discipline (guardrail, always on).** Facts, definitions, regulations, and proper
  nouns must be backed by the knowledge base or a primary source. Mark anything unverified with
  `[要確認]`. Keep terminology consistent with the domain glossary
  (`knowledge/domains/<DOMAIN>/core/glossary.md` when present).
- **Human-in-the-loop.** The human may edit the draft directly and leave inline notes prefixed
  `[人]`. **Never delete or overwrite the human's `[人]` notes or edits** — read them, apply
  them, and remove a `[人]` note only after addressing it (confirm with the user if unsure).
- **Edit surgically.** Change the target section only; never reprint the whole document.

## Stage 1 — Context Gathering

Goal: close the gap between what the user knows and what you know, so later guidance is smart.

Ask for meta-context first (shorthand answers are fine):
1. Document type? (proposal / decision doc / spec / technical article / whitepaper …)
2. Primary audience and their prior knowledge?
3. Desired impact — what should the reader do or believe after reading?
4. A template or required format?
5. Domain (for the knowledge base, e.g. `dataspace` / `tddi`) and any hard constraints?

Then invite an unstructured **info dump into `notes.md`** — background, prior discussions,
why alternatives were rejected, organizational context, timeline, dependencies, stakeholder
concerns. Tell them not to organize it. Sources can be: pasted text, links, repo files, or a
knowledge-base topic to pull.

While gathering: pull relevant definitions/facts from the knowledge base and note their sources;
track what is understood vs still unclear. When the user signals they are done, ask **5–10
numbered clarifying questions** targeting gaps (they can answer in shorthand). 

Exit when questions can probe edge cases and trade-offs without needing basics explained.
Ask if there is more context, or if it is time to draft.

## Stage 2 — Refinement & Structure

Goal: build the document section by section: brainstorm → curate → draft → refine.

1. **Agree the structure.** Propose 3–5 sections appropriate to the doc type/template, or ask
   which section to start with. Start with the section that has the most unknowns (for a
   decision doc, the core proposal; for a spec, the technical approach). Leave summaries for last.
2. **Scaffold.** Write the section headers into `draft.md` with `[To be written]` placeholders,
   plus the draft-state header (AI起草 / 人執筆中 / 自己レビュー済 / 確定).
3. **For each section:**
   - **Clarifying questions** (5–10) about what to include.
   - **Brainstorm** 5–20 candidate points; surface forgotten context and un-mentioned angles.
   - **Curate**: ask which to keep/remove/combine (accept shorthand like "keep 1,4,7; drop 3").
   - **Gap check**: anything important missing?
   - **Draft** the section by replacing its placeholder. Ground every fact via the knowledge
     base and cite the source; mark unverified claims `[要確認]`; follow the glossary.
   - **Refine** through surgical edits from the user's feedback. Encourage the user to say what
     to change (this teaches their style) but also honor direct `[人]` edits.
   - After ~3 iterations with no substantial change, ask what can be cut without losing meaning.
4. **Near completion (80%+):** re-read the whole draft for flow, redundancy, contradictions,
   and generic filler ("does every sentence carry weight?"). Fix or flag.

## Stage 3 — Reader Testing (self-review)

Goal: verify the draft works for a fresh reader with no shared context.

- Predict **5–10 questions** a real reader would ask.
- **If sub-agents are available**, test each question against a fresh agent given only the draft;
  also run `doc-review` on the draft for substantive weaknesses, and spot-check key facts with
  `verify-content` / `evidence-check` + the knowledge base. Summarize what the reader got wrong
  and any ambiguity/contradiction/unstated-assumption found.
- **If sub-agents are not available**, give the user the questions to run in a fresh Claude
  conversation, plus "what is ambiguous / what prior knowledge does this assume / any
  contradictions?" and collect the results.
- Loop failures back into Stage 2 for the affected sections.

Exit when a fresh reader answers consistently and surfaces no new gaps.

## Final review & handoff

- Ask the user to do a final read — they own the document and its quality — and to verify facts,
  links, and that it achieves the intended impact.
- Offer targeted handoffs: `doc-refactor` (tighten structure), `ai-tell-reducer` /
  `humanize-prose` (reduce AI tells), `faithful-translation` (JA↔EN), `doc-review` (independent
  critique). Then build the deliverable (`make build DOC=<name>` → DOCX).
- Update the draft-state header to 確定 when agreed.

## Guidance

- Be direct and procedural; explain rationale briefly; do not "sell" the workflow — execute it.
- Always give the user agency: any stage can be skipped, reordered, or dropped for freeform.
- Do not let context gaps accumulate — ask as they arise. Quality over speed.
