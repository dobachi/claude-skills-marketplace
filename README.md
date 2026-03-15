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

### Presentation

| Plugin | Description |
|---|---|
| **marp-slides** | Creates effective and professional presentations using Marp format. |

### Quality

| Plugin | Description |
|---|---|
| **fact-checker** | Automated fact-checking for AI-generated documents. Extracts claims and citations, verifies them in parallel via web search and Puppeteer headless browser, and generates a Markdown report. |
| **evidence-check** | Verifies the validity of references and citations in reports and papers, conducting evidence-based fact-checking. |

## Installation

### 1. Add the marketplace (first time only)

```
/plugin marketplace add dobachi/claude-skills-marketplace
```

### 2. Install a plugin

```
/plugin install fact-checker@dobachi-skills
```

### 3. Restart Claude Code

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

## Adding a New Plugin

1. Create a directory at `plugins/<plugin-name>/`
2. Write metadata in `.claude-plugin/plugin.json`
3. Place the skill body in `skills/<skill-name>/SKILL.md`
4. Add an entry to the `plugins` array in `.claude-plugin/marketplace.json`
5. Commit & push

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
