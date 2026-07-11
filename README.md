[English](README.md) | [日本語](README_ja.md)

# dobachi-skills

Personal skills marketplace for Claude Code — and, via `install.sh`, for other coding
agents (OpenAI Codex CLI, Gemini CLI, Google Antigravity) that read the same
[Agent Skills](https://agentskills.io) `SKILL.md` format.

## Available Plugins

### Development Tools

| Plugin | Description |
|---|---|
| **build** | Detects and runs the appropriate build command for your project. Supports Node.js, Rust, Python, Go, Makefile, and more. |
| **checkpoint** | Checkpoint management for AI instruction systems. Tracks task start, progress, and completion, and manages instruction usage state. |
| **commit-and-report** | Commits changes, pushes to remote, and reports progress to GitHub Issues in one step. |
| **github-issues** | Lists GitHub Issues, aggregates by label, analyzes priorities, and organizes/suggests tasks. |
| **reload-instructions** | Updates AI instruction submodules to the latest version and reloads ROOT_INSTRUCTION. |
| **reload-and-reset** | Updates the AI instruction system to the latest version and resets AI behavior to follow instructions. |
| **verify-content** | Integrated skill for fact-checking and reference verification. Identifies claims, verifies with external sources, and organizes references. |
| **agent-delegate** | Delegate a task to another CLI coding agent — Codex (`codex-delegate`), Antigravity/agy (`agy-delegate`), or Claude Code (`claude-code-delegate`) — from your current agent. Explicit-invocation only, read-first routing, and a preview→confirm→apply gate for any write. Bundles three skills. |

### Role Skills

| Plugin | Description |
|---|---|
| **web-api-dev** | Development expert for designing and implementing production-grade RESTful Web APIs. |
| **cli-tool-dev** | CLI development expert for designing and implementing user-friendly command-line tools. |
| **data-analyst** | Comprehensive data analysis expert covering data analysis, statistical insights, visualization, and machine learning. |
| **technical-writer** | Creates high-quality technical documents including API docs, user guides, and technical blogs. |
| **academic-researcher** | Comprehensive academic research support including paper writing, literature reviews, citation management, and research methodology. |
| **business-consultant** | Comprehensive business consulting from strategy planning to execution using McKinsey/BCG methodologies. |
| **project-manager** | Comprehensive project planning, execution, monitoring, and completion management. |
| **startup-advisor** | Practical advice and strategic guidance from startup launch to growth. |
| **python-expert** | Python development expert supporting clean code, performance optimization, and test-driven development. |
| **code-reviewer** | Provides constructive reviews from the perspectives of code quality, security, performance, and maintainability. |
| **tauri-dev** | Development expert for designing and building Tauri v2 desktop and mobile applications. |
| **tauri-research** | Research assistant for investigating Tauri-related questions via web search and official documentation. |
| **competitive-analysis** | Researches competitor products via web search, compares features/pricing/differentiation, and generates comparison matrices. |
| **business-model-canvas** | Generates structured business model documents following Business Model Canvas and Lean Canvas frameworks. |
| **market-sizing** | Estimates TAM/SAM/SOM market size using top-down and bottom-up approaches with evidence-backed reports. |
| **strategy-memo** | Structures business ideas into a 4-layer framework (Market/Value Proposition/Technology/Execution) and checks for logical gaps. |

### Presentation

| Plugin | Description |
|---|---|
| **marp-slides** | Creates effective and professional presentations using Marp format. |
| **pptx-design** | Expert guidance for designing professional PowerPoint (.pptx) decks: typography, color, layout, data visualization, structural diagrams, deck genres, and accessibility. |
| **pptx-build** | Generates clean, white-based .pptx files that don't look AI-made — built on python-pptx. Default mode: grid-anchored from-scratch layout with no drifting decorative bands. Template-fill mode: opens a real corporate .pptx/.potx and writes into its layouts and placeholders, inheriting the template's master/theme/fonts/logos. LibreOffice preview. |

### Documentation

| Plugin | Description |
|---|---|
| **faithful-translation** | Produces source-faithful translations across any language pair with a parallel sentence ledger, terminology glossary, and translator's notes. No summarization — chain with `document-summary` if you need both. |
| **document-summary** | Structured document/literature summarization with Executive and Professional modes. Mandatory source-grounded Claim Ledger and Source-vs-Inference separation prevent hallucinated content. |
| **document-figures** | Extracts figures from existing documents (PDF / Word / PowerPoint / web) with provenance and creates new structural diagrams (Mermaid-first). Produces a Figure Ledger that chains into `document-summary`. Requires Node.js 18+, Puppeteer, and poppler-utils. |
| **doc-coauthoring** | Guided, knowledge-grounded co-authoring workflow for substantial documents — three optional, composable stages (context gathering, section-by-section drafting, reader-testing). Grounds facts in a domain knowledge base with cited sources and consistent terminology, drafts into a working file, preserves human [人] edits, and hands off review/refactor/fact-check/de-AI/translation to sibling skills. Bilingual JA/EN. |
| **doc-refactor** | Refactors prose documents — restructures and de-duplicates without changing meaning, the way code refactoring preserves behavior. Diagnose-first workflow (reverse outline → issue inventory → confirm moves → refactor → change log) that preserves every claim, fact, figure, and the author's voice, and flags substantive problems instead of silently fixing them. |
| **ai-tell-reducer** | Reduces the "AI-ness" of writing — uniform sentence rhythm, reflexive hedging, vague abstraction, formulaic scaffolding, inflated vocabulary, and surface tics (em-dash / bold / rule-of-three overuse) — while preserving meaning, facts, register, and the author's voice, and without fabricating anything. Bilingual (Japanese / English). |

### Research

| Plugin | Description |
|---|---|
| **literature-search** | Literature search, citation chasing, snowballing (Wohlin), author profile + h-index, BibTeX export, and retraction screening using free official APIs (Semantic Scholar + OpenAlex + CrossRef). Honest Google Scholar alternative — no scraping, no paid services. Requires Node.js 18+. |

### Quality

| Plugin | Description |
|---|---|
| **fact-checker** | Automated fact-checking for AI-generated documents. Extracts claims and citations, verifies them in parallel via web search and Puppeteer headless browser, and generates a Markdown report. |
| **evidence-check** | Verifies the validity of references and citations in reports and papers, conducting evidence-based fact-checking. |

## Installation

### Option A — one-liner: register the marketplace and install every plugin

No clone required. Registers the marketplace from GitHub and installs all plugins:

```bash
curl -fsSL https://raw.githubusercontent.com/dobachi/claude-skills-marketplace/master/install.sh | bash
```

Requires the `claude` CLI, plus `git` (one-liner mode) and `python3` or `jq`.
Then run `/reload-plugins` in a running session, or restart Claude Code.

From a local checkout you can run the same script directly — `./install.sh`.

The installer keeps **one on-disk copy** of the skills (`SRC_DIR`) and points every
agent at it, so a single `git pull` updates all of them:

- **checkout mode** (`./install.sh`) — `SRC_DIR` is your checkout.
- **one-liner mode** (`curl … | bash`) — `SRC_DIR` is a neutral clone at
  `${XDG_DATA_HOME:-~/.local/share}/agent-skills/dobachi-skills` (not Claude's private
  plugin cache, so the other agents don't couple to it).

If a different source is already registered it **reconciles** instead of silently
overwriting; use `--force` to switch, `--status` to inspect. Useful flags:

| Flag | Effect |
|------|--------|
| `--status` | Show what every agent currently points at, then exit (no changes) |
| `--force` | Switch all agents to this run's `SRC_DIR`; clean stale `.bak` clones/symlinks |
| `--no-agents` | Only (re)register the Claude Code marketplace; skip the other agents |
| `--extra-dir DIR` | Also link into an additional discovery dir (repeatable) |
| `--unlink` | Remove the symlinks this script created from the other agents |

### Other coding agents (Codex CLI, Gemini CLI, Antigravity)

`install.sh` also symlinks each skill into the discovery dirs these agents scan, so the
same skills light up there too — no format conversion, just one shared copy:

| Agent | Discovery dir it reads | Source |
|-------|------------------------|--------|
| Codex CLI | `~/.agents/skills/` | [OpenAI docs](https://learn.chatgpt.com/docs/build-skills) |
| Gemini CLI | `~/.gemini/skills/` (also reads `~/.agents/skills/`) | [Google docs](https://geminicli.com/docs/cli/skills/) |
| Antigravity CLI (1.0.x) | `~/.agents/skills/` (verified with `agy`) | [Google codelabs](https://codelabs.developers.google.com/getting-started-with-antigravity-skills) |

The default run links `~/.agents/skills/` and `~/.gemini/skills/`, which covers all
three. The **Antigravity IDE** reads `~/.gemini/config/skills/` instead — add it with
`./install.sh --extra-dir ~/.gemini/config/skills`. Restart the agent (or start a new
session) to pick up newly linked skills. Skills that ship helper scripts still need
their runtime present (e.g. `python3` + the packages in the skill's `requirements.txt`).

### Option B — install individual plugins in-session (Claude Code)

**1. Add the marketplace (first time only)**

```
/plugin marketplace add dobachi/claude-skills-marketplace
```

**2. Install a plugin**

```
/plugin install fact-checker@dobachi-skills
```

**3. Restart Claude Code**

After installation, restart Claude Code to activate the plugin.

## Usage

After installation, you can use it in Claude Code like this:

### Fact-checking / Quality

```
Fact-check this report: /path/to/report.md
```

```
Verify the citations in the following text:
[paste your text]
```

### Development

```
Build this project
```

```
Review the code in this PR
```

```
Help me design REST API endpoints: user management system
```

### Documentation / Presentation

```
Create reference documentation for this API
```

```
Create a Marp slide deck for the project progress report
```

### Data Analysis / Research

```
Analyze this CSV data and report trends: /path/to/data.csv
```

```
Create a literature review on "fine-tuning large language models"
```

### Business Strategy

```
Conduct a competitive analysis: Palantir vs Databricks vs Snowflake
```

```
Create a Business Model Canvas for a data governance SaaS product
```

```
Estimate the TAM/SAM/SOM for the data catalog market in North America
```

```
Structure this idea memo into a strategy memo: [paste your notes]
```

### Project Management

```
Organize GitHub Issues and analyze priorities
```

```
Commit changes and report progress to Issue #42
```

## Update

To fetch marketplace updates:

```
/plugin marketplace update dobachi-skills
```

## Prerequisites

The fact-checker plugin requires:

- **Node.js** (v18+)
- **Puppeteer** — Install with `npm install puppeteer`

The document-figures plugin requires:

- **Node.js** (v18+)
- **Puppeteer** — `npm install puppeteer`
- **poppler-utils** — `pdfimages`, `pdftocairo`, `pdftotext` (`apt install poppler-utils` or `brew install poppler`)
- **xmllint** — `apt install libxml2-utils` or `brew install libxml2`
- **(optional) LibreOffice** — for slide-to-PNG rendering of PPTX

## Adding a New Plugin

1. Create a directory at `plugins/<plugin-name>/`
2. Write metadata in `.claude-plugin/plugin.json`
3. Place the skill body in `skills/<skill-name>/SKILL.md`
4. Add an entry to the `plugins` array in `.claude-plugin/marketplace.json`
5. Commit & push

For the full step-by-step procedure (importing a packaged `.skill` file, updating an
existing plugin, validation, and installation), see
[docs/adding-or-updating-a-skill.md](docs/adding-or-updating-a-skill.md).

```
plugins/<plugin-name>/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    └── <skill-name>/
        ├── SKILL.md
        ├── scripts/
        ├── references/
        └── assets/
```

## Private Repository Access

If this repository is private, GitHub authentication is required on each machine:

```bash
gh auth login
```

Or set the `GITHUB_TOKEN` environment variable.
