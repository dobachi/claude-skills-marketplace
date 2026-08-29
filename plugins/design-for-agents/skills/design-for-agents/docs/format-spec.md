# 書式仕様

`rules/` `playbooks/` `tokens/` `antipatterns/` に置くファイルの書式を定める。
**これが書式の正である。** CONCEPT.md 第4節は概観であり、細部はここに従う。

新しいファイルを追加する前に、第7節のチェックリストを通すこと。

---

## 1. 共通規則

| 規則 | 内容 |
|---|---|
| 1ファイル1判断 | rule は1枚に1つの判断だけを書く。2つ書きたくなったら2枚に割る |
| ID = ファイル名 | `rules/core-title-assertion.md` の ID は `core-title-assertion` |
| ID は変えない | 一度公開した ID は改名しない。廃止するときは `status: deprecated` と `superseded_by` を書き、ファイルは残す |
| frontmatter 必須 | YAML frontmatter が無いファイルは参照対象にしない |
| 本文は根拠 | frontmatter が機械可読な本体。本文は「なぜそうなのか」と例だけを書く |

## 2. ID 体系

```
<scope>-<topic>-<slug>
```

### scope

| scope | 意味 | 判定 |
|---|---|---|
| `core` | 媒体非依存 | 媒体を PowerPoint から web に変えても文言が成り立つなら `core` |
| `pptx` | PowerPoint 固有 | スライドマスター、プレースホルダ、SmartArt、アニメーション、16:9インチのグリッドなど、その媒体にしか存在しない概念に依存する |

v0.3 以降で `web` / `doc` を追加する。**迷ったら `core` にしない。**
媒体固有として書いておき、他媒体で同じ規則が要ると分かった時点で
`core` に引き上げる（引き上げは ID の変更なので、旧 ID を deprecated にして残す）。

### topic

`type` / `color` / `layout` / `ornament` / `density` / `emphasis` / `title` /
`structure` / `chart` / `table` / `diagram` / `image` / `a11y` / `master` /
`source` / `file`

この一覧にないトピックを使うときは、この節に追記してから使う。

### slug

英小文字とハイフンのみ。3語以内。否定形にしない
（`no-gradient` ではなく `ornament-none`）。

### 例

```
core-title-assertion        タイトルは主張文にする
core-density-one-message    1スライド1メッセージ
core-color-four-slots       色は4枠。5つ目を作らない
core-a11y-contrast-body     本文のコントラスト比 4.5:1 以上
core-chart-data-ink         データインク比を上げる
pptx-master-placeholder     内容はレイアウトのプレースホルダに書く
pptx-animation-none         アニメーションを使わない
```

## 3. rule の書式

```yaml
---
id: core-title-assertion
status: active                    # active | deprecated
tier: SHOULD                      # MUST | SHOULD | HOUSE
media: [pptx]                     # 適用が確認済みの媒体だけを書く
topic: title
statement: "スライドのタイトルは主張文にする（体言止めのトピック名にしない）"
values: []                        # 決め打ちの値。無ければ空配列
not_applicable_when: "目次、章扉、付録の見出し"
source:
  kind: consensus                 # normative | consensus | house
  key: alley-neeley-2005          # docs/sources.md のキー。URL はそこにしか書かない
  ref: "Alley & Neeley 2005"      # その場で読める短い出典表記
done_when:                        # 第5節。1つ以上必須
  - id: all-titles-assertive
    applies_to: slide
    predicate: count
    statement: "タイトルが体言止めのスライドが 0 枚である"
    check: manual
    floor: "本文スライドが3枚以上ある"
---
```

### 各フィールド

| フィールド | 必須 | 内容 |
|---|---|---|
| `id` | ○ | 第2節の体系に従う。ファイル名と一致 |
| `status` | ○ | `active` / `deprecated`。`deprecated` なら `superseded_by` も書く |
| `tier` | ○ | 第4節 |
| `media` | ○ | **適用が確認済みの媒体だけ**。「たぶん効く」は書かない |
| `topic` | ○ | 第2節の一覧から |
| `statement` | ○ | 1文。命令形。「〜する」「〜しない」 |
| `values` | ○ | 決め打ちの値。値が `tokens/` にあるならトークン名で指す。**範囲で書かない** |
| `not_applicable_when` | ○ | 適用しない条件。例外が無いなら `"なし"` と明記する（省略しない） |
| `source` | ○ | 第4節 |
| `done_when` | ○ | 第5節。**1つ以上必須。検証手段が無いルールは追加しない** |

