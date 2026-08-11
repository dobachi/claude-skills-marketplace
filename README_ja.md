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
| **commit-safe** | 変更を確認してから選択的にコミットし、開始時の「リリースまで含めますか？」に Yes ならそのままリリースまで運ぶ（バージョン更新・CHANGELOG・タグ・push・GitHub Release・パッケージ公開。不可逆な操作は毎回承認ゲート）。大きな変更ではファイル指定を提案し、`git add -A` を防止。AI署名を防ぐ自己完結の commit.sh と、読み取り専用の `release-preflight.sh` を同梱。 |
| **github-issues** | GitHub Issueの一覧取得、ラベル別集計、優先度分析を行い、タスクを整理・提案。 |
| **backlog** | 軽量で永続する「あとでやる」インボックス。1行で放り込み、別セッションで拾い直す。ハイブリッド保存（gitリポジトリ内は`<repo>/BACKLOG.md`、外は`~/.claude/backlog.md`）、`list`はリポジトリと個人の両方をまとめて表示、`archive`/棚卸しで済み項目を消し込む。`/backlog`や「これ積んでおいて」等の自然文で発火。stdlibのみ・エージェント横断。 |
| **reload-instructions** | AI指示書サブモジュールを最新版に更新し、ROOT_INSTRUCTIONを再読み込み。 |
| **reload-and-reset** | AI指示書システムを最新版に更新し、AIの振る舞いを指示書に従った状態にリセット。 |
| **verify-content** | 文章の事実確認と参照検証を行う統合スキル。主張の洗い出し、外部ソースでの検証、参考文献の整備まで一貫実行。 |
| **agent-delegate** | 現在のエージェントから別のCLIコーディングエージェント（Codex=`codex-delegate`、Antigravity/agy=`agy-delegate`、Claude Code=`claude-code-delegate`）へタスクを委譲。明示指示のみ・読み取り優先・書き込みは preview→確認→apply ゲートを経由し、各書き込みを OS サンドボックス（bubblewrap）で隔離。3スキルを同梱。 |
| **knowledge-base** | セッションをまたいで、どのエージェントからも使える永続ナレッジベース。プレーンMarkdown・1ディレクトリ=1KB・サーバもDBも不要なので、フォルダのコピーで持ち運べGit/OneDriveで同期できる。複数KB（`prose`/`entities` 形式）、索引→grep の想起、Claude Code / Codex / Antigravity(`agy`) で検証済みのエージェント横断アダプタを備える。stdlibのみの検証器を同梱。 |
| **skill-authoring** | **このマーケットプレイス**にスキルを追加・更新・リリースするための取り決め。一般的なスキル指南が扱わないリポジトリ固有の部分を持つ。`new_skill.sh` が雛形生成と登録、`release_check.sh` が出荷前ゲート — description の長さとYAML安全性、説明文を揃えるべき4箇所、バージョン更新、サイトカタログの鮮度、validator、同梱ハーネスの実行。忘れても症状が出ない項目だけを機械化してある。執筆ガイドと登録手順書を references として同梱。測定（evals・トリガ精度・版のA/B）は公式の `skill-creator` に委譲。 |

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
| **pptx-design** | プロフェッショナルなPowerPoint（.pptx）資料の設計ガイド。タイポグラフィ、配色、レイアウト、データビジュアライゼーション、構造図、資料ジャンル、アクセシビリティ、スライドマスタ設計。助言専用で、実ファイルの生成は `pptx-build` に引き渡す（手書きの python-pptx は書かない）。 |
| **pptx-build** | AIっぽく見えない、白基調でシンプルな.pptxファイルを生成。python-pptxベース。デフォルトモードは全要素を共有グリッドに固定し、ズレて見える帯を一切描かない設計。テンプレート流し込みモードは、実際の会社の.pptx/.potxを開いて、そのレイアウトとプレースホルダ（タイトル・本文など）に書き込み、テンプレートのマスター/テーマ/フォント/ロゴをそのまま継承。表・グラフのスライド型を備え、手書きの python-pptx に逃げる必要がない（それが白紙レイアウト＋テキストボックスの原因）。生成後の .pptx を検査する `audit_pptx.py` を同梱し、内容がプレースホルダに入っていないデッキはエラーにする。LibreOfficeプレビュー同梱。 |

