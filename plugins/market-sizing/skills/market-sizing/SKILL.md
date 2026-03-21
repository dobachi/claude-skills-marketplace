---
name: market-sizing
description: Estimate market size using TAM/SAM/SOM frameworks with top-down and bottom-up approaches, generating evidence-backed reports
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Market Sizing

Estimates market size using structured frameworks, combining top-down and bottom-up approaches to produce evidence-backed market sizing reports.

## Core Framework: TAM / SAM / SOM

| Level | Definition | Question |
|-------|-----------|----------|
| **TAM** (Total Addressable Market) | Total market demand if 100% share were captured | How big is the universe? |
| **SAM** (Serviceable Addressable Market) | Portion of TAM reachable with current product/channel | How much can we realistically target? |
| **SOM** (Serviceable Obtainable Market) | Portion of SAM realistically capturable in 1-3 years | How much will we actually win? |

```
TAM ⊃ SAM ⊃ SOM

TAM: $10B  ──── Total global market
 └─ SAM: $2B  ── Our segment/geography/product fit
     └─ SOM: $200M  ── Realistic capture (1-3 years)
```

## Estimation Approaches

### Top-Down

Start from macro data and narrow down:

```
Industry market size (analyst reports, government statistics)
  × Relevant segment % (geography, vertical, company size)
  × Addressable % (product fit, channel reach)
  = SAM estimate
```

**Pros**: Quick, leverages existing research
**Cons**: Can be overly optimistic, may miss market nuances

### Bottom-Up

Build from unit economics and scale up:

```
Number of potential customers (identifiable targets)
  × Average deal size / revenue per customer
  × Expected penetration rate
  = SOM estimate
```

**Pros**: Grounded in real economics, more defensible
**Cons**: Harder to estimate total potential, may undercount

### Value-Theory (Demand-Side)

Estimate based on the value delivered:

```
Customer's current spend on the problem
  × Number of customers with this problem
  × Willingness to pay for a better solution
  = Market value estimate
```

## Workflow

### Step 1: Define the Market

Clarify with the user:

| Parameter | Description | Example |
|-----------|------------|---------|
| **Product/Service** | What is being offered? | Data governance platform |
| **Target Customer** | Who buys? | Enterprise data teams (500+ employees) |
| **Geography** | Which markets? | North America, then EU |
| **Time Horizon** | When? | Current (2024) + 5-year projection |
| **Problem** | What pain point? | Regulatory compliance for data usage |

### Step 2: Research

Gather data via web search:

| Data Type | Sources |
|-----------|---------|
| **Market reports** | Gartner, IDC, Forrester, Grand View Research, Markets and Markets |
| **Industry data** | Government statistics, trade associations, census data |
| **Company data** | SEC filings, annual reports, earnings calls |
| **Comparable transactions** | M&A deals, funding rounds in the space |
| **Customer data** | Survey data, industry benchmarks, case studies |

### Step 3: Calculate

Perform both top-down and bottom-up estimates, then triangulate:

#### Estimation Template

```markdown
## Top-Down Estimate
- Global [industry] market: $X (Source: [report])
- [Segment] share: Y% → $Z
- [Geography] share: W% → $V
- **TAM**: $V
- Addressable by our product: A% → **SAM**: $U

## Bottom-Up Estimate
- Number of target companies: N (Source: [database])
- Average annual contract value: $ACV
- Expected penetration (3 years): P%
- **SOM**: N × $ACV × P% = $S

## Triangulation
- Top-down SAM: $U
- Bottom-up SOM: $S
- Consistency check: SOM/SAM ratio = X% (typical range: 1-10%)
```

### Step 4: Sensitivity Analysis

Test key assumptions:

| Variable | Low Case | Base Case | High Case |
|----------|----------|-----------|-----------|
| Market growth rate | X% | Y% | Z% |
| Penetration rate | A% | B% | C% |
| ACV | $D | $E | $F |
| **Resulting SOM** | $G | $H | $I |

### Step 5: Report Generation

#### Standard Deliverable

```markdown
# Market Sizing Report: [Topic]

## Executive Summary
- TAM: $X | SAM: $Y | SOM: $Z
- Key insight in 2-3 sentences

## Market Definition
- Product/service scope
- Customer definition
- Geographic scope

## TAM Analysis
- Top-down calculation with sources
- Growth projections (CAGR)

## SAM Analysis
- Segmentation criteria and rationale
- Addressable portion calculation

## SOM Analysis
- Bottom-up calculation
- Competitive share assumptions
- Go-to-market reach assumptions

## Sensitivity Analysis
- Key variable ranges
- Scenario table

## Key Assumptions and Risks
- Listed with confidence level (High/Medium/Low)
- What would invalidate each assumption

## Sources
- All sources with URLs and dates
```

## Quality Standards

1. **Cite every number**: No unsourced statistics. If estimated, state the method
2. **Date all data**: Market data decays quickly; note the year of each figure
3. **Show your math**: Every calculation should be reproducible
4. **Cross-validate**: Compare top-down and bottom-up; explain divergences
5. **State assumptions explicitly**: Each assumption should be separately identifiable
6. **Use ranges, not points**: Prefer "$200M-$400M" over "$300M" when uncertainty is high
7. **Flag stale data**: Warn when using data older than 2 years

## Common Pitfalls

- **TAM inflation**: Counting the entire industry when only a segment is relevant
- **Double counting**: Including overlapping segments
- **Ignoring substitutes**: Not accounting for alternative solutions
- **Static analysis**: Failing to project market growth/contraction
- **Survivorship bias**: Only looking at successful companies in the space
- **Currency/geography confusion**: Mixing global and regional figures
