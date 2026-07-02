# EA駆動デリバリー・スキル拡充計画

エンタープライズアーキテクチャ(EA)の考え方で **要求分析 → アーキテクチャ設計 →
ミドルウェア選定 → ソフトウェア開発 → サービス化** を一気通貫で回すために、
このマーケットプレイスへ追加すべきスキルの設計提案。

- ステータス: 計画確定(実装未着手)
- スコープ: 新規8スキル(EA駆動フローを閉じる3枚 + 実装能力5枚)
- スコープ外: ドメイン知識スキル、サービス化後半のIaC/CI-CD/監視(将来P3)

---

## 1. 背景と目的

既存スキルを EA駆動フローに並べ直すと、中核の `archimate-ea`(要求分析・設計)は
YAML running model + バリデータ + PlantUML/XML emit を備えた**ツール裏付け型**で
完成度が高い一方、その下流(選定・実装橋渡し・具体実装能力)に構造的な穴がある。

本計画は、その穴を **関心を分離した小さなスキルの積み重ね**で埋め、EAモデルの
`ea-model.yaml` を唯一の真実として工程間を縫うことを目的とする。

## 2. 駆動ユースケース(抽象化アーキタイプ)

計画の妥当性は、具体的な実現対象を抽象化した**アーキタイプ**で検証する。特定案件や
対象領域は伏せ、能力要件だけを取り出す:

> **プラットフォーム型サービスのアーキタイプ** — 多数の参加者が投入するオファーを
> 捌く**取引/マッチングのコア**、その意思決定を支援する**アルゴリズム群**、そして
> アルゴリズムを第三者が登録・流通できる**プラグイン市場**を備えるサービス(まずは
> モックとして実現)。

このアーキタイプを実装能力に分解すると、取引API・マッチング、最適化アルゴリズム、
プラグイン基盤、シミュレーション、UI が必要になり、既存スキルで埋まらない穴を
炙り出す(§4B)。※ 対象領域固有のルールや理論そのものは**ドメイン知識**として
本計画から除外。

## 3. スキル全体マップ

```
【W ea-delivery = 薄い司令塔:通し状態 ea-model.yaml・工程ゲート・後戻り管理】
   ↓委譲       ↓委譲          ↓委譲            ↓委譲          ↓委譲
要求分析 → 設計 → P1 tech-selector → P2 archimate-to-impl → 開発 → サービス化
archimate-ea(既存)                                     実装能力群(下記)  pm/commit(既存)
                    ▲                        │
                    └───後戻り(新非機能要求)───┘

実装能力群(アーキタイプで顕在化した横断スキル):
  G1 plugin-platform / G2 optimization-modeling / G3 event-driven-service
  G4 simulation-harness / G5 web-frontend-dev
```

| # | スキル | カテゴリ | 型 | 状態 |
|---|--------|---------|----|------|
| P1 | `tech-selector` | 鎖を閉じる | ツール型 | 新規 |
| P2 | `archimate-to-impl` | 鎖を閉じる | ツール型 | 新規 |
| W  | `ea-delivery` | 鎖を閉じる(司令塔) | 指示型(薄い) | 新規 |
| G1 | `plugin-platform` | 実装能力 | 役割+参照型 | 新規 |
| G2 | `optimization-modeling` | 実装能力 | 役割+参照型 | 新規 |
| G3 | `event-driven-service` | 実装能力 | 役割+参照型 | 新規 |
| G4 | `simulation-harness` | 実装能力 | 役割+参照型 | 新規 |
| G5 | `web-frontend-dev` | 実装能力 | 役割+参照型 | 新規 |

**既存の再利用**: archimate-ea(①②)、web-api-dev / python-expert / cli-tool-dev /
tauri-dev(④)、data-analyst(予測・分析)、competitive-analysis(候補収集)、
project-manager / github-issues / commit-and-report(⑤)、code-reviewer / build。

## 4. 共通不変条件(全新規スキル)

1. **`ea-model.yaml` が唯一の真実。** モデルへの書き戻しは要素の `properties` のみ、
   直後に `validate_model.py` を通す。emit済みファイルは手編集しない。
2. **stable id が追跡のアンカー。** 既存 id(`req-*`, `appsvc-*`, `syssw-*`)を
   ADR・トレーサビリティ・タスクの参照キーに使う。新規 id は kebab-case。