### ドキュメンテーション (Documentation)

| Plugin | Description |
|---|---|
| **faithful-translation** | 任意の言語ペアで原文に忠実な翻訳を生成。検証用の文単位parallel ledger、用語集、訳者注を必須化。要約はせず、必要なら `document-summary` と連携。 |
| **document-summary** | 文献の構造化要約スキル。エグゼクティブ向け／プロフェッショナル向けの2モード。出典紐付けの Claim Ledger を全モード必須化し、原文に無い推論は `[Inference]` ブロックとして明示分離してハルシネーションを防止。 |
| **debrief-report** | 国際学会・商業カンファレンス・展示会・標準化会合・顧客訪問・社内討議の記録を、読者に合わせた報告書に変換。真実の源となる Markdown 報告書と、そこから派生させたエグゼクティブ向け `.pptx` の2成果物。着手前に「読者・依頼事項・公開範囲・当初の目的・イベント種別」を確定し、入力（AIトランスクリプト・写真・撮影スライド・予稿集・配布資料・同僚のメモ）を確度と秘匿区分つきで棚卸し、セッション順ではなく論点で再構成。事実／解釈／伝聞を分離した軽量な根拠台帳で裏づけ、並行トラックのイベントではカバレッジ（全M件中N件参加）を明示、「潮流」の主張には独立した3件以上の観測を要求し、ベンダー発表は GA／Preview／ロードマップ／コンセプトに分類してから論じる。イベント種別ごとの報告書・デッキ雛形を同梱。エグゼクティブサマリを冒頭に置き（BLUF）、示唆と担当・期限つきアクション表で締める。デッキ生成は `pptx-build` に委譲。日英対応。 |
| **social-post** | 記事・成果・登壇・会議参加などを告知/報告する LinkedIn 中心のSNS投稿を作成。書き出す前に「誰の投稿か」（個人／会社アカウント／所属を明示した個人＝「個人の見解です」の明示が必要で顧客名・機密は書けない）を確定し、トーンも推測せず確認する（既定はビジネスとカジュアルの中間）。"See more" で切れる冒頭約140字に結論を置き、具体（数字・固有名詞・実際の行動）を最低1つ要求。絵文字は上限つき、「このたび」「Thrilled to announce」型の定型開幕、絵文字の箇条書き、engagement bait、1文1行の broetry を禁止。日英は翻訳せず言語ごとに書き下ろす。成果物は2案＋フック3案＋1stコメント文＋ハッシュタグ＋事実・許諾チェック。最終のAIらしさ除去は `ai-tell-reducer` に委譲。X・Facebook・note への変換表つき。 |
| **document-figures** | 既存ドキュメント（PDF / Word / PowerPoint / Web）から図を出典付きで抽出し、新規の構造図（Mermaid 優先）を作成。`document-summary` と連携する Figure Ledger を生成。装飾的な箱・矢印は情報量テストで排除。Node.js 18+ / Puppeteer / poppler-utils が必要。 |
| **pdf-extract** | PDF からのテキスト・表・構造化フィールド抽出。まず同梱スクリプトでファイルを判定し（テキスト層の有無・段組み・スキャンか）、そのうえで最も安く済む経路へ振り分ける — ネイティブ抽出／OCR＋レイアウト解析パーサ／ビジョンモデル直接。抽出した各フィールドはページ番号と逐語スパンに紐づけ、機械的に検証できる形で返す。表の直列化形式、スキーマ拘束抽出、各経路の既知の失敗モードまで扱う。poppler-utils が必要。 |
| **doc-coauthoring** | 知識ベースに接地した文書の共同執筆ガイド — 文脈収集・節ごとの起草・読者テストの3段（任意・合成可）。事実・定義をドメイン知識ベースで裏取りして出典を付し、用語を統一。作業ファイルに起草し、人の [人] 編集を保持。批判レビュー/再構成/事実確認/脱AI/翻訳は兄弟スキルへ委譲。日英対応。 |
| **longform-discipline** | **長い**文章をAIと書くための規律と最小ワークフロー — 数万字から書籍規模、学術長文まで。長文は「下手に書かれる」のではなく「ドリフトする」ことで壊れる。計測されている3つの劣化軸（長い入力・長い出力・長いセッション）に対して規律を与える: 全体を一括生成しない、目的・アウトライン・用語集・文体契約・主張を持つ**スパインファイル**をコンテキスト外に置く、章は直前章の末尾を載せて逐次に書く、分割生成が必ず生む継ぎ目を修復する、アウトラインを凍結しない、そして合否は決定的スキャンと具体的な人手レビュー項目で決めAIの自己採点で決めない。各規律は出典付きの計測結果に紐づき、ベンチマーク間の**不一致もそのまま提示**する。同梱の `drift_scan.py`（標準ライブラリのみ）は**スパインを読んで実際に強制する**。表層だけでなく**意図**と**内容**も見る。意図台帳は着手前に完了条件を書かせ、「論を強くする」つもりが5往復後に語尾を直している、という**すり替わりを可視化**する。内容側は — 章が主旨の語を述べているか・未検証の主張・定義前に使われた用語・無出典の断定。意味が要る部分は `content-review.md` の章ごとの点検手順が受け持ち、人へ渡す番号付きレビューリストを作る。表層の検査: 宣言した文体契約への違反・用語集違反・**章をまたぐ数値の食い違い**（§2は200ms、§7は500ms）・文体混在・長すぎる一文・表記ゆれ・章間重複・章の痩せを検出し、ループの停止条件に使える終了コードを返す。任意の SudachiPy バックエンドを入れると、表に無い表記ゆれの検出が 0/8 → 6/8 になる（実測）。日本語規則は文化審議会建議「公用文作成の考え方」と JTF スタイルガイドが根拠。日英対応。 |
| **doc-refactor** | 文章ドキュメントをリファクタリング — コードのリファクタリングが挙動を保つように、意味を変えずに構造整理と重複削除を行う。診断優先のワークフロー（逆アウトライン → 課題棚卸し → 構造変更の確認 → リファクタ → 変更ログ）で、すべての主張・事実・図・著者の声を保ちつつ、実質的な問題は勝手に直さず指摘する。 |
| **ai-tell-reducer** | 文章の「AIっぽさ」を低減 — 単調な文のリズム、反射的なヘッジ、曖昧な抽象化、定型的な骨組み、大げさな語彙、表層的な癖（ダッシュ・太字・三点列挙の多用）を、意味・事実・レジスター・著者の声を保ったまま、何も捏造せずに整える。日本語・英語対応。 |
| **doc-review** | 文章ドキュメントの批判的レビュー（読み取り専用）— `/code-review` の散文版。ジャンル別ルーブリックで実質的な弱点（論の破綻・結論の埋没・薄い根拠・暗黙の前提・反論の欠如・読者ミスマッチ・内部矛盾）を洗い出し、自らの指摘を敵対的に検証してから、編集はせず優先度付きの指摘レポートを返す。日英対応。 |
| **essence-distiller** | アーティファクトの本質を見極め、本質でない部分を削ぎ落とす — `doc-refactor` の「引き算（via negativa）」版。散文/ドキュメント・仕様/要求・ソースコード・図を横断。その成果物の唯一の目的と読み手にとって荷重を支える部分と、重複・過剰装飾・飾り・埋め草・投機的一般化・早すぎる詳細・スコープクリープを切り分け、根拠と「何が失われるか」を添えて削除を提案する。`doc-refactor`（並べ替えのみ）と違い意図的に意味を変えるため、診断優先・非破壊・提案してから確認。すべての削除を「明示した目的＋読み手」に紐づけ、チェスタトンの垣根（理由が分からないものは削らず指摘）を守り、正しさ・挙動を保つ。日英対応。 |
| **humanize-prose** | AI生成／AI補助のテキストを人間が書いたように書き換え。よくあるAIの癖（ダッシュ多用・delve/leverage・三点列挙・反射的な箇条書き・定型的な書き出し／締め）を、意味・レジスター・事実を保ったまま低減。英語・日本語対応。 |
| **math-paper** | 数学論文の執筆支援：記法の一貫性（Symbol Ledger）、定理／証明の構造、数式の相互参照、ジャーナル／arXiv 投稿準備。LaTeX と Markdown+math に対応。 |

