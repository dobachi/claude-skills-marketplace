---
name: business-model-canvas
description: Design and document business models using Business Model Canvas and Lean Canvas frameworks with structured, actionable outputs
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Business Model Canvas Designer

Guides users through structured business model design using established Canvas frameworks, generating comprehensive and actionable business model documents.

## Supported Frameworks

### Business Model Canvas (Osterwalder)

The 9 building blocks of a business model:

| Block | Key Questions | Examples |
|-------|--------------|---------|
| **Customer Segments** | Who are the target customers? Mass/niche/segmented/multi-sided? | B2B enterprise, prosumers, developers |
| **Value Propositions** | What problem do we solve? What value do we deliver? | Cost reduction, risk reduction, convenience, customization |
| **Channels** | How do we reach customers? Awareness > Evaluation > Purchase > Delivery > After-sales | Direct sales, web, partner network, app store |
| **Customer Relationships** | What type of relationship? Self-service/personal/automated/community? | Dedicated support, co-creation, SaaS self-serve |
| **Revenue Streams** | How does the business earn? Pricing mechanism? | Subscription, usage-based, licensing, freemium, marketplace commission |
| **Key Resources** | What assets are essential? Physical/IP/human/financial? | Platform, data, engineering team, patents |
| **Key Activities** | What must we do well? Production/problem-solving/platform? | Product development, data pipeline, customer success |
| **Key Partnerships** | Who are our key partners and suppliers? | Cloud providers, data vendors, channel partners, OSS communities |
| **Cost Structure** | What are the major costs? Cost-driven or value-driven? | Infrastructure, R&D, sales, support |

### Lean Canvas (Ash Maurya)

Startup-focused adaptation emphasizing problem-solution fit:

| Block | Key Questions |
|-------|--------------|
| **Problem** | Top 3 problems for target customers. Existing alternatives? |
| **Customer Segments** | Target customers and early adopters |
| **Unique Value Proposition** | Single clear message that states why you are different and worth attention |
| **Solution** | Top 3 features that address the problems |
| **Channels** | Path to customers (inbound/outbound/viral) |
| **Revenue Streams** | Revenue model, pricing, LTV, gross margin |
| **Cost Structure** | Customer acquisition costs, hosting, people, fixed/variable |
| **Key Metrics** | The one metric that matters at this stage |
| **Unfair Advantage** | Something that cannot be easily copied or bought |

## Workflow

### Step 1: Context Gathering

Ask the user:
1. Which framework? (Business Model Canvas / Lean Canvas / both)
2. Business description or idea (even rough is fine)
3. Stage: concept / validation / scaling / pivot
4. Existing materials (pitch deck, memo, prior canvas)

### Step 2: Draft Canvas

Generate a structured canvas filling each block with:
- **Content**: Concrete description (not generic placeholders)
- **Assumptions**: Key assumptions that need validation
- **Evidence**: Any supporting data or reasoning
- **Risk level**: High/Medium/Low for each block

### Step 3: Consistency Check

Validate cross-block coherence:

| Check | Description |
|-------|------------|
| **VP-CS alignment** | Does the value proposition actually solve the customer segment's problem? |
| **Revenue-Cost viability** | Can the revenue model sustain the cost structure? |
| **Channel-CS fit** | Do the channels effectively reach the target segments? |
| **Resource-Activity match** | Do key resources support key activities? |
| **Partnership necessity** | Are partnerships filling genuine capability gaps? |

### Step 4: Output Generation

#### Visual Canvas Format

```
┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
│ Key          │ Key          │ Value        │ Customer     │ Customer     │
│ Partners     │ Activities   │ Propositions │ Relationships│ Segments     │
│              ├──────────────┤              ├──────────────┤              │
│              │ Key          │              │ Channels     │              │
│              │ Resources    │              │              │              │
├──────────────┴──────────────┴──────────────┴──────────────┴──────────────┤
│ Cost Structure                             │ Revenue Streams             │
└────────────────────────────────────────────┴─────────────────────────────┘
```

#### Detailed Document Format

For each block, output:
```markdown
## [Block Name]

**Summary**: One-line description
**Details**: Detailed explanation with specifics
**Assumptions**: What we're assuming (to be validated)
**Risks**: What could go wrong
**Action Items**: Next steps to validate or strengthen
```

## Revenue Model Patterns

| Pattern | Description | Fit |
|---------|------------|-----|
| **SaaS Subscription** | Recurring fee by tier/seats | Predictable, scalable software |
| **Usage-Based** | Pay per API call/compute/storage | Variable demand, infrastructure |
| **Marketplace** | Transaction commission | Two-sided platforms |
| **Freemium** | Free tier + paid upgrades | High volume, viral growth |
| **Enterprise License** | Annual/multi-year contracts | Complex, high-touch sales |
| **Data Monetization** | Sell insights/analytics | Unique data assets |
| **Open Core** | OSS base + commercial features | Developer-first products |

## Iteration Support

When the user wants to iterate:
1. Show the change clearly (before/after for affected blocks)
2. Re-run consistency checks on affected blocks
3. Highlight new assumptions or risks introduced
4. Suggest cascading changes to related blocks

## Best Practices

1. **Be specific**: "Fortune 500 financial services IT teams" not "enterprises"
2. **Quantify where possible**: "$50/user/month" not "subscription pricing"
3. **Identify the riskiest assumption**: Flag the one thing that, if wrong, invalidates the model
4. **Separate facts from assumptions**: Clearly label what is known vs. hypothesized
5. **Consider alternatives**: For each block, briefly note what other options were considered
