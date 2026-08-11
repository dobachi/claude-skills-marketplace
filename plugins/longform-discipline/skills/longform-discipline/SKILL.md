---
name: longform-discipline
description: Guardrails and a minimal loop for co-writing a LONG document with an AI — tens of thousands of characters to book length, including academic long-form. Long documents fail by drifting, not by being written badly, so this targets the three measured decay axes (long input, long output, long session) — never single-pass the whole document, keep a spine file (outline, glossary, style contract) outside the context window, write sections sequentially with the prior section's tail loaded, repair the seams decomposition creates, keep the outline revisable, and gate on a deterministic scan plus a human review list, not AI self-scoring. Ships drift_scan.py (文体 mixing, sentence length, terminology drift, cross-section duplication). Bilingual JA/EN. Use when writing or continuing a long doc — 長文, 長編, 章立て, 数万字, 書籍, whitepaper, thesis — or on 用語がぶれる / 章がちぐはぐ / 後半が薄い / 同じことを何度も書いている / 'it lost the thread'. Hands drafting to doc-coauthoring, restructuring to doc-refactor, critique to doc-review, AI tells to ai-tell-reducer.
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Long-form Discipline

Rules for writing a document too long to hold in one context, one pass, or one session.

**The premise, and it is measured, not folklore:** a long document does not fail by being written
badly. It fails by *drifting* — terminology moves, the argument reappears in three places in three
shapes, chapter 9 contradicts chapter 2, and the last third is thinner than the first. Every
mechanism behind that drift is documented in `references/failure-modes.md`, with a verbatim span
and a source for each. Read that file when someone asks *why* a rule exists, or wants to break one.

This skill is a **cross-cutting layer**, not a competing workflow. It composes with whatever else
is running: `doc-coauthoring` (the drafting conversation), `doc-refactor` (restructuring),
`doc-review` (critique), `essence-distiller` (cuts), `ai-tell-reducer` / `humanize-prose` (AI tells),
`verify-content` / `fact-checker` (facts), `faithful-translation` (JA↔EN). It owns none of those
jobs. It owns **coherence across length**.

## When it applies

Turn it on at roughly **8,000 characters / 3,000 words**, or the moment any of these is true:

- the document has chapters or numbered sections written at different times
- drafting will span more than one session, or more than one compaction
- the whole document no longer fits comfortably in the context alongside the work
- a glossary, a house style, or a citation set has to stay fixed across the whole thing

Below that, this skill is overhead — write the thing.

## The three decay axes

Three independent failure surfaces. Confusing them leads to fixing the wrong one.

| Axis | What decays | The measured signature | The rule it forces |
|---|---|---|---|
| **Long input** | The model's use of what you gave it | Middle-of-context material is used worst; effective context is far shorter than advertised; accuracy drops with length *even when retrieval is perfect* | Never paste the whole document and say "fix it". Feed the spine + the relevant section. |
| **Long output** | The text being generated | Single-pass generation stalls near ~2k words; quality, instruction-following and information density fall as output grows; repetition sets in | Never ask for the whole document in one pass. Bounded sections. |
| **Long session** | The conversation carrying the work | Large drop from single-turn to multi-turn, driven by unreliability rather than lost skill; a wrong early turn is not recovered from; early errors raise the odds of later ones | Re-enter fresh per section from the spine. Do not let a long thread accumulate. |

## The seven rules

Non-negotiable unless the user overrides them knowingly.

1. **Never single-pass a long document.** Not the first draft, not the "just regenerate it cleanly"
   rewrite. Output quality falls off well before the document is done, and the model will silently
   stop short of the requested length.
2. **Keep a spine file outside the context window.** One file beside the draft holding purpose,
   audience, outline with per-section status, glossary, style contract, claims, and open questions.
   It is the thing that is re-read at the start of every session and after every compaction — the
   draft is the output, the spine is the state. Schema: `references/spine-file.md`.
3. **Write sections sequentially, with the previous section's tail in context.** Not in parallel.
   Parallel section generation measurably costs coherence even when it improves throughput.
4. **Repair the seams, always.** Decomposition is not free: it buys length, breadth and depth and
   it *costs* local coherence and produces cross-section restatement. A seam pass is part of the
   method, not a nicety. Skipping it is why decomposed drafts read as stitched.
5. **The outline is revisable, not frozen.** A plan improves a long draft; a plan held rigid past
   the point it stopped fitting is itself a documented cause of long-form collapse. When a section
   fights its outline entry, change the entry and say so in the spine — do not force the prose.
6. **Gate on a deterministic scan plus a human read. Never on AI self-scoring.** Model judges carry
   position, order and self-preference bias, and automatic self-contradiction detection is
   unreliable exactly on the nuanced cases that matter. `drift_scan.py` is the mechanical gate;
   the human is the judgment gate.