### エンタープライズアーキテクチャ & エンジニアリング (Enterprise Architecture & Engineering)

| Plugin | Description |
|---|---|
| **archimate-ea** | 対話型 ArchiMate 3.2 EA ファシリテーター（グリーンフィールド）。要求を引き出し、レイヤ全体を単一のYAML真実源として設計、メタモデル検証の上、PlantUMLビューと Open Group Exchange XML（Archi用）を生成。 |
| **archimate-native** | ブラウンフィールド ArchiMate：既存の `.archimate` ファイルを真実源として読解・レビュー・解釈・その場で外科的に編集（往復安全。id/座標/フォルダ/スタイル保持）。archimate-ea の対。 |
| **requirements-stories** | 対話型の要求定義・ユーザーストーリー ファシリテーター。プロダクトバックログ（ペルソナ、エピック、Given-When-Then／ルール形式の受入基準を伴うユーザーストーリー、EARS記法の非機能要求、ストーリーマップ、MoSCoW／WSJF 優先順位づけ）を単一の `backlog.yaml` 真実源として育て、INVEST/EARS/構造の品質を検証し、Markdownバックログと Gherkin フィーチャーファイルを生成。各ストーリーを ArchiMate の `ea-model.yaml`（読み取り専用の上流）へ双方向カバレッジ検証付きでトレースし、archimate-ea と archimate-to-impl を橋渡し。EAモデルなしの単独利用も可能。 |
| **tech-selector** | EAモデルの非機能要求から具体的なミドルウェア／ランタイムを選定：重み付き・感度分析付き評価、根拠のADR、決定のTechnology層への書き戻し。 |
| **archimate-to-impl** | EAモデルのApplication層を実装へ橋渡し：要求→コンポーネント→サービス→api→タスクのトレーサビリティ、サービス別OpenAPIスケルトン、DataObjectスタブ、コンポーネント別タスク、孤児チェック。 |
| **ea-delivery** | EA駆動デリバリの一気通貫コンダクター：要求→設計→ミドルウェア選定→実装→サービス化を専門スキル間で順序づけ、`ea-model.yaml` を軸に各ハンドオフをゲート。 |
| **web-frontend-dev** | 本番Webフロントエンド（SPA以上）を構築：コンポーネント設計、状態管理、キャッシュ付きAPIデータ取得、フォーム／テーブル、認証・セッションUI、アクセシビリティ。OpenAPI契約を消費。 |
| **event-driven-service** | REST以外のイベント駆動・非同期・リアルタイムサービスを設計：メッセージング（キュー／ストリーム）、非同期ワーカー、スケジュールジョブ、WebSocket/SSEプッシュ。冪等性・順序・配信保証・バックプレッシャに対応。 |
| **plugin-platform** | プラグイン／拡張基盤（例：アルゴリズムマーケット）を設計：安定したバージョン付きSDK契約、探索・互換性を持つレジストリ、サンドボックス化と最小権限による未信頼コードの安全実行。 |
| **simulation-harness** | シミュレーション／バックテスト基盤を構築：シナリオ生成、離散イベント／時間ステップモデル実行、履歴リプレイ、メトリクス収集、固定シードでの再現可能なA/B比較。 |
| **optimization-modeling** | 数理最適化／意思決定エンジニアリング：意思決定をLP/MILP/凸/確率モデルとして定式化、ソルバーを駆動、不確実性（確率的・ロバスト）を扱い、実行可能性・感度で検証。 |

