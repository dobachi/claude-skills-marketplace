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

1. **Source quality**: Prioritize official websites, analyst reports, press releases, and credible tech publications
2. **Recency**: Note the date of each data point; flag information older than 12 months
3. **Verification**: Cross-reference pricing and feature claims across multiple sources
4. **Objectivity**: Present facts and data, not opinions; clearly label any inferences
5. **Gaps**: Explicitly note when information is unavailable or unverifiable

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
