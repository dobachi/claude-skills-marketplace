# dobachi-skills

Personal skills marketplace for Claude Code.

## Available Plugins

| Plugin | Description |
|---|---|
| **fact-checker** | AI生成ドキュメントの自動ファクトチェック。主張・引用を抽出し、ウェブ検索とPuppeteerヘッドレスブラウザで並列検証、Markdownレポートを生成。 |

## Installation

### 1. マーケットプレイスを追加（初回のみ）

```
/plugin marketplace add dobachi/claude-skills-marketplace
```

### 2. プラグインをインストール

```
/plugin install fact-checker@dobachi-skills
```

### 3. Claude Codeを再起動

インストール後、Claude Codeを再起動すると有効になります。

## Usage

インストール後、Claude Codeで以下のように使えます。

```
この報告書をファクトチェックして: /path/to/report.md
```

```
以下の文章の引用が正しいか検証して:
[テキストを貼り付け]
```

## Update

マーケットプレイスの更新を取得するには：

```
/plugin marketplace update dobachi-skills
```

## Prerequisites

fact-checker プラグインは以下を必要とします：

- **Node.js** (v18+)
- **Puppeteer** — `npm install puppeteer` でインストール

## Adding a New Plugin

1. `plugins/<plugin-name>/` にディレクトリを作成
2. `.claude-plugin/plugin.json` にメタデータを記述
3. `skills/<skill-name>/SKILL.md` にスキル本体を配置
4. `.claude-plugin/marketplace.json` の `plugins` 配列にエントリを追加
5. コミット & プッシュ

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

このリポジトリがプライベートの場合、各マシンで GitHub 認証が必要です：

```bash
gh auth login
```

または環境変数 `GITHUB_TOKEN` を設定してください。
