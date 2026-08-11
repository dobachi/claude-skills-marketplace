# evals — SKILL.md の指示そのものを測る

`tests/run_tests.sh` は `drift_scan.py` が正しく動くかを測る。ここは別のことを測る —
**SKILL.md の指示が、狙った振る舞いを実際に引き出すか**。

形式は Agent Skills の公式規約に従う（`evals/evals.json`、`skill_name` + `evals[]`）。
仕様と運用手順: <https://agentskills.io/skill-creation/evaluating-skills>

## 走らせ方

公式に組み込みの実行系は無い。

> There is not currently a built-in way to run these evaluations. Users can create
> their own evaluation system. Evaluations are your source of truth for measuring
> Skill effectiveness.
> — Anthropic, *Skill authoring best practices*

`skill-creator` プラグインがこのループを自動化する。手で回すなら:

1. 各ケースを**2回**走らせる — スキール有り (`with_skill/`) と無し (`without_skill/`)。
   **差分が結果**であって、有りの合格率そのものではない。
2. 各実行は**クリーンな文脈**から。Claude Code なら subagent、無ければ別セッション。
3. `assertions` を出力に照らして PASS/FAIL を付け、**出力を引用した根拠**を添える
   （`grading.json`）。意見ではなく引用。
4. 集計して `benchmark.json`（pass_rate / time / tokens と delta）。
5. 作業ディレクトリはスキル外に置く: `longform-discipline-workspace/iteration-N/`。

## このファイルを直すとき

- **両方の構成で必ず通る assertion は消す。** スキルが無くてもモデルができることを
  測っており、有りの合格率を水増しするだけ。
- **両方で必ず落ちる assertion は疑う。** assertion が壊れているか、ケースが難しすぎるか、
  見ているものが違う。
- **有りで通り無しで落ちる assertion に注目する。** そこがスキルの価値なので、
  なぜ効いたのかを特定する。
- 実行ごとに結果がぶれるなら、フィクスチャではなく**指示が曖昧**な可能性がある。

## 3ケースの意図

| id | 何を測るか | 落ちたら疑うもの |
|---|---|---|
| 1 | 規律1・2・8 — スパインを先に作り、いきなり書き始めない | 「When it applies」と規律の並び順・強さ |
| 2 | 規律6・7 — スキャナをゲートにし、番号付きリストを出す | `content-review.md` の「レビューリストの作り方」 |
| 3 | Anti-patterns 表の1行目 — 全文を貼っての一括修正を断れるか | Anti-patterns の位置づけ（表は読まれているか） |

ケース3が一番重要である。ユーザーの言うとおりに従うことが**失敗**になる唯一のケースで、
スキルが単なる助言集ではなく制約として働いているかを分ける。

## トリガ精度の計測

`evals/trigger-eval.json` は「発火すべき」7件と「発火すべきでない」9件。近傍スキル
（doc-review / ai-tell-reducer / faithful-translation / essence-distiller）の領分を
厚めに入れてある。誤爆1回のコストは約10.9k トークンなので、過剰発火の方が高くつく。

**公式の `skill-creator/scripts/run_eval.py` はこの環境では動かない。** 検出が

```python
if tool_name in ("Skill", "Read"): ...
else: return False        # 最初のツール呼び出しがそれ以外なら即「未発火」
```

となっており、CLAUDE.md が KB 確認を命じている環境では最初の呼び出しが `Bash` に
なるため、**全クエリが 0% になる**。しかも「発火すべきでない」側も 0% で合格するので、
両方向とも合格に見えて情報がゼロになる。実測 9/16 は全部この人工物だった。

`measure_trigger.py` はストリーム全体を走査し、実際に導入済みのスキルを測る:

```bash
python3 evals/measure_trigger.py evals/trigger-eval.json
```

6件のサンプルで 5/6。落ちた1件は「5万字くらいの提案書を…」で、別の実行では発火した
ため**ばらつきの範囲**。n=1 では判定できないので、判断するなら runs-per-query を上げる。

## 保証しないこと

- **確率的である。** 1回の結果で判断しない。ぶれるなら複数回。
- **今日のこのモデルを測っている。** モデルが変われば、スキル無変更でも結果は変わる。
- **助言の良し悪しは測れない。** 約束した形の出力が出るかまで。中身の妥当性は人が読む。