### 禁止

- 「検討する」「適切に」「必要に応じて」「バランスを取る」を書かない。
  書きたくなったら、そのルールはまだ書ける状態にない
- 範囲（「18〜24pt」）を書かない。1つの値と、そこから外れてよい条件を書く

## 4. tier と出典

**`tier` と `source.kind` は1対1に対応する。** 別々に判断しない。

| tier | source.kind | 条件 | 上書き |
|---|---|---|---|
| `MUST` | `normative` | 公開された規範文書に、条番号の粒度で対応づけられる（例: WCAG 2.2 SC 1.4.3）。または逸脱すると読めない・使えない | 不可 |
| `SHOULD` | `consensus` | 独立した複数の出典が同じ方向を支持する。規範文書ではない（Tufte、CRAP、コンサルの慣行など） | 理由を書けば可 |
| `HOUSE` | `house` | 出典が無い。または正解が複数あるなかから本リポジトリが1つ選んだ | ユーザ指定・ブランドがあれば即上書き |

`key` は [`docs/sources.md`](sources.md) の登録キーを指す。**URL は台帳にしか書かない**
（同じ URL を30枚のルールに再掲すると必ず食い違う）。台帳に無い出典を使うときは、
先に台帳へ登録する。

`ref` には**何を根拠にしたかが特定できる粒度**で書く。「デザインの原則」のような
書き方はしない。`kind: house` のときは `ref` に「本リポジトリの決め」と書き、
**外部規範のふりをさせない**。

## 5. done_when の書式

**`done_when` はルールに置く。** ルールと検証は不可分であり、playbook 側に置くと
同じルールを使う playbook の数だけ複製されて必ず崩れるため。

playbook が持てるのは、**単一のルールに紐づかない条件だけ**である
（例: 論の筋が通っているか）。その場合に限り playbook に `done_when` を書き、
`rule:` フィールドは省く。

完了条件の完全な ID は `<rule-id>#<check-id>` である
（例: `core-title-assertion#all-titles-assertive`）。

**後から検出器に落とせる形でしか書かない。**

```yaml
done_when:
  - id: all-titles-assertive
    applies_to: slide              # deck | slide | element
    predicate: count               # 第5.1節の6つから1つ
    statement: "タイトルが体言止めのスライドが 0 枚である"
    check: manual                  # manual | automated
    detector: ""                   # automated のときコマンドを書く
    floor: "本文スライドが3枚以上ある"
```

### 5.1 predicate — この6つ以外を使わない

| predicate | 形 | 例 |
|---|---|---|
| `exists` | 対象が存在する | 「各データスライドに出典行が存在する」 |
| `absent` | 対象が存在しない | 「グラデーションを持つ図形が存在しない」 |
| `count` | 個数が N 以下 / 以上 | 「第1階層の箇条書きが6個以下である」 |
| `member` | 値が定められた集合に属する | 「全フォントサイズが型スケールの集合に属する」 |
| `ratio` | 比が閾値以上 | 「本文と背景のコントラスト比が 4.5 以上である」 |
| `equal` | 全対象で値が一致する | 「全スライドのタイトル上端が同じ値である」 |

**この6つに還元できない条件は `done_when` に書けない。** `needs_human` に回す。

### 5.2 statement の書き方

1. **状態を書く。手順を書かない。** 「タイトルを主張文にする」は手順であり
   完了条件ではない。「体言止めのタイトルが0枚である」が完了条件
2. **主語は数えられる対象**（スライド、タイトル、色、図形、フォントサイズ）
3. **評価語を使わない。** 「適切」「十分」「読みやすい」「バランスの良い」は
   検出器に落ちない
4. **数値は statement の中に書く。** 別の場所を見に行かせない

### 5.3 floor — 削除で満たすのを禁じる

`floor` は必須である。「違反0件」は対象を全部消せば達成できてしまうため、
**消すと成立しなくなる下限**を必ず添える。

- 悪い: `floor: ""`
- 良い: `floor: "本文スライドが3枚以上ある"`
- 良い: `floor: "各データスライドにグラフまたは表が1つ以上ある"`

### 5.4 check

