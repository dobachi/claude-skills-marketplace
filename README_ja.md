[English](README.md) | [日本語](README_ja.md)

# dobachi-skills

Claude Code 用の個人スキルマーケットプレイス。さらに `install.sh` 経由で、同じ
[Agent Skills](https://agentskills.io) の `SKILL.md` 形式を読む他のコーディング
エージェント（OpenAI Codex CLI・Gemini CLI・Google Antigravity）でも使えます。

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
| **tauri-dev** | Tauri v2デスクトップ・モバイルアプリケーションの設計・構築を支援する開発エキスパート。 |
| **tauri-research** | Tauri関連の疑問をWeb検索・公式ドキュメントで調査するリサーチアシスタント。 |
| **competitive-analysis** | Web検索で競合製品を調査し、機能・価格・差別化ポイントを比較マトリクスとして生成。 |
| **business-model-canvas** | Business Model Canvas・Lean Canvasフレームワークに沿った構造化されたビジネスモデル文書を生成。 |
| **market-sizing** | TAM/SAM/SOMフレームワークでTop-down・Bottom-upの市場規模推定を行い、根拠付きレポートを生成。 |
| **strategy-memo** | ビジネスアイデアを4層構造（市場・価値提案・技術・実行）に整理し、論点の抜け漏れをチェック。 |

### プレゼンテーション (Presentation)

| Plugin | Description |
|---|---|
| **marp-slides** | Marpフォーマットを活用した効果的でプロフェッショナルなプレゼンテーション作成を支援。 |
| **pptx-design** | PowerPoint（.pptx）デッキの設計支援エキスパート。タイポグラフィ・配色・レイアウト・データ可視化・構造図／アーキ図・デッキジャンル別作法・アクセシビリティを網羅。装飾的な箱・矢印を排し、構造を符号化する図のみを採用。 |
| **pptx-build** | AIっぽく見えない、白基調でシンプルな.pptxファイルを生成。python-pptxベース。デフォルトモードは全要素を共有グリッドに固定し、ズレて見える帯を一切描かない設計。テンプレート流し込みモードは、実際の会社の.pptx/.potxを開いて、そのレイアウトとプレースホルダ（タイトル・本文など）に書き込み、テンプレートのマスター/テーマ/フォント/ロゴをそのまま継承。LibreOfficeプレビュー同梱。 |

### ドキュメンテーション (Documentation)

| Plugin | Description |
|---|---|
| **faithful-translation** | 任意の言語ペアで原文に忠実な翻訳を生成。検証用の文単位parallel ledger、用語集、訳者注を必須化。要約はせず、必要なら `document-summary` と連携。 |
| **document-summary** | 文献の構造化要約スキル。エグゼクティブ向け／プロフェッショナル向けの2モード。出典紐付けの Claim Ledger を全モード必須化し、原文に無い推論は `[Inference]` ブロックとして明示分離してハルシネーションを防止。 |
| **document-figures** | 既存ドキュメント（PDF / Word / PowerPoint / Web）から図を出典付きで抽出し、新規の構造図（Mermaid 優先）を作成。`document-summary` と連携する Figure Ledger を生成。装飾的な箱・矢印は情報量テストで排除。Node.js 18+ / Puppeteer / poppler-utils が必要。 |
| **doc-coauthoring** | 知識ベースに接地した文書の共同執筆ガイド — 文脈収集・節ごとの起草・読者テストの3段（任意・合成可）。事実・定義をドメイン知識ベースで裏取りして出典を付し、用語を統一。作業ファイルに起草し、人の [人] 編集を保持。批判レビュー/再構成/事実確認/脱AI/翻訳は兄弟スキルへ委譲。日英対応。 |
| **doc-refactor** | 文章ドキュメントをリファクタリング — コードのリファクタリングが挙動を保つように、意味を変えずに構造整理と重複削除を行う。診断優先のワークフロー（逆アウトライン → 課題棚卸し → 構造変更の確認 → リファクタ → 変更ログ）で、すべての主張・事実・図・著者の声を保ちつつ、実質的な問題は勝手に直さず指摘する。 |
| **ai-tell-reducer** | 文章の「AIっぽさ」を低減 — 単調な文のリズム、反射的なヘッジ、曖昧な抽象化、定型的な骨組み、大げさな語彙、表層的な癖（ダッシュ・太字・三点列挙の多用）を、意味・事実・レジスター・著者の声を保ったまま、何も捏造せずに整える。日本語・英語対応。 |

### 研究 (Research)

| Plugin | Description |
|---|---|
| **literature-search** | 文献検索・引用チェイス・スノーボーリング(Wohlin法)・著者プロファイル+h-index・BibTeX 出力・撤回論文チェックを、無料公式API(Semantic Scholar + OpenAlex + CrossRef)のみで実現。スクレイピングや有料サービスを使わない誠実な Google Scholar 代替。Node.js 18+ が必要。 |

### 品質管理 (Quality)

| Plugin | Description |
|---|---|
| **fact-checker** | AI生成ドキュメントの自動ファクトチェック。主張・引用を抽出し、ウェブ検索とPuppeteerヘッドレスブラウザで並列検証、Markdownレポートを生成。 |
| **evidence-check** | レポートや論文の参考文献・引用の妥当性を検証し、エビデンスに基づくファクトチェックを実施。 |

## Installation

### 方法A — ワンライナー：マーケット登録から全プラグイン導入まで

clone不要。GitHubからマーケットを登録し、全プラグインを一括インストールします。

```bash
curl -fsSL https://raw.githubusercontent.com/dobachi/claude-skills-marketplace/master/install.sh | bash
```

必要なもの: `claude` CLI、`git`（ワンライナー時）、`python3` または `jq`。
実行後、起動中セッションでは `/reload-plugins`、または Claude Code を再起動してください。

ローカルにcloneしている場合は同じスクリプトを `./install.sh` で直接実行できます。

インストーラはスキルの**実体を1つ**（`SRC_DIR`）に保ち、全エージェントをそこへ向けます。
`git pull` 1回で全エージェントに反映されます。

- **checkout モード**（`./install.sh`）— `SRC_DIR` は clone したディレクトリ。
- **ワンライナー モード**（`curl … | bash`）— `SRC_DIR` は中立クローン
  `${XDG_DATA_HOME:-~/.local/share}/agent-skills/dobachi-skills`（Claude 内部キャッシュ
  ではないので、他エージェントがそこに依存しません）。

別ソースが既に登録されている場合は、無断で上書きせず**照合（reconcile）**します。切替は
`--force`、状態確認は `--status`。主なフラグ:

| フラグ | 効果 |
|--------|------|
| `--status` | 各エージェントの現在の向き先を表示して終了（変更なし） |
| `--force` | 全エージェントを今回の `SRC_DIR` に切替。孤立 `.bak`・古い symlink を掃除 |
| `--no-agents` | Claude Code のマーケット登録のみ。他エージェントはスキップ |
| `--extra-dir DIR` | 追加の探索ディレクトリにもリンク（複数指定可） |
| `--unlink` | 本スクリプトが作成した他エージェント向け symlink を削除 |

### 他のコーディングエージェント（Codex CLI・Gemini CLI・Antigravity）

`install.sh` は各スキルを、これらのエージェントが走査する探索ディレクトリへ symlink します。
形式変換は不要で、実体1つを共有するだけです。

| エージェント | 読み込む探索ディレクトリ | 出典 |
|--------------|--------------------------|------|
| Codex CLI | `~/.agents/skills/` | [OpenAI docs](https://learn.chatgpt.com/docs/build-skills) |
| Gemini CLI | `~/.gemini/skills/`（`~/.agents/skills/` も読む） | [Google docs](https://geminicli.com/docs/cli/skills/) |
| Antigravity CLI (1.0.x) | `~/.agents/skills/`（`agy` で実測確認） | [Google codelabs](https://codelabs.developers.google.com/getting-started-with-antigravity-skills) |

既定の実行で `~/.agents/skills/` と `~/.gemini/skills/` にリンクし、上記3つを全てカバーします。
**Antigravity IDE** だけは `~/.gemini/config/skills/` を読むため、その場合は
`./install.sh --extra-dir ~/.gemini/config/skills` を使ってください。新規リンクの反映には
エージェントの再起動（または新セッション）が必要です。ヘルパースクリプトを同梱するスキルは、
実行時ランタイム（例: `python3` とスキルの `requirements.txt`）が別途必要です。

### 方法B — セッション内で個別にインストール（Claude Code）

**1. マーケットプレイスを追加（初回のみ）**

```
/plugin marketplace add dobachi/claude-skills-marketplace
```

**2. プラグインをインストール**

```
/plugin install fact-checker@dobachi-skills
```

**3. Claude Codeを再起動**

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

### ビジネス戦略

```
競合分析をして: Palantir vs Databricks vs Snowflake
```

```
データガバナンスSaaS製品のビジネスモデルキャンバスを作成して
```

```
北米のデータカタログ市場のTAM/SAM/SOMを推定して
```

```
このアイデアメモを戦略メモに構造化して: [メモを貼り付け]
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

document-figures プラグインは以下を必要とします：

- **Node.js** (v18+)
- **Puppeteer** — `npm install puppeteer`
- **poppler-utils** — `pdfimages`, `pdftocairo`, `pdftotext`（`apt install poppler-utils` または `brew install poppler`）
- **xmllint** — `apt install libxml2-utils` または `brew install libxml2`
- **（任意）LibreOffice** — PPTX のスライドを PNG レンダリングする場合に使用

## Adding a New Plugin

1. `plugins/<plugin-name>/` にディレクトリを作成
2. `.claude-plugin/plugin.json` にメタデータを記述
3. `skills/<skill-name>/SKILL.md` にスキル本体を配置
4. `.claude-plugin/marketplace.json` の `plugins` 配列にエントリを追加
5. コミット & プッシュ

パッケージ済み `.skill` ファイルの取り込み、既存プラグインの更新、検証、インストールまでの
詳細な手順は [docs/adding-or-updating-a-skill.md](docs/adding-or-updating-a-skill.md) を参照してください。

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
