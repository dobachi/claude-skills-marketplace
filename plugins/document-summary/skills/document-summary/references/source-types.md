# Source Types: Extraction Priorities and Conventions

Different document genres have different signal patterns. Use this reference to decide what to capture in the ledger and how to structure the summary for each.

## Academic Papers (Empirical)

### Where the signal lives

| Section | Extract |
|---|---|
| **Abstract** | Research question, headline finding, hedge-bearing summary statement |
| **Introduction** | Gap in prior work, research question, hypothesis, scope |
| **Methods** | Design, sample, measures, statistical approach, ethical considerations, methodological limitations |
| **Results** | Primary finding with effect size and confidence interval; secondary findings; subgroup/sensitivity analyses |
| **Discussion** | Authors' interpretation, limitations they acknowledge, generalizability, implications, future work |
| **Conclusion** | Hedge-preserving headline conclusion |

### Priorities

1. Research question (it anchors everything else)
2. Primary finding with effect size + CI + hedges
3. Methodology (sample size, design, key measures)
4. Limitations the authors explicitly acknowledge
5. Conclusions, with hedges preserved

### Watch for

- **Effect sizes without CIs** in your summary — always preserve confidence intervals
- **Significance reported as "significant"** when source says "p < 0.05" — preserve the precise statistic
- **Generalization beyond sample** — preserve scope conditions ("among adults aged 18–65 in the US")
- **Authors' hedges in Discussion** — these often signal known weaknesses; preserve them
- **Limitations buried in Discussion** — extract aggressively; AI summaries often drop these

### Negative space common in this genre

- Replication status — was this study replicated?
- Effect size in absolute terms (not just relative)
- Comparison with prior literature's effect sizes
- Subgroup heterogeneity not analyzed

## Academic Papers (Theoretical / Review)

### Where the signal lives

| Element | Extract |
|---|---|
| **Thesis statement** | The central argument |
| **Contributions** | Novel claims the paper makes |
| **Positioning** | How the paper relates to prior literature |
| **Argument structure** | The chain of reasoning, section by section |
| **Counterarguments** | Objections engaged or anticipated |
| **Implications** | What the thesis claims to imply |

### Priorities