検出器を実装したものから `automated` に変え、`detector` にコマンドを書く。
**このとき statement は書き換えない。** 書き換えが必要になったなら、それは
5.1〜5.3 に違反していた。

2026-08-29 に最初の13条件を昇格させた結果、**statement の書き換えは1件も
発生しなかった**。この書式の前提は成立している。昇格時に直したのは検出器側の
2点（`not_applicable_when` の未実装、自動図形が空のテキストフレームを持つこと
の見落とし）であり、条件の書き方ではなかった。

## 6. playbook の書式

```yaml
---
id: pptx-deck-decision
axis: deck                        # mode | deck | element | constraint
media: pptx
when:                             # 全て真なら該当。判定可能な条件だけ
  - "成果物が PowerPoint である"
  - "聞き手に決裁・承認・予算・採用可否を求める"
ambiguous_if: "説明が目的か決裁が目的か判別できない場合。推測せずユーザに聞く"
uses_rules: [core-title-assertion, core-density-one-message]
done_when: []                     # 単一ルールに紐づかない条件だけ。通常は空
needs_human:                      # テキストでは判定できない項目
  - "配色がブランドらしいか"
---
```

本文は次の順で書く。節を増やさない。

```
## 状況        この資料が置かれている状況を2〜3文
## 手順        順序付き。各段に「何を決めるか」を1つ
## 決め打ち値   この playbook 固有の値（共通値は tokens/ を指す）
## よくある失敗  具体名で。抽象的な戒めを書かない
```

検証すべき条件は `uses_rules` が指すルール側の `done_when` を集めれば得られる。
playbook に再掲しない（同じ内容を2か所に書かない）。

### axis

`INDEX.md` の軸と一致させる。

| axis | 選び方 |
|---|---|
| `mode` | 既存資料のとき、他より先に読む |
| `deck` | **必ず1つだけ**選ぶ |
| `element` | 置く要素の数だけ（0本以上） |
| `constraint` | 該当する分だけ（0本以上） |

## 7. token の書式

W3C DTCG の JSON 形式に準拠する。**独自形式を作らない。**

- `tokens/<media>.tokens.json` — 機械可読の正
- `tokens/<media>.md` — 人間可読の表。**値は JSON から転記するだけ**で、
  ここで新しい値を決めない

`$description` に、そのトークンが由来する rule の ID を書く。

## 8. antipattern の書式

```yaml
---
id: pptx-slop-decorative-band
media: pptx
statement: "タイトル背景の全幅カラーバンド"
why_it_appears: "生成のたびに座標が変わり、スライド間でずれる"
instead: "白地に ink のタイトル。区切りはヘアライン1本（core-color-four-slots）"
violates: [core-color-four-slots, pptx-master-placeholder]
---
```

**具体名で禁止する。** 「装飾を控える」ではなく「全幅カラーバンド」「グラデーション」
「ドロップシャドウ」「ベベル」「WordArt」「六角形」と名指しする。

## 9. 追加前チェックリスト

**この節は `scripts/lint.py` が機械的に確認する。**

```
python3 scripts/lint.py            # 0=違反なし / 1=違反あり / 2=検査できない
python3 scripts/lint.py --vocab    # 用語集の「使わない語」も照合（警告のみ）
```

検査器は下限を持つ。`rules/` を空にして「違反なし」にすることはできない
（対象が無ければ終了コード 2 になる）。

1つでも「いいえ」があるなら、そのファイルは追加しない。

- [ ] frontmatter の必須フィールドが全て埋まっているか
- [ ] `statement` に「検討」「適切」「必要に応じて」が無いか
- [ ] 値が範囲ではなく1つに決まっているか
- [ ] `tier` と `source.kind` が対応しているか
- [ ] `kind: house` のものが、外部規範のふりをしていないか
- [ ] `not_applicable_when` が埋まっているか（例外が無いなら「なし」と書いたか）
- [ ] rule に `done_when` が1つ以上あるか（検証手段の無いルールを足していないか）
- [ ] `source.key` が `docs/sources.md` に登録済みか
- [ ] `done_when` の全項目が第5.1節の6つの predicate に還元できるか
- [ ] `done_when` の全項目に `floor` があるか
- [ ] 目視でしか判定できないものを `done_when` に混ぜていないか
- [ ] 同じ内容を他のファイルに書いていないか
- [ ] 使った語が `glossary.md` にあるか（無いなら先に追加したか）
