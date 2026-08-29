---
id: core-density-budget
status: active
tier: HOUSE
media: [pptx]
topic: density
statement: "1スライドに載せる量の上限を定め、超えたらスライドを割る"
values:
  - "箇条書き: 第1階層 6個まで、階層は2まで、1項目1行（最大2行）"
  - "2段組: 1段あたり4項目まで"
  - "表: 6列 × 8行まで。超えるものは付録に置く"
  - "グラフ: 4系列まで。円グラフは3区分まで（core-chart-pie-limit）"
  - "図: 1スライドに1つ"
  - "余白: スライドのおよそ1/4を空ける"
not_applicable_when: "付録。ただし付録であることをスライド上で明示する"
source:
  kind: house
  key: house
  ref: "本リポジトリの決め"
done_when:
  - id: bullets-within-budget
    applies_to: slide
    predicate: count
    statement: "第1階層の箇条書きが7個以上あるスライドが 0 枚である（付録を除く）"
    check: automated
    detector: "scripts/check_deck.py <deck.pptx>"
    floor: "本文スライドが3枚以上あり、各スライドの本文が1行以上ある"
  - id: nesting-depth
    applies_to: slide
    predicate: count
    statement: "箇条書きの階層が3以上あるスライドが 0 枚である"
    check: automated
    detector: "scripts/check_deck.py <deck.pptx>"
    floor: "本文スライドが3枚以上あり、各スライドの本文が1行以上ある"
  - id: table-within-budget
    applies_to: element
    predicate: count
    statement: "7列以上または9行以上の表が 0 個である（付録を除く）"
    check: automated
    detector: "scripts/check_deck.py <deck.pptx>"
    floor: "表を含むスライドがある場合に限り評価する。列や行を削って満たしてはならない"
---

# 密度予算

## なぜこれが HOUSE なのか

**6 や 4 という数に外部の根拠は無い。**「7±2」を根拠に引いてはならない
（`docs/sources.md` の「引いてはいけないもの」）。作業記憶に限界があるという
方向は Sweller / Mayer が支持するが、そこからスライドの箇条書き数は導けない。

決めておく効用は、**超過が「割る」という判断の引き金になる**ことである。
上限が無いと、載らない量は文字を縮めることで吸収されてしまう
（`core-type-body-floor`）。

## 超過したときの順序

1. 消せる要素を消す（情報テスト）
2. スライドを割る
3. 付録に移す

**文字を縮める、行間を詰める、余白を削る — いずれも選択肢に無い。**

## 余白について

余白は「空いている」のではなく「空けている」。何も空いていないスライドは、
載っているどれかが役割を持っていない。
