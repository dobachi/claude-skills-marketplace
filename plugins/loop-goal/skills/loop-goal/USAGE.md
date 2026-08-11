# loop-goal 使い方

`SKILL.md` が「何をどう考えるか」で、こちらは**手を動かす順番**。
コマンドはこのディレクトリを基準に、そのまま貼れる形で書いてある。

コマンドは**このスキルのディレクトリ**を基準に書いてある。
プラグインとして導入した場合は `~/.claude/plugins/*/skills/loop-goal/` 配下にある。

---

## 0. インストール（初回だけ）

スキルとして呼びたい場合。研究ディレクトリのまま使うなら飛ばしてよい。

```bash
SRC=<このスキルのディレクトリ>
cp -r "$SRC" ~/.claude/skills/loop-goal        # 全プロジェクトから使う
# cp -r "$SRC" .claude/skills/loop-goal        # そのプロジェクトだけ
```

`fixtures/` はテスト用なので、配布時は落としてよい（残しても害は無い）。

`python3` があれば動く。追加インストールは無い。

---

## 1. まず走らせてみる

検出器は単体で動く。文書を1つ渡すだけ。

```bash
cd <このスキルのディレクトリ>
python3 detectors/refs_integrity.py detectors/fixtures/report_v3_fixed.md
echo "exit=$?"        # 0=OK / 1=NG / 2=引数エラー
```

出力の最後に必ず「**保証しないこと**」が出る。ここが**この検査で見ていない範囲**である。
判定 OK は「この観点では問題が無い」であって「文書が正しい」ではない。

引数なしで実行すると使い方が出る。

```bash
python3 detectors/citation_presence.py
```

---

## 1.5 ゲートを組む前に噛み合いを見る

**検出器が文書に噛んでいなければ、緑は「何も検査していない緑」になる。**

```bash
python3 detectors/applicability_report.py 対象.md
```

判定はしない（exit は 0 か 2 のみ）。`⚠️` が付いたマーカーに依存する検出器は空振りするので、
`ROW` / `REF` などの正規表現を文書に合わせるか、その検出器をゲートから外す。

---

## 2. ゲートを組む — 1本で回さない

**1本だけを停止条件にすると、通った瞬間に別の1本が落ちる。** 実測で起きている。
`gate.sh` はそれを避けるための例。

```bash
BASE=detectors/fixtures/report_v2_uncited.md \
  ./gate.sh detectors/fixtures/report_v4_sourced.md
echo "exit=$?"
```

`BASE`（編集前のファイル）を渡すと単調性の下限が入る。**渡さないと警告して落ちる**。
他の検出器はどれも「消せば満たせる」ため、下限が無いゲートは意味を持たない。

自分の文書で使うときは `gate.sh` の中の検出器の並びを書き換える。編集点はファイル冒頭。

---

## 3. ループを回す

### Claude Code（ツールがループを持つ）

```bash
cp 対象.md /tmp/base.md          # 単調性の基準を先に取る
```

対話セッションで:

```
/goal BASE=/tmp/base.md ./gate.sh 対象.md が通るまで直して、5回で諦めて
```

**回数の上限を必ず付ける。** 付けないと止まらない。

### Codex / gemini（呼び出し側がループを持つ）

```bash
cp 対象.md /tmp/base.md
for i in $(seq 5); do
  BASE=/tmp/base.md ./gate.sh 対象.md && break
  codex exec "gate の NG を直して"        # gemini -p "..." --approval-mode auto_edit でも同じ
done
```

ベンダーごとの現況は [`references/vendor-matrix.md`](references/vendor-matrix.md)。
**測定日を見ること。1日で3行動いた実績がある。**

### 検出器を書き込み範囲の外に置く

同じディレクトリに置いたままだと、最短経路が「検出器を書き換える」になりうる。
最低限これだけはやる。

```bash
mkdir -p /tmp/gate && cp -r detectors /tmp/gate/ && chmod -R 444 /tmp/gate/detectors/*.py
```

より強くするなら subagent の `tools` で書き込み範囲を絞るか、別ベンダーに委譲する。

---

## 4. 自分の文書に合わせる

検出器は**書き換えて使う**前提。設定ファイルは無く、**冒頭の定数だけが編集点**。

