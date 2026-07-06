[English](README.md) | [日本語](README_ja.md)

# dobachi-skills

Personal skills marketplace for Claude Code.

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

Requires the `claude` CLI, plus `python3` or `jq` (to parse the plugin list).
Then run `/reload-plugins` in a running session, or restart Claude Code.

From a local checkout you can run the same script directly — `./install.sh` — which
discovers plugins from the directory tree instead of fetching the manifest.

### Option B — install individual plugins in-session

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