7. **Give the human something specific to check.** People given AI output review it worse *and
   trust it more*. "Please review" gets nodded through. Hand over a numbered list: these 4 claims
   are unverified, these 2 sections contradict, this term drifted in §7.

## The loop

Per section. Everything below happens with the spine loaded and the rest of the draft *not* loaded.

```
0. SPINE      Write/refresh the spine file. Purpose, audience, outline, glossary, style contract.
              No drafting until the outline exists and the glossary has the load-bearing terms.
1. SITUATE    Load: spine + the outline entry for this section + the previous section's last
              ~300 words + any section this one must not repeat. Nothing else.
2. DRAFT      Write this section only, to its budget. Mark unverified facts [要確認] / [unverified].
3. RECONCILE  Update the spine in the same turn: section status, new terms, new claims, anything
              the outline now gets wrong. A spine updated "later" is a spine that is already stale.
4. RE-ENTER   Start the next section from a clean context. Do not continue the thread.
```

Then, once the sections exist:

```
5. SEAM       Read consecutive section pairs. Fix transitions, kill cross-section restatement,
              resolve terminology that moved. This is rule 4 and it is not optional.
6. SCAN       python3 scripts/drift_scan.py <draft.md> --spine <draft>.spine.md
              Fix or consciously accept every finding. It reports; it never edits.
7. HANDOFF    doc-review (argument), verify-content (facts), essence-distiller (cuts),
              ai-tell-reducer (AI tells), doc-refactor (structure).
8. HUMAN      Numbered, specific review list. Not "please review".
```

## The drift scan

```bash
python3 scripts/drift_scan.py DRAFT.md                      # human-readable
python3 scripts/drift_scan.py DRAFT.md --spine DRAFT.spine.md
python3 scripts/drift_scan.py DRAFT.md --json               # machine-readable
```

Stdlib only, Python 3.8+. Exit `0` clean, `1` findings, `2` usage error — so it can be a loop's
stop condition (see `loop-goal`). What it detects, and the failure each maps to:

| Check | Catches |
|---|---|
| `style-mixing` | です・ます and だ・である mixed within or across sections |
| `long-sentence` | Japanese sentences past 60 / 100 characters; English past 40 / 60 words |
| `notation-drift` | The same term spelled two ways (サーバ/サーバー, 行う/行なう, e-mail/email) |
| `glossary-violation` | A banned variant of a spine glossary term, or a key term never defined |
| `cross-section-dup` | Near-identical sentences in *different* sections — the restatement signature |
| `section-imbalance` | Sections far below the document's median length — the thinning-tail signature |
| `redundant-expression` | 重言 and double negatives |
| `open-marker` | `[要確認]` / `TODO` / `TBD` / `[unverified]` left in the draft |
| `repeated-opener` | The same sentence opener reused across the document |

It **points, it never edits**, and it cannot see meaning: a flagged repetition may be a deliberate
callback, and a short section may be short on purpose. Judge every hit.

## Anti-patterns

| Anti-pattern | Why it fails | Instead |
|---|---|---|
| "Here's the whole 40k-character draft, make it consistent" | Buries the work mid-context, where it is used worst, and asks for a long output at the same time | Spine + one section at a time |
| One long chat for the whole book | Multi-turn unreliability compounds; an early wrong assumption is never recovered from | Fresh context per section, state in the spine |
| Freezing the outline at chapter 1 | Rigid plans are a documented cause of long-form collapse | Revise the outline in the spine, deliberately |
| Writing all sections in parallel to go faster | Measurably worse coherence | Sequential, prior tail carried |
| Concatenate sections and ship | Decomposition leaves seams and restatement by construction | Mandatory seam pass |
| "Score this draft 1-10 and fix anything below 8" | Judge bias plus self-preference; the model grades its own work | `drift_scan.py` + a human read |
| Asking the model whether the document contradicts itself | Automatic contradiction detection is unreliable on exactly the nuanced cases | Scan mechanically, then read the flagged pairs yourself |
| Keeping a spine that contradicts itself | Contradictory persistent instructions get resolved arbitrarily | Prune the spine when the outline changes |
| Repeating the glossary in the prompt instead of the spine | It falls out of context on compaction and drifts | One file on disk, re-read each session |
| Letting the draft grow without the spine | The state lives only in a context window that is about to be summarized away | Rule 2 |

## Japanese long-form

Japanese adds mechanically checkable failures that English does not have — 文体 mixing, 表記ゆれ,
一文の長さ, 係り受け distance, 重言, 二重否定. The rules and their primary sources (文化審議会建議
「公用文作成の考え方」, JTF日本語標準スタイルガイド) are in `references/japanese.md`. Fix the style
contract in the spine **before** drafting: 文体, 表記, 数字, 記号, 敬語. Deciding it at the end means
rewriting everything.

## References

- `references/failure-modes.md` — every rule above, with the measured finding, a verbatim span, and the source
- `references/spine-file.md` — spine file schema and a filled example
- `references/japanese.md` — Japanese long-form rules and their primary sources