| 変えたいこと | 触る場所 |
|---|---|
| 出典IDの書式（`S-01` 以外） | 各ファイルの `ROW` / `REF` |
| 引用の書式（`「」` 以外） | `declared_counts.py` の `SPAN`、`no_regression.py` の `SPAN` |
| 禁止する語 | `forbidden_phrases.py` の `FORBIDDEN` |
| 出典の偏りの上限 | `distribution.py` の `MAX_TOP_SHARE` など |
| 見逃してよい候補の数 | `citation_presence.py` の `ALLOWED` |
| 前提が無いときの向き | 各ファイルの `REQUIRE_APPLICABLE`（既定 True＝落とす） |
| 対象外にする節 | `citation_presence.py` の `SKIP_SECTIONS` |
| 生成物の検査対象 | `build_artifacts.py` の `OUT_DIR` / `REQUIRED` / `EXPECT` |

**閾値を緩めた範囲は「見ていない範囲」として残る。** 緩める理由は書き残すこと。

### 動くことの確かめ方

`NG が出ないこと` だけを見ても、検出器が壊れていれば気づけない。**欠陥を注入して NG が出るか**と、
**前提を持たない文書で落ちるか**まで見る。期待値の表は実行できる形にしてある。

```bash
./detectors/test_detectors.sh     # 0=全件一致 / 1=食い違いあり
```

個別に見るなら、欠陥注入版と前提なし版が fixtures に固定してある。

```bash
python3 detectors/refs_integrity.py detectors/fixtures/report_v3_broken_ref.md
echo "exit=$?"    # 1（未定義 S-99 を検出）
python3 detectors/refs_integrity.py detectors/fixtures/no_markers.md
echo "exit=$?"    # 1（出典記法を持たない＝測定できない）
```

`echo $?` はパイプの最後のコマンドの結果になる。`| head` などを挟むと**終了コードが取れない**。

---

## 5. 検出器を足す

[`detectors/_template.py`](detectors/_template.py) をコピーする。そのままでも動くので、
動く状態から削るのが早い。

**足す前に種類を決める。規則の掛かり方が変わる。**

| `KIND` | 中身 | 実例が要るか |
|---|---|---|
| `"spec"` | 仕様から書ける。対応関係・数の一致・存在確認 | 不要。先に書いてよい |
| `"example"` | ヒューリスティック・除外リスト・閾値 | **必須。** 実際に取り逃した欠陥からのみ |

`example` を先回りして書いても、使われないか、起きたときには形が違う。
`ORIGIN`（由来の1行）が空のまま `KIND="example"` で回すと exit 2 で落ちる。

作法（[`detectors/README.md`](detectors/README.md) に同じものがある）:

- 1ファイル1目的
- 標準ライブラリのみ
- 30〜120行。超えたら分割の合図
- 設定ファイルを持たない。定数は冒頭にベタ書き
- 出力に「保証しないこと」を含める
- 終了コードで判定できる（0=OK / 1=NG / 2=引数エラー）

共通処理は切り出さない。1ファイル単独でコピーして書き換えられることが依存なしの実体で、
共通モジュールを作った時点で成立しなくなる。正規表現の重複は許容する。

足したら `detectors/test_detectors.sh` の `CASES` に期待値を1行足す。
入れないと、その検出器は回帰の対象外になる。

---

## 6. 通ったあとにやること

**通ったことは、欠陥が無かったことを意味しない。**

1. 各検出器の「保証しないこと」を読む。そこが見ていない範囲
2. 差分を見る。**満たし方が「消す」でなかったか**。`no_regression.py` は数しか見ない
3. 主観（論旨の妥当性、読みやすさ）は別コンテキストへ出す。`doc-review` など

実測例: 検出器の隣接判定の都合で発火した箇所が、**文書側の整形で解消**されたことがある。
判定は OK になったが、欠陥は直っていない。

---

## 7. うまくいかないとき

| 事象 | 原因と対処 |
|---|---|
| 全部 OK なのに文書がおかしい | 検出器が見ている範囲の外。「保証しないこと」を読む。必要なら検出器を足す |
| 候補が多すぎて使えない | `citation_presence.py` の `SKIP_SECTIONS` に、事実を報告しない節（方法論・書式説明）を足す |
| `ALLOWED` を上げるか迷う | 上げてよい。ただし**上げた数だけ人が確認済みであること**が前提 |
| ループが止まらない | 回数上限を渡していない。`/goal` なら「N回で諦めて」を必ず書く |
| ループが検出器を書き換えた | 検出器がループの書き込み範囲内にある。手順3の `chmod 444` をやる |
| 「測定できない」で落ちる | 検出器の書式が文書と噛んでいない。手順4 で `ROW` / `REF` を合わせる。合わせずに `REQUIRE_APPLICABLE=False` にすると、**何も検査していない状態で緑になる** |
| 終了コードが常に0 | `| head` などを挟んでいる。`echo $?` はパイプ最後のコマンドの結果 |
| `make check` が通るのに壊れている | それが `build_artifacts.py` を書いた理由。終了コードではなく生成物を見る |
