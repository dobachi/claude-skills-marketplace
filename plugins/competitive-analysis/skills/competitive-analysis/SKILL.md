---
name: competitive-analysis
description: Research competitors via web search, analyze features/pricing/customers/differentiation, and generate structured comparison matrices
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Competitive Analysis

Conducts structured competitive analysis by researching competitor products, services, and strategies, then generating actionable comparison reports.

## Workflow

### Phase 1: Scope Definition

Clarify the analysis scope with the user:

1. **Target company/product**: What is being analyzed?
2. **Competitors**: Known competitors to include (or discover via research)
3. **Analysis dimensions**: Which comparison axes matter most?
4. **Purpose**: Investment decision, product strategy, market entry, etc.

### Phase 2: Research

Use web search to gather information on each competitor across the following dimensions:

| Dimension | Key Data Points |
|-----------|----------------|
| **Product/Service** | Core features, platform, technology stack, integrations |
| **Pricing** | Pricing model (subscription/usage/license), tiers, free tier, enterprise pricing |
| **Target Customers** | Industry verticals, company size, use cases, notable customers |
| **Market Position** | Market share, growth rate, funding/revenue, geographic presence |
| **Differentiation** | Unique selling points, moats, patents, ecosystem lock-in |
| **Weaknesses** | Known limitations, customer complaints, missing features |
| **Go-to-Market** | Sales model (self-serve/enterprise), partnerships, channel strategy |

### Phase 3: Analysis Frameworks

Apply one or more frameworks depending on the analysis purpose:

#### Feature Comparison Matrix

```markdown
| Feature          | Company A | Company B | Company C |
|------------------|-----------|-----------|-----------|
| Feature 1        | Yes       | Partial   | No        |
| Feature 2        | No        | Yes       | Yes       |
| Pricing (entry)  | $X/mo     | $Y/mo     | Free      |
| Target segment   | Enterprise| SMB       | Developer |
```

#### Strategic Group Mapping

Plot competitors on 2 axes relevant to the market (e.g., price vs. feature breadth, ease-of-use vs. customizability).

#### SWOT per Competitor

For each competitor, identify:
- **Strengths**: What they do best
- **Weaknesses**: Where they fall short
- **Opportunities**: Market gaps they could exploit
- **Threats**: Risks to their position

#### Porter's Five Forces (Market-Level)

When analyzing the competitive landscape as a whole, assess:
- Rivalry intensity among existing players
- Threat of new entrants
- Substitute products/services
- Supplier bargaining power
- Buyer bargaining power

### Phase 4: Deliverable Generation

#### Standard Deliverable Structure

```markdown
# Competitive Analysis: [Topic]

## Executive Summary
- Key findings (3-5 bullet points)
- Recommended positioning

## Market Overview
- Market definition and scope
- Key trends and dynamics

## Competitor Profiles
### [Competitor 1]
- Overview, product, pricing, strengths, weaknesses

### [Competitor 2]
...

## Comparison Matrix
(Feature/pricing/capability comparison table)

## Strategic Implications
- White spaces and opportunities
- Threats and risks
- Recommended actions

## Sources
- List of sources with URLs and access dates
```

## Research Guidelines

Competitive analysis is unusually hallucination-prone: every fact is contested, every primary source is an interested party, and the aggregators that rank well are restating each other. Ground it or don't ship it.

1. **Evidence Ledger (required)**: Every cell in the comparison matrix that asserts a fact — a price, a feature, a customer, a limit — carries a ledger row with a **verbatim quote** from the source that establishes it. A matrix cell with no ledger row is an inference, and gets marked as one.
2. **Open what you cite**: A search-result snippet is not a source. Fetch the page. Snippets are generated text and routinely paraphrase pricing pages wrongly.
3. **Quote the deciding words**: The quote must contain the fact, not merely discuss the topic. Link validity and topical relevance are not verification — cited sources that resolve, are on-topic, and don't support the claim are the dominant failure mode here.
4. **Source quality**: Prioritize official websites, analyst reports, press releases, and credible tech publications — but rate them:
   - **Vendor's own pricing/docs**: authoritative about themselves, unreliable about rivals.
   - **A vendor's benchmark or comparison of a competitor**: never a fact. Register it as *a claim the vendor makes*, attributed, and go verify it against the competitor's own source.
   - **Aggregators, listicles, "X vs Y" SEO pages, AI-written roundups**: never terminal. Use them to find the primary, then cite the primary.
5. **Trace up**: If a source restates another, cite the original. Restated pricing drifts — tiers get stale, regional prices get flattened, annual gets reported as monthly.
6. **Corroboration means independent origin**: Three articles restating one press release is one source with three URLs. Say "one source" when it is one source.
7. **Recency**: Record an access date per data point; flag anything older than 12 months. Pricing and feature claims decay fastest.
8. **Objectivity**: Present facts and data, not opinions; clearly label any inferences. Keep strategic implications visibly separate from the evidence they rest on — that separation is where the reader's judgement enters.
9. **Disagreement**: When sources conflict on a price or capability, report both with attribution and mark it unresolved. Do not average, split the difference, or silently prefer the newer one. Most conflicts are definitional (list vs. street price, per-seat vs. per-user, a feature gated behind a tier) and dissolve once stated.
10. **Gaps**: Explicitly note when information is unavailable or unverifiable. Enterprise pricing is usually "not published" — say that, never estimate it into the matrix as though it were found.

```markdown
| ID   | Claim                          | Competitor | Source (URL)      | Tier            | Accessed   | Verbatim quote           |
|------|--------------------------------|------------|-------------------|-----------------|------------|--------------------------|
| E-01 | Starts at $49/seat/month       | Vendor A   | https://…/pricing | vendor-primary  | 2026-07-17 | "$49 per seat per month" |
| E-02 | No SSO below Enterprise tier   | Vendor A   | https://…/pricing | vendor-primary  | 2026-07-17 | "SSO available on Enterprise" |
| E-03 | "2× faster than Vendor A"      | Vendor B   | https://…/compare | vendor-on-rival | 2026-07-17 | "2× faster than Vendor A" — B's claim about A; unverified |
```

For a high-stakes analysis — an investment decision, a market-entry call, anything that will be quoted back at you — run the research through `grounded-research` first (parallel retrieval subagents, source ledger, blind per-claim verification) and build the matrix from its ledger. To audit a competitive report someone already wrote, use `fact-checker`.

## Output Formats

| Format | When to Use |
|--------|------------|
| **Comparison Matrix** | Quick feature/pricing comparison for decision-making |
| **Full Report** | Comprehensive analysis for strategic planning |
| **Executive Brief** | 1-page summary for leadership review |
| **Battle Card** | Sales-oriented competitive positioning per competitor |

## Anti-Patterns to Avoid

- Relying on outdated information without noting the date
- Comparing on dimensions irrelevant to the user's decision
- Ignoring indirect competitors or substitute products
- Presenting speculation as fact
- Omitting sources