3. **generate-forward + 対話。** バッチ生成せず、断片を提案→ユーザが赤ペン。
4. **司令塔は薄く。** `ea-delivery` は配線・状態・ゲートのみ。工程ロジックを持たない。
5. **description は役割で峻別。** トリガー衝突を避ける(司令塔=一気通貫、子=各工程)。
6. **規約準拠。** SKILL.md < 500行、超過分は `references/`、plugin.json +
   marketplace.json 登録(`docs/skill-authoring-best-practices.md`)。

---

## 4A. 鎖を閉じる3スキル

### P1 `tech-selector` — 非機能要求からミドルウェア選定 + ADR

- **役割**: Motivation層の Requirement/Constraint と Technology層の未選定要素
  (製品名が汎用の SystemSoftware/Node/TechnologyService)を入力に、重み付き評価で
  具体製品を選び、根拠(ADR)を残し、決定をモデルへ書き戻す。
- **入力**: 対象 = `type ∈ {SystemSoftware, Node, TechnologyService}` の要素 /
  適用要求 = それへ realize/serve/access で辿れる Requirement・Constraint。
- **成果物**:
  - `criteria.yaml`(評価軸・重み・要求とのマッピング, running artifact)
  - 評価マトリクス Markdown(候補×軸, 加重スコア, 感度分析)→ `out/tech-selection/`
  - ADR `docs/adr/NNNN-*.md`(MADR: 文脈/決定/根拠/棄却案/影響)
  - **書き戻し**: 対象要素の `properties` に `selected-product` / `decision-adr` /
    `evaluated-on`
- **スクリプト**: `score.py`(加重スコア+感度分析)/ `writeback.py`(properties
  マージ→再検証, ruamelでコメント保持)。候補収集は competitive-analysis へ委譲。
- **DoD**: 全未選定Tech要素が `selected-product` を持ち、各決定がADRに紐づき、
  各ADRが少なくとも1つの Requirement/Constraint にトレースする。

### P2 `archimate-to-impl` — 設計→実装トレーサビリティ橋渡し

- **役割**: Application層(+効くTechnology層)を実装タスク・API仕様・雛形へ写像し、
  `requirement → component → service → api → task` の機械可読な追跡を維持。
- **入力**: ApplicationComponent(実装単位)/ ApplicationService(API群)/
  ApplicationInterface(プロトコル境界)/ DataObject+Access(スキーマ・CRUD権限)/
  Realization・Serving(どの要求を満たすか)。
- **成果物**:
  - `traceability.yaml` + Markdown(全経路 + 孤立検出)
  - ApplicationService/Interface ごとの OpenAPI 3.0 skeleton → web-api-dev が肉付け
  - DataObject ごとのエンティティ雛形
  - component単位の実装タスク一覧(推奨スキル注記付き)→ github-issues / pm へ
- **スクリプト**: `derive.py`(走査して skeleton+追跡表を生成)/ `trace_check.py`
  (孤立検出バリデータ, text/json 出力は validate_model と同形式)。
- **DoD**: 全 Requirement が少なくとも1実装タスクへ trace、全 ApplicationService が
  API skeleton を持ち、孤立警告ゼロ。

### W `ea-delivery` — 全工程の薄い司令塔

- **役割**: 通しの `ea-model.yaml` を工程間で受け渡し、各工程を専門スキルへ委譲し、
  ハンドオフ前にゲートを通す。中身は持たない。
- **所有するもの**: 工程ステートマシン(要求→設計→P1→P2→開発→サービス化)/
  ゲート(各ハンドオフ前に validate、未選定Tech要素の残存チェック等)/
  後戻りエッジ管理(P2で判明した新非機能要求を P1 へ差し戻す)/
  delivery ledger(現工程・生成物の所在・開いている後戻り)。
- **委譲先**: archimate-ea → tech-selector → archimate-to-impl → web-api-dev 等 →
  project-manager / commit-and-report。
- **設計上の注意**: オーケストレーションは指示レベル(ソフト)。ゲート手順を
  チェックリストとして SKILL.md に明記して規律を担保。任意工程からのエントリを許可
  (ブラウンフィールド対応)。決定的自動実行が要るなら Workflow の領域(本計画では
  対象外)。
- **DoD**: サンプルモデルで、要求分析から実装タスク生成までを司令塔経由で
  一巡でき、各ゲートで検証が走り、後戻りが ledger に記録される。

---

## 4B. 実装能力5スキル(アーキタイプで顕在化)

### G1 `plugin-platform` — プラグイン基盤 + 隔離実行 ◎最優先

- **なぜ穴か**: 「アルゴリズムのマーケット」= 差別化点そのもの。既存・計画のどこにも
  無く、セキュリティ直結で設計が難しい(security-review はレビュー用で基盤構築は不可)。
