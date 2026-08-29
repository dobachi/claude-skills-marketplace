# design-for-agents

人間向けに書かれたデザイン知を、**AIが迷わず引ける形**に組み直した参照体。

AIエージェントは資料やUIを日常的に生成するが、その出来を自分で見られない。
結果、(1) 作って検算できない、(2) 指示しなかった判断が学習データの最頻値
（紫グラデーション＋Inter＋3枚のカード、いわゆる AI slop）に落ちる、という
2つの失敗が起きる。

これは「デザイン原則集」ではない。
**判断が空欄にならないよう決め打ちされ、適用条件と完了条件が明示された、
ユースケース単位の手順書**である。

対象媒体は v0.1 では PowerPoint のみ。web / chart / 文書は v0.3 以降。

## 入口

| | |
|---|---|
| **AIが最初に読む入口** | [`skills/design-for-agents/INDEX.md`](skills/design-for-agents/INDEX.md) — ルーティング表。**これだけを常時読む** |
| 設計思想 | [`CONCEPT.md`](CONCEPT.md) |
| 書式仕様（ファイルを追加する前に読む） | [`docs/format-spec.md`](skills/design-for-agents/docs/format-spec.md) |
| 用語集 | [`glossary.md`](skills/design-for-agents/glossary.md) |
| 出典台帳 | [`docs/sources.md`](skills/design-for-agents/docs/sources.md) |

## 使い方

このプラグインをインストールすると、ルータスキル `design-for-agents` が有効になる。
スキル自体は判断を持たず、`INDEX.md` に渡すだけである。

```
/plugin install design-for-agents@dobachi-skills
```

スキルを介さず、AI に `skills/design-for-agents/INDEX.md` を直接読ませてもよい。
実行手順は INDEX の第0節にある。

```
媒体 → モード → ジャンル(1つだけ) → 要素(0本以上) → 制約(0本以上)
     → 決め打ち値と禁止事項 → done_when の確認 → 判定できない項目を返す
```

**リポジトリ全体を読み込ませない。** INDEX が指した行のファイルだけを開く。
上の経路で実際に開くのは 5 ファイル・約 20KB であり、収録物全体（約 150KB）の
7分の1で済む。

## 構成

```
skills/design-for-agents/
  SKILL.md          薄いルータ。判断を持たない
  INDEX.md          ルーティング表（常時読む唯一の入口）
  glossary.md       語彙の固定
  playbooks/        ユースケース別の手順書 8本（mode 1 / deck 3 / element 3 / constraint 1）
  rules/            原子ルール 39枚（MUST 3 / SHOULD 16 / HOUSE 20）
  tokens/           決め打ち値。W3C DTCG 形式
  antipatterns/     具体名で禁止された事項 10件
  docs/             書式仕様と出典台帳
  scripts/lint.py   書式検査
```

## 検査

**収録物の書式** を検査する（依存なし）。

```
python3 skills/design-for-agents/scripts/lint.py            # 0=違反なし / 1=違反あり / 2=検査できない
python3 skills/design-for-agents/scripts/lint.py --vocab    # 用語集の「使わない語」も照合（警告のみ）
```

**実物の .pptx** を、rules の完了条件に照らして検査する（python-pptx が要る）。

```
pip install -r skills/design-for-agents/assets/requirements.txt
python3 skills/design-for-agents/scripts/check_deck.py deck.pptx [--json]
```

検査の id は `<rule-id>#<check-id>` で、rules の `done_when` と1対1に対応する。
閾値は `tokens/pptx.tokens.json` から読むので、値は検出器に書かれていない。
61条件のうち **13 が `check: automated`**（実物で発火を確認済み）、残りは `manual`。

標準ライブラリのみ。必須フィールド、ID の体系、`tier` と出典種別の対応、
`done_when` の述語と下限、範囲表記の混入、参照先ルールの実在などを確認する。
**検査器自身が下限を持ち**、対象を消して「違反なし」にはできない（終了コード 2）。

## 出自

本プラグインは、かつて同じマーケットプレイスにあった `pptx-design` の
`references/`（1212行）を抽出・再構造化したものである。取り込みを終えた時点で
`pptx-design` は廃止した（2026-08-29）。抽出にあたって加えた主な変更。

- 各規則に出典と権威の階層（MUST / SHOULD / HOUSE）を付け、外部の規範と
  本プラグインの決めを区別した。元は大半が出典なしの断定だった
- 一次情報を4件補った（Alley & Neeley 2005、Cleveland & McGill 1984、
  Okabe & Ito、JIS X 8341-3:2016）。詳細は
  [`docs/sources.md`](skills/design-for-agents/docs/sources.md)
- 元にあった矛盾を1件解決した（円グラフの区分上限が 6 と 3 で食い違っていた）
- 完了条件を検出器互換の書式で書き直し、削除で満たせないよう下限を添えた

実際の `.pptx` の生成・抽出は `pptx-build` が行う。本プラグインは仕様と
完了条件のみを供給する。

## ライセンス

リポジトリ全体の方針に従う。文書は CC BY 4.0（[`LICENSE-docs`](../../LICENSE-docs)）、
コードは Apache License 2.0（[`LICENSE`](../../LICENSE)）。

引用・参照している外部の規範や著作物の権利は、それぞれの権利者に帰属する。
出典は [`docs/sources.md`](skills/design-for-agents/docs/sources.md) にある。