### 研究 (Research)

| Plugin | Description |
|---|---|
| **grounded-research** | ハルシネーション対策を設計そのものに組み込んだ複数ソース調査。収集サブエージェントは逐語引用スパンのみを返し、追記専用のソース台帳に行がない主張は本文に書けない。各主張はドラフトを見せない目隠し検証にかけ、出典間の食い違いは平均せずそのまま提示する。討論や多数決は意図的に使わない。 |
| **literature-search** | 文献検索・引用チェイス・スノーボーリング(Wohlin法)・著者プロファイル+h-index・BibTeX 出力・撤回論文チェックを、無料公式API(Semantic Scholar + OpenAlex + CrossRef)のみで実現。スクレイピングや有料サービスを使わない誠実な Google Scholar 代替。Node.js 18+ が必要。 |

### 品質管理 (Quality)

| Plugin | Description |
|---|---|
| **fact-checker** | AI生成ドキュメントの自動ファクトチェック。主張・引用を抽出し、ウェブ検索とPuppeteerヘッドレスブラウザで並列検証、Markdownレポートを生成。 |
| **evidence-check** | レポートや論文の参考文献・引用の妥当性を検証し、エビデンスに基づくファクトチェックを実施。 |
| **loop-goal** | 「OKになるまで直して」を、機械が判定できる停止条件に変える — **文書の**検証ループ向け。終了条件を決定的な検出器の終了コードに落とし、検出器を1本ではなく**集合**でゲートにし、削除でゲートを満たせないよう単調性の下限を添え、生成側と採点側の境界を指示ではなく機構で担保する。依存なしの検出器11本とフィクスチャ、`test_detectors.sh` を同梱。測るのは追跡可能性であって正しさではない。対象は文書に限る（コードは既製の判定器があり事情が違う）。 |

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

