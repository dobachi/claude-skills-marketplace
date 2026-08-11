# ベンダーのループ機構 — 台帳

**測定日: 2026-08-09**

**腐る情報。** 使う前に再測定すること。前回から1日で3行動いた実績がある。
期限は `detectors/matrix_freshness.py` が見る（既定14日）。

```bash
python3 detectors/matrix_freshness.py references/vendor-matrix.md
```

## 台帳

機能の細目は持たない。**腐るのは版と有無だけ**で、結論は年単位で変わらないためである。

| ツール | 版 | ループ機構 |
|---|---|---|
| Claude Code | 2.1.223 | **あり**（`/goal`・`/loop`・`/schedule`） |
| Codex CLI | 0.92.0 | 無し |
| gemini CLI | 0.1.21 | 無し |
| agy (Antigravity) | 未インストール | — |

## 結論 — これは年単位で変わりにくい

`/goal` 相当を持つのは Claude Code だけで、他は呼び出し側がループを書く。
したがって**移植可能な資産はループではなく、検出器の終了コード**である。

```bash
# Claude Code: ツールがループを持つ
/goal ./gate.sh report.md が通るまで直して、5回で諦めて

# Codex / gemini: 呼び出し側がループを持つ
for i in $(seq 5); do
  ./gate.sh report.md && break
  codex exec "NG を直して"          # あるいは gemini -p "..." --approval-mode auto_edit
done
```

ベンダーごとの抽象化レイヤは作らない。定義も責任範囲も違うため、抽象化すると嘘になる
（HANDOVER §2.1）。**この台帳は抽象化しないと決めた根拠**であって、実装の設計図ではない。

## 測り方

```bash
for c in claude codex agy gemini; do $c --version; done
codex --help; gemini --help          # ループ関連のサブコマンド・フラグの有無
```

`--help` に出ないことは「無い」の証明ではない。言えるのは
**「この版の `--help` と機能フラグの範囲では見つからない」**まで。

### 組み込みコマンドは非対話では確かめられない（腐らない教訓）

`/goal` の存在確認で空振りした調べ方を残す。2026-08-09 の実測。

| 見たもの | 結果 | 評価 |
|---|---|---|
| セッションのスキル一覧 | `loop`・`schedule` はあるが `goal` は無い | **誤誘導。** 組み込みコマンドは一覧に出ない |
| バイナリ内の文字列 | `"goal"` が5回。既知の `"schedule"` も5回で同形 | 示唆止まり。証拠として弱い |
| `claude -p "/help"` | `/help isn't available in this environment.` | 非対話では列挙できない |
| **利用者に打ってもらう** | **存在を確認** | 1往復で決着 |

**対話でしか観測できないものを、非対話の手段だけで判定しない。**
スキル一覧に無いことを「無い」の根拠にすると外す。