1. Thesis (often hedged, often complex)
2. Contributions (the paper's claim to novelty)
3. Argument structure
4. Positioning vis-à-vis prior work
5. Counterarguments engaged
6. Limitations / scope conditions

### Watch for

- **Thesis simplification** — theoretical papers often have nuanced theses; resist flattening
- **Lost engagement with prior work** — positioning matters in this genre
- **Counterarguments dropped** — these often distinguish a sophisticated paper from a polemic

## Business Reports / Whitepapers

### Where the signal lives

| Section | Extract |
|---|---|
| **Executive summary** | Headline claims, recommendations |
| **Key findings** | Numbered or bulleted main claims |
| **Methodology / approach** | How conclusions were reached |
| **Recommendations** | Action items, often prioritized |
| **Appendix** | Detailed data, methodology, footnotes |

### Priorities

1. Recommendations and the question they answer
2. Key findings with quantitative precision
3. Methodology summary (one-line description)
4. Forecast hedges and assumptions
5. Limitations / scope of the analysis

### Watch for

- **Forecast confidence drift** — "could reach" → "will reach"
- **Currency or unit shifts** — preserve original currency
- **Defined-term consistency** — KPIs and frameworks usually defined; apply consistently
- **Branded methodology names** — keep original (e.g., "Five Forces", "BCG Matrix")

### Negative space common in this genre

- Sample size of underlying surveys
- Time horizon of forecasts
- Sensitivity analyses

## News Articles

### Where the signal lives

| Element | Extract |
|---|---|
| **Lede (1st paragraph)** | Who/what/when/where/why/how |
| **Nut graf** | The "so-what" — why this story matters |
| **Direct quotes** | Speakers and their stances |
| **Attributions** | "according to", "said", "reported by" |
| **Background paragraphs** | Context for the news event |

### Priorities

1. The 5W1H from the lede
2. The nut graf if present
3. Direct quotes from primary actors
4. Attributions (who said what)
5. Background context where it changes the meaning

### Watch for

- **Editorial color in your summary** — preserve the article's neutral register
- **Attribution drift** — "said" vs "claimed" vs "alleged" carry different weight
- **Loaded vocabulary** — translate / paraphrase preserving the original word choices

### Negative space common in this genre

- The other side's response
- Source independence (was the news outlet given exclusive access?)
- Verification status of claims

## White Papers / Industry Reports

### Where the signal lives

| Section | Extract |
|---|---|
| **Problem statement** | The market problem or technological gap |
| **Approach** | The proposed solution or framework |
| **Evidence / case studies** | Supporting data and examples |
| **Economic impact / ROI** | Quantified outcomes |
| **Conclusions and call to action** | Recommended next steps |

### Priorities

1. Problem framing (often where the white paper's POV is most visible)
2. The proposed approach
3. Evidence quality and source
4. Economic claims with assumptions
5. Author/sponsor context (whitepapers are often vendor-authored — note this)

### Watch for

- **Sponsor bias** — white papers often advocate for the sponsor's product/category; preserve this stance honestly
- **Cherry-picked case studies** — note when only success stories are included
- **Vague terms** ("modernization", "digital transformation") — pin down the specific meaning in the source

## Books (Non-fiction)

### Where the signal lives

| Element | Extract |
|---|---|
| **Preface / introduction** | Author's purpose, intended audience, scope |
| **Table of contents** | Argument structure |
| **Chapter introductions and conclusions** | Chapter theses |
| **Recurring imagery / case studies** | The book's argumentative anchors |
| **Conclusion** | Synthesized argument |

### Priorities

1. Author's central argument (the book's thesis)
2. Chapter-by-chapter sub-arguments
3. Key case studies or recurring examples
4. Engagement with prior literature
5. Limitations or scope acknowledged by the author

### Watch for

- **Single-chapter summaries** that miss the book's overall arc
- **Lost narrative voice** — books have authorial voice that signals stance
- **Recurring imagery dropped** — often the book's mnemonic anchors

## Regulatory / Policy Documents

### Where the signal lives

| Section | Extract |
|---|---|
| **Scope** | What the regulation covers, who it applies to |
| **Definitions** | Defined terms (often capitalized) |
| **Obligations** | Required actions, with modal precision (shall / must / may) |
| **Exceptions / safe harbors** | Carve-outs |
| **Effective dates** | When provisions take effect |
| **Enforcement** | Penalties, oversight |

### Priorities

1. Scope (which entities are covered)
2. Top obligations with their modal verbs preserved
3. Major exceptions
4. Effective dates and transition periods
5. Enforcement mechanisms and penalties
6. Cross-references to other regulations

### Watch for

- **Modal weakening** — "shall" must not become "should"
- **Defined-term drift** — capitalized terms have specific scope
- **Cross-reference loss** — regulations interlock; missed cross-refs change meaning

### Negative space common in this genre

- What's explicitly excluded from scope
- Whether the regulation supersedes prior regulations
- Foreign jurisdictional impact

## Technical Documentation

### Where the signal lives

| Element | Extract |
|---|---|
| **Purpose / overview** | What the documented system does |
| **Prerequisites** | Required knowledge / setup |
| **Procedure / API surface** | What the user can do |
| **Parameters / options** | Configuration |
| **Examples** | Canonical use cases |
| **Edge cases / limitations** | Known issues |

### Priorities

1. Purpose (often missing in poorly-written docs; if missing, note as negative space)
2. Prerequisites
3. Core procedure or API surface (the most useful 80%)
4. Parameter semantics
5. Known limitations
6. Version applicability

### Watch for

- **Code identifiers translated** — never translate code, commands, paths, env vars
- **Version-specific notes lost** — preserve version numbers
- **Examples missing** — examples are often the highest-signal element of technical docs

## Systematic Reviews / Meta-analyses

### Where the signal lives

| Section | Extract |
|---|---|
| **PICO** | Population, Intervention, Comparison, Outcome |
| **Search strategy** | Databases, dates, language inclusion |
| **Included studies** | Number, quality assessment |
| **Pooled estimate** | Effect size with 95% CI |
| **Heterogeneity / subgroups** | Sources of variation |
| **Certainty assessment** | GRADE rating |
| **Reviewers' conclusions** | Hedge-preserving summary |

### Priorities

1. PICO (frames everything)
2. Pooled effect with CI
3. Certainty rating (GRADE: high / moderate / low / very low)
4. Heterogeneity findings
5. Reviewers' acknowledged limitations
6. Implications for practice / policy

### Watch for

- **Effect size dropped or rounded** — preserve precision
- **Certainty inflation** — moderate certainty must not become "the evidence shows"
- **Heterogeneity ignored** — even significant pooled effects may have important subgroup variation

## Quick-Reference Matrix

| Genre | Signal-rich sections | Priority claims | Negative space prompts |
|---|---|---|---|
| Empirical academic | Methods, Results, Discussion | Effect size + CI + hedges + limitations | Replication, subgroup analyses |
| Theoretical academic | Thesis, contributions, positioning | Thesis nuance, counterarguments | Engagement gaps, scope conditions |
| Business report | Exec summary, recommendations | Recommendations + assumptions | Sample size, time horizon |
| News | Lede, nut graf, attributions | 5W1H, direct quotes | Other side, verification |
| Whitepaper | Problem, approach, evidence | Approach + sponsor stance | Bias, case study selection |
| Book | TOC, chapter conclusions | Thesis + chapter arc | Engagement gaps |
| Regulatory | Scope, definitions, obligations | Modals, defined terms, dates | Excluded scope, cross-refs |
| Technical doc | Purpose, API, examples | Use cases + prerequisites | Edge cases, versions |
| Systematic review | PICO, pooled estimate, GRADE | Effect + CI + certainty | Heterogeneity, applicability |