### Claude Desktop / claude.ai

カスタムスキルは各サーフェス間で**同期しません**（Claude Code・claude.ai・Skills API は
別々のストア）。一括アップロード経路も無いため、Claude Desktop アプリに入れるにはスキル
ごとに `.zip` を1つずつ手動アップロードします。自動化できる部分（梱包と検証）は2つの
支援ツールが担い、アップロードは手動のままです。

```bash
python3 tools/pack-desktop.py                 # viable なスキルを zip 化 → dist/desktop/
python3 tools/pack-desktop.py --experimental  # スクリプト同梱のものも含める
python3 tools/pack-desktop.py --only doc-review --out "$(wslpath /mnt/c/Users/you/Downloads)"
```

出力は `dist/desktop/`（git 管理外）に、`<skill>.zip` 群・順序付きチェックリスト
`UPLOAD.md`・ハッシュ台帳（再梱包時に変更分だけを表示）としてまとまります。あとはアプリの
スキル設定で各 zip をアップロードするだけです。梱包対象の一覧や初回アップロード時に確認す
べき点を含む詳細は [docs/claude-desktop-packaging.md](./docs/claude-desktop-packaging.md)。

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

pdf-extract プラグインは以下を必要とします：

- **poppler-utils** — `pdfinfo`, `pdftotext`, `pdffonts`, `pdfimages`（`apt install poppler-utils` または `brew install poppler`）
- **（任意）OCRmyPDF + Tesseract** — OCR 経路を使う場合のみ（`apt install ocrmypdf tesseract-ocr` または `brew install ocrmypdf tesseract`）

## Adding a New Plugin

1. `plugins/<plugin-name>/` にディレクトリを作成
2. `.claude-plugin/plugin.json` にメタデータを記述
3. `skills/<skill-name>/SKILL.md` にスキル本体を配置
4. `.claude-plugin/marketplace.json` の `plugins` 配列にエントリを追加
5. 検証: `python3 tools/validate_skills.py`（CI も同じチェックを実行）
6. コミット & プッシュ

パッケージ済み `.skill` ファイルの取り込み、既存プラグインの更新、検証、インストールまでの
詳細な手順は [`skill-authoring` スキル](plugins/skill-authoring/skills/skill-authoring/references/registration-runbook.md) を参照してください。

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
