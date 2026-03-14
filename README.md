# dobachi-skills

Personal skills marketplace for Claude Code.

## Available Plugins

### 開発ツール (Development Tools)

| Plugin | Description |
|---|---|
| **build** | プロジェクトに適したビルドコマンドを検出・実行。Node.js、Rust、Python、Go、Makefileなど主要タイプに対応。 |
| **checkpoint** | AI指示書システムのチェックポイント管理。タスクの開始・進捗・完了を追跡し、指示書の使用状態を管理。 |
| **commit-and-report** | 変更のコミット、リモートへのプッシュ、GitHub Issueへの進捗報告を一括実行。 |
| **github-issues** | GitHub Issueの一覧取得、ラベル別集計、優先度分析を行い、タスクを整理・提案。 |
| **reload-instructions** | AI指示書サブモジュールを最新版に更新し、ROOT_INSTRUCTIONを再読み込み。 |
| **reload-and-reset** | AI指示書システムを最新版に更新し、AIの振る舞いを指示書に従った状態にリセット。 |
| **verify-content** | 文章の事実確認と参照検証を行う統合スキル。主張の洗い出し、外部ソースでの検証、参考文献の整備まで一貫実行。 |

### 役割スキル (Role Skills)

| Plugin | Description |
|---|---|
| **web-api-dev** | 本番環境向けの高品質なRESTful Web APIの設計・実装を支援する開発エキスパート。 |
| **cli-tool-dev** | 使いやすいコマンドラインツールの設計・実装を支援するCLI開発エキスパート。 |
| **data-analyst** | データ分析、統計的洞察、可視化、機械学習を含む包括的なデータ分析支援エキスパート。 |
| **technical-writer** | APIドキュメント、ユーザーガイド、技術ブログなど高品質な技術文書の作成を支援。 |
| **academic-researcher** | 学術論文執筆、文献レビュー、引用管理、研究方法論を含む包括的な学術研究支援。 |
| **business-consultant** | McKinsey・BCG等の方法論を用いた戦略立案から実行支援まで包括的なビジネスコンサルティング。 |
| **project-manager** | プロジェクトの計画、実行、監視、完了を総合的に管理。 |
| **startup-advisor** | スタートアップの立ち上げから成長まで、実践的なアドバイスと戦略的ガイダンスを提供。 |
| **python-expert** | Python開発の専門家として、クリーンコード、パフォーマンス最適化、テスト駆動開発を支援。 |
| **code-reviewer** | コード品質、セキュリティ、パフォーマンス、保守性の観点から建設的なレビューを提供。 |

### プレゼンテーション (Presentation)

| Plugin | Description |
|---|---|
| **marp-slides** | Marpフォーマットを活用した効果的でプロフェッショナルなプレゼンテーション作成を支援。 |

### 品質管理 (Quality)

| Plugin | Description |
|---|---|
| **fact-checker** | AI生成ドキュメントの自動ファクトチェック。主張・引用を抽出し、ウェブ検索とPuppeteerヘッドレスブラウザで並列検証、Markdownレポートを生成。 |
| **evidence-check** | レポートや論文の参考文献・引用の妥当性を検証し、エビデンスに基づくファクトチェックを実施。 |

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

### ファクトチェック / 品質管理

```
この報告書をファクトチェックして: /path/to/report.md
```

```
以下の文章の引用が正しいか検証して:
[テキストを貼り付け]
```

### 開発支援

```
このプロジェクトをビルドして
```

```
このPRのコードをレビューして
```

```
REST APIのエンドポイント設計を手伝って: ユーザー管理システム
```

### ドキュメント / プレゼンテーション

```
このAPIのリファレンスドキュメントを作成して
```

```
プロジェクト進捗報告のMarpスライドを作って
```

### データ分析 / リサーチ

```
このCSVデータを分析して傾向をレポートして: /path/to/data.csv
```

```
「大規模言語モデルのファインチューニング」に関する文献レビューを作成して
```

### プロジェクト管理

```
GitHub Issueを整理して優先度を分析して
```

```
変更をコミットしてIssue #42に進捗を報告して
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
