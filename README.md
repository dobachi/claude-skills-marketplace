# design-for-agents

人間向けに書かれたデザイン知を、**AIが迷わず引ける形**に組み直した参照体。

AIエージェントは資料やUIを日常的に生成するが、その出来を自分で見られない。
結果、(1) 作って検算できない、(2) 指示しなかった判断が学習データの最頻値
（紫グラデーション＋Inter＋3枚のカード、いわゆる AI slop）に落ちる、という
2つの失敗が起きる。

このリポジトリは「デザイン原則集」ではない。
**判断が空欄にならないよう決め打ちされ、適用条件と完了条件が明示された、
ユースケース単位の手順書**である。

- **AIが最初に読む入口**: [INDEX.md](INDEX.md)（ルーティング表。これだけを常時読む）
- 設計思想: [CONCEPT.md](CONCEPT.md)
- 書式仕様（ファイルを追加する前に読む）: [docs/format-spec.md](docs/format-spec.md)
- 用語集: [glossary.md](glossary.md)
- 出典台帳: [docs/sources.md](docs/sources.md)

## 検査

```
python3 tools/lint.py
```

書式仕様のチェックリストを機械的に確認する。標準ライブラリのみ。
終了コードは 0=違反なし / 1=違反あり / 2=検査できない。
- 現在の状態: v0.1 策定中（対象媒体: PowerPoint）。
  `INDEX.md` が指す先はまだ大半が未作成であり、状態列に明示している

## 使い方

### スキルとして使う

このリポジトリは [Agent Skills](https://agentskills.io) 形式のルータスキルを
同梱している（`skills/design-for-agents/SKILL.md`）。スキルは判断を持たず、
`INDEX.md` に渡すだけである。

```
git clone https://github.com/dobachi/design-for-agents.git
```

Claude Code から使う場合は、クローンしたディレクトリをプラグインとして
登録する（`.claude-plugin/plugin.json` を同梱済み）。

### 直接引く

スキルを介さず、AI に `INDEX.md` を読ませてもよい。実行手順は INDEX の第0節にある。

```
媒体 → モード → ジャンル(1つだけ) → 要素(0本以上) → 制約(0本以上)
     → 決め打ち値と禁止事項 → done_when の確認 → 判定できない項目を返す
```

**リポジトリ全体を読み込ませない。** INDEX が指した行のファイルだけを開く。

### 書式を検査する

```
python3 tools/lint.py            # 0=違反なし / 1=違反あり / 2=検査できない
python3 tools/lint.py --vocab    # 用語集の「使わない語」も照合（警告のみ）
```

## pptx-design との関係

本リポジトリは [dobachi/claude-skills-marketplace](https://github.com/dobachi/claude-skills-marketplace)
の `pptx-design` スキルの `references/` を抽出・再構造化したものであり、
**そちらの上流にあたる**。抽出にあたって加えた主な変更は次のとおり。

- 各規則に出典と権威の階層（MUST / SHOULD / HOUSE）を付け、
  外部の規範と本リポジトリの決めを区別した。元は大半が出典なしの断定だった
- 一次情報を4件補った（Alley & Neeley 2005、Cleveland & McGill 1984、
  Okabe & Ito、JIS X 8341-3:2016）。詳細は [docs/sources.md](docs/sources.md)
- 元にあった矛盾を1件解決した（円グラフの区分上限が 6 と 3 で食い違っていた）
- 完了条件を検出器互換の書式で書き直し、削除で満たせないよう下限を添えた

## ライセンス

| 対象 | ライセンス |
|---|---|
| 文書（`rules/` `playbooks/` `antipatterns/` `tokens/` `docs/` ほか `.md`） | [CC BY 4.0](LICENSE-docs) |
| コード（`tools/`） | [Apache License 2.0](LICENSE) |

文書中で引用・参照している外部の規範や著作物の権利は、それぞれの権利者に帰属する。
