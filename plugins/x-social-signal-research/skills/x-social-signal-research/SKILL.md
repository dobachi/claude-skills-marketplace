---
name: x-social-signal-research
description: Research X/Twitter market signals with Hermes Tweet for competitive analysis, market sizing, and strategy work
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# X Social Signal Research

Use this skill when a research, competitive analysis, market sizing, startup, or strategy task depends on current X/Twitter signals.

## When to Use

- The user asks for competitor launch signals, customer language, founder narratives, category conversations, or market sentiment from X/Twitter.
- The output will feed `competitive-analysis`, `market-sizing`, `business-consultant`, `startup-advisor`, or `strategy-memo`.
- Current public posts or account-level context could materially change the conclusion.

## Hermes Tweet Setup

Hermes Tweet is optional. Install it when the environment supports Hermes Agent plugins:

```bash
hermes plugins install Xquik-dev/hermes-tweet
```

Live reads require `XQUIK_API_KEY`. If Hermes Tweet or the API key is unavailable, state that live X/Twitter evidence is unavailable and continue with other sources.

Account-changing actions require `HERMES_TWEET_ENABLE_ACTIONS=true` and explicit user confirmation. Default to read-only research.

## Workflow

1. Restate the research question and the decision it supports.
2. Define the accounts, posts, competitors, keywords, or hashtags to inspect.
3. Use Hermes Tweet for current public X/Twitter evidence only when recency matters.
4. Cross-check important claims with official pages, product docs, news, or other credible sources.
5. Summarize findings as sourced signals, not absolute market truth.
6. Translate signals into implications for positioning, competitors, demand, market size, or strategy.

## Output

Use this structure unless the user requested a different format:

```markdown
# X/Twitter Signal Brief: [Topic]

## Decision Context
- Research question:
- Decision supported:

## Signal Summary
| Signal | Evidence | Source | Confidence | Implication |
|--------|----------|--------|------------|-------------|

## Strategic Implications
- Competitive:
- Market:
- Messaging:
- Risk:

## Gaps
- Missing or unavailable evidence:
- Follow-up checks:
```

## Guardrails

- Do not post, like, repost, follow, delete, or change account state unless the user explicitly requests it and confirms the exact action.
- Do not treat X/Twitter as representative of the full market.
- Do not expose private account data, credentials, cookies, tokens, or internal routing details.
- Note stale, missing, or unverifiable evidence clearly.
