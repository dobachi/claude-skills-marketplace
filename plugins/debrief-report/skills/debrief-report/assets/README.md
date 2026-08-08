# Assets — どれを使うか

Step 0 で決めたプロファイルに対応する一式をコピーして埋める。**2つのプロファイルを混ぜない**。

| プロファイル | 報告書 Markdown | デッキ spec | 入力インベントリ |
|---|---|---|---|
| A. 国際学会 | `profiles/academic-conference/report-template.md` | `profiles/academic-conference/deck.yaml` | `input-inventory.md` |
| B. 商業カンファレンス・展示会 | `profiles/commercial-conference/report-template.md` | `profiles/commercial-conference/deck.yaml` | `input-inventory.md` |
| C. 標準化会合・委員会 | `report-template.md` ＋ `references/event-profiles.md` §C の追加節 | `deck.debrief-report.yaml` | `input-inventory.md` |
| D. 商談・顧客訪問 | `report-template.md` ＋ §D の追加節 | `deck.debrief-report.yaml` | `input-inventory.md` |
| E. 社内会議・討議 | `report-template.md` ＋ §E の追加節 | `deck.debrief-report.yaml` | `input-inventory.md` |

C〜D〜E に専用テンプレートを置いていないのは、基本テンプレートとの差分が数節にとどまり、
5系統を並行保守すると必ず内容がずれるため。差分は `references/event-profiles.md` にある。

デッキ spec は `pptx-build` のフォーマット。生成前に必ず lint する:

```bash
cd <pptx-build>/skills/pptx-build/assets
python3 validate_deck.py <このディレクトリ>/profiles/academic-conference/deck.yaml
python3 build_deck.py    <同上> -o debrief.pptx        # 会社テンプレなら --template corp.pptx
./render_preview.sh debrief.pptx                        # Gate 3 でPNGを確認
```
