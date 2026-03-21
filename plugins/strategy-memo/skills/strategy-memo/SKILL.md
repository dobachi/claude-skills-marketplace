---
name: strategy-memo
description: Structure business ideas into a 4-layer framework (Market/Value Proposition/Technology/Execution), check for logical gaps, and generate polished strategy memos
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Strategy Memo

Transforms rough business ideas and insights into structured strategy memos using a 4-layer framework, with systematic gap analysis and logical consistency checking.

## 4-Layer Framework

### Layer 1: Market (Why Now?)

| Element | Description | Key Questions |
|---------|------------|---------------|
| **Market Dynamics** | Current state and trajectory | What is changing in this market? What are the macro/micro trends? |
| **Customer Pain** | Problems worth solving | Who suffers? How much does it cost them? How do they cope today? |
| **Timing** | Why this opportunity exists now | What has changed (technology, regulation, behavior) to create this window? |
| **Competitive Landscape** | Who else is here | Who are the incumbents? New entrants? What are their blind spots? |

### Layer 2: Value Proposition (What?)

| Element | Description | Key Questions |
|---------|------------|---------------|
| **Core Offering** | What we build/deliver | What is the product/service? What does it do concretely? |
| **Differentiation** | Why us over alternatives | What is our unique angle? What moat can we build? |
| **Customer Value** | Measurable impact | What ROI/outcome can customers expect? How do we prove it? |
| **Positioning** | Market perception | How do we want to be perceived? What category do we create or own? |

### Layer 3: Technology (How?)

| Element | Description | Key Questions |
|---------|------------|---------------|
| **Architecture** | Technical approach | What is the high-level system design? Buy vs. build? |
| **Key Technology Bets** | Critical technical choices | What technologies are we betting on? What are the risks? |
| **Data Strategy** | Data as an asset | What data do we need? How do we acquire/generate/protect it? |
| **Technical Moat** | Defensibility through technology | What gets harder to replicate over time? Network effects? Data flywheel? |

### Layer 4: Execution (Who/When/How Much?)

| Element | Description | Key Questions |
|---------|------------|---------------|
| **Team** | Who executes | What capabilities do we need? What do we have vs. need to hire? |
| **Milestones** | Key checkpoints | What are the 3/6/12-month milestones? What proves/disproves the thesis? |
| **Resources** | Investment required | How much funding? What infrastructure? What partnerships? |
| **Risks & Mitigations** | What could go wrong | Top 3-5 risks and how we address each |
| **Go-to-Market** | How we launch and grow | First customers? Sales motion? Growth loops? |

## Workflow

### Step 1: Input Analysis

Accept the user's raw input (idea memo, conversation notes, brainstorm output) and:
1. Extract key claims and assertions
2. Identify which of the 4 layers are covered
3. Note which layers have gaps

### Step 2: Gap Analysis

Generate a gap analysis table:

```markdown
## Gap Analysis

| Layer | Element | Status | Notes |
|-------|---------|--------|-------|
| Market | Market Dynamics | Covered | Strong macro analysis |
| Market | Customer Pain | Partial | Pain identified but not quantified |
| Market | Timing | Gap | No "why now" argument |
| Market | Competitive Landscape | Covered | 3 competitors identified |
| Value Prop | Core Offering | Covered | Clear product description |
| Value Prop | Differentiation | Partial | Claimed but not evidenced |
| ... | ... | ... | ... |
```

Status levels:
- **Covered**: Adequately addressed with evidence/reasoning
- **Partial**: Mentioned but needs more depth or evidence
- **Gap**: Not addressed at all
- **Assumption**: Stated as fact but actually an untested assumption

### Step 3: Consistency Check

Verify logical coherence across layers:

| Check | Description |
|-------|------------|
| **Market-VP alignment** | Does the value proposition address the identified market pain? |
| **VP-Tech feasibility** | Can the technology actually deliver the promised value? |
| **Tech-Execution realism** | Does the team/resource plan match the technical ambition? |
| **Market-Execution timing** | Do milestones align with market window? |
| **Overall coherence** | Does the story hold together end-to-end? |

### Step 4: Memo Generation

#### Standard Memo Template

```markdown
# Strategy Memo: [Title]

**Date**: [Date]
**Author**: [Author]
**Status**: Draft / Review / Final
**Confidentiality**: [Level]

---

## Executive Summary
3-5 sentences capturing the core thesis, opportunity size, and recommended action.

## 1. Market Opportunity
### 1.1 Market Dynamics
### 1.2 Customer Pain Point
### 1.3 Why Now
### 1.4 Competitive Landscape

## 2. Value Proposition
### 2.1 Core Offering
### 2.2 Differentiation
### 2.3 Customer Value / ROI
### 2.4 Positioning

## 3. Technology & Product
### 3.1 Architecture Overview
### 3.2 Key Technology Bets
### 3.3 Data Strategy
### 3.4 Technical Moat

## 4. Execution Plan
### 4.1 Team & Capabilities
### 4.2 Milestones (3 / 6 / 12 months)
### 4.3 Resource Requirements
### 4.4 Risks & Mitigations
### 4.5 Go-to-Market Strategy

## 5. Open Questions
Numbered list of unresolved issues that need further investigation.

## 6. Next Steps
Concrete actions with owners and deadlines.

## Appendix
- Gap analysis table
- Assumptions log
- Sources
```

## Quality Criteria

### Memo Scoring Rubric

| Dimension | Strong | Adequate | Weak |
|-----------|--------|----------|------|
| **Clarity** | Thesis stated in one sentence | Thesis identifiable but verbose | Thesis unclear |
| **Evidence** | Data-backed claims with sources | Some data, some assertions | Mostly opinion |
| **Completeness** | All 4 layers substantively covered | Minor gaps acknowledged | Major layers missing |
| **Coherence** | Logical flow across all layers | Some disconnects noted | Contradictions present |
| **Actionability** | Clear next steps with owners/dates | General direction provided | No clear path forward |

## Iteration Modes

| Mode | Description | When to Use |
|------|------------|-------------|
| **Expand** | Deepen a specific layer or element | "Tell me more about the competitive landscape" |
| **Challenge** | Stress-test assumptions and claims | "What could go wrong with this thesis?" |
| **Sharpen** | Tighten the argument, remove fluff | "Make this more concise and compelling" |
| **Pivot** | Explore alternative framings | "What if we targeted a different segment?" |

## Anti-Patterns to Avoid

- **Solution-first thinking**: Starting with technology instead of market need
- **Hand-waving at execution**: Vague milestones like "scale the platform"
- **Competitor dismissal**: "No one else does this" (almost never true)
- **TAM abuse**: Citing a huge market without narrowing to the addressable portion
- **Missing the "why now"**: An idea without timing rationale is just an observation
- **Assumption blindness**: Treating hypotheses as established facts