- **カバー範囲**: 安定したプラグイン契約(SDK/インターフェース定義)、登録・版管理・
  発見のレジストリ、**準・未信頼コードの隔離実行**(サンドボックス、リソース制限、
  タイムアウト)、プラグインのライフサイクルとバージョニング。
- **EA連携**: P1 が「隔離実行ランタイムの選定」を、P2 が「プラグイン契約 =
  ApplicationInterface の SDK雛形化」を供給。
- **references案**: plugin-contract / sandboxing-strategies / registry-and-versioning。

### G2 `optimization-modeling` — 最適化/意思決定アルゴリズム ◎最優先

- **なぜ穴か**: 意思決定支援アルゴリズムの核は不確実性下の最適化。data-analyst は
  統計/可視化/ML であり、**数理最適化(LP/MILP/凸、ソルバ工学)はカバー外**。
- **カバー範囲**: 問題定式化(目的関数・制約)、ソルバ選定と利用(OSS/商用)、
  確率的/ロバスト最適化、解の検証と感度分析、性能とスケール。※ 対象領域固有の
  理論そのものはドメイン側。
- **references案**: problem-formulation / solver-selection / stochastic-and-robust。

### G3 `event-driven-service` — イベント駆動/非同期・リアルタイム ○

- **なぜ穴か**: 取引の同時到着・マッチングラウンド・通知は request/response REST に
  収まらない。web-api-dev は明示的に REST スコープ。
- **カバー範囲**: メッセージング(キュー/ストリーム)、非同期ワーカ、スケジュール
  ジョブ、WebSocket/SSE プッシュ、冪等性・順序保証・バックプレッシャ。
- **references案**: messaging-patterns / realtime-push / delivery-guarantees。

### G4 `simulation-harness` — シミュレーション/バックテスト ○

- **なぜ穴か**: アルゴリズムと取引コアの挙動評価には、合成データ・リプレイ・
  指標を持つシミュレータが要る。data-analyst で部分代替可だが専用化の価値あり。
- **カバー範囲**: シナリオ生成、離散イベント/時間ステップ実行、リプレイ、指標収集、
  再現性(seed管理)、A/B 比較。
- **references案**: scenario-design / metrics-and-reproducibility。

### G5 `web-frontend-dev` — Webフロントエンド実装 △

- **なぜ穴か**: 取引プラットフォームUI + アルゴリズム閲覧UI に本番 Web SPA 実装スキルが無い
  (frontend-design=指針、tauri-dev=デスクトップ、web-artifacts-builder=claude.ai用)。
  モック段階では後回し可のため優先度低。
- **カバー範囲**: SPA構成、状態管理、API連携、フォーム/テーブル、認証UI、
  アクセシビリティ。frontend-design(指針)を実装へ橋渡し。
- **references案**: spa-architecture / state-and-data-fetching。

---

## 5. 依存関係と実装順序

```
フェーズ1(鎖を閉じる):  P1 tech-selector → P2 archimate-to-impl → W ea-delivery
フェーズ2(駆動ケース中核): G2 optimization-modeling, G1 plugin-platform
フェーズ3(駆動ケース周辺): G3 event-driven-service, G4 simulation-harness
フェーズ4(UI, 任意):     G5 web-frontend-dev
```

- **P1** は依存なし・ツール型で検証しやすく、鎖の起点。最初に着手し計画の妥当性を最速確認。
- **P2** は P1 と独立に着手可(App層を読む)。**W** は P1/P2 完成後に薄く被せる。
- **G1〜G5** は鎖とも相互とも概ね独立。駆動ケースへの中心性で G2・G1 を優先。
- 各スキルは規約に従い、SKILL.md 骨格 → サンプルで一巡 → references 充実 の順で作る。

## 6. 各スキルの受け入れ条件(サマリ)

| スキル | 完了の目印 |
|--------|-----------|
| P1 | 全未選定Tech要素に製品確定、決定→ADR→要求のトレース成立 |
| P2 | 全要求が実装タスクへtrace、全ApplicationServiceにAPI skeleton、孤立ゼロ |
| W  | サンプルモデルで要求→実装タスクを司令塔経由で一巡、ゲート検証+後戻り記録 |
| G1 | プラグイン契約定義・レジストリ・隔離実行の3点をサンプルで実演 |
| G2 | 定式化→ソルバ選定→求解→感度分析をサンプル問題で一巡 |
| G3 | キュー/ワーカ/プッシュの最小構成が動くサンプル |
| G4 | seed固定で再現するシナリオ実行と指標収集 |
| G5 | API連携する最小SPAが動くサンプル |
