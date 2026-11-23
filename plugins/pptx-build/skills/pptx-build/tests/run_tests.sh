#!/bin/bash
# extract_deck.py（既存 .pptx → spec の抽出）と roundtrip_check.py が生きているかを
# 確かめる。
#
# 「抽出できた」だけを見ても意味がない。抽出器が静かに内容を落としていても、
# 出力は「きれいな spec」に見えるからだ。だから3方向を見る:
#
#   1. 正常系: build_deck.py が作ったデッキを抽出し、型・タイトル・全テキストが
#      戻ることを roundtrip_check.py で照合する            (期待 0)
#   2. 欠陥注入: (a) spec を1行書き換えた版で比較器が差を検出するか (期待 1)
#                (b) 手書き相当の乱雑なデッキで LOSS を報告するか   (期待 1)
#   3. 前提なし: .pptx でないファイル / 存在しないファイル         (期待 2)
#
# さらに連結テスト: 乱雑なデッキ → 抽出 → 再ビルド → audit_pptx.py が
# エラー0 になること（リファクタリングの成立条件そのもの）。
#
# 使い方:   ./run_tests.sh
# 終了コード: 0=全件一致 / 1=食い違いあり
set -u
cd "$(dirname "$0")" || exit 2
A="../assets"
f="fixtures"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# 依存が無い環境（CI の素の runner、python-pptx 未インストールの手元）では、
# 全ケースが ModuleNotFoundError で落ちて「スキルが壊れている」ように見える。
# それは嘘なので、検査を実行できないことを明示して抜ける。CI は
# assets/requirements.txt を入れてから呼ぶので、ここは通らない。
if ! python3 -c "import pptx, yaml" >/dev/null 2>&1; then
  echo "SKIP  python-pptx / PyYAML が無いため、このハーネスは何も検査していない"
  echo "      入れるには: pip install -r ../assets/requirements.txt"
  exit 0
fi

# ─────────── 編集点: 検査を足したら、両方向の行を足す ───────────
# 書式1: 期待exit|コマンド行        0=指摘なし / 1=指摘あり / 2=前提エラー
# 書式2: has:<文字列>|コマンド行    その文字列が出力に現れること
# 書式3: lacks:<文字列>|コマンド行  その文字列が出力に現れないこと（誤検出の対照）
CASES=(
  # ---- 正常系: 自前の出力は無損失で戻る ----
  "0|python3 $A/extract_deck.py $f/clean-deck.pptx -o $TMP/clean.yaml"
  "0|python3 roundtrip_check.py $f/clean-deck.yaml $f/clean-deck.pptx"

  # ---- 正常系: 構図の型（statement/cards/steps/matrix/split）が型として戻る ----
  "0|python3 $A/extract_deck.py $f/archetype-deck.pptx -o $TMP/arch.yaml"
  "0|python3 roundtrip_check.py $f/archetype-deck.yaml $f/archetype-deck.pptx"
  "0|python3 $A/validate_deck.py $f/archetype-deck.yaml"
  "0|python3 $A/audit_pptx.py $f/archetype-deck.pptx --quiet"

  # ---- 正常系: いま生成したデッキでも成り立つか ----
  # 固定フィクスチャだけを見ていると、build_deck.py 側の退行（パーツの命名を
  # 失う等）に気づけない。その場でビルドして、監査と往復の両方にかける。
  "0|python3 $A/build_deck.py $f/archetype-deck.yaml -o $TMP/fresh.pptx"
  "0|python3 $A/audit_pptx.py $TMP/fresh.pptx --quiet"
  "0|python3 roundtrip_check.py $f/archetype-deck.yaml $TMP/fresh.pptx"

  # ---- 同梱テーマ: どの見た目でも構図と監査が壊れないか ----
  # テーマは色・書体・造形の値しか変えない。値を変えたら監査が落ちる、という
  # 状態になっていないことを、明暗の両方で確かめる。
  "0|python3 $A/build_deck.py $f/archetype-deck.yaml -o $TMP/t1.pptx --theme $A/themes/editorial.json"
  "0|python3 $A/audit_pptx.py $TMP/t1.pptx --quiet"
  "0|python3 $A/build_deck.py $f/archetype-deck.yaml -o $TMP/t2.pptx --theme $A/themes/warm.json"
  "0|python3 $A/audit_pptx.py $TMP/t2.pptx --quiet"
  "0|python3 $A/build_deck.py $f/archetype-deck.yaml -o $TMP/t3.pptx --theme $A/themes/slate-dark.json"
  "0|python3 $A/audit_pptx.py $TMP/t3.pptx --quiet"

  # ---- テンプレート流し込み: 出典・章の名前・章番号が名前つきプレースホルダに入るか ----
  # 置き場のあるテンプレートでは全部プレースホルダに入り、置き去りのテキストボックスが
  # 出ない (0)。置き場のないテンプレートでは、出典を黙って落とさず警告する (1)。
  "0|python3 template_annot_check.py"
  "1|python3 template_annot_check.py --no-source"
  "has:期待どおり 1 を返す|python3 template_annot_check.py --no-source"

  # ---- panels: 2列の文章と編集できる図を1枚に組む ----
  # 4種の図（stacked_bar / staircase / flow / chips）と下段のまとめを含む版を
  # その場でビルドし、監査を通す (0)。描けない図の種類は検証で止める (1)。
  "0|python3 $A/validate_deck.py $f/panels-deck.yaml"
  "0|python3 $A/build_deck.py $f/panels-deck.yaml -o $TMP/panels.pptx"
  "0|python3 $A/audit_pptx.py $TMP/panels.pptx --quiet"
  "1|python3 $A/validate_deck.py $f/bad-panels.yaml"
  "has:panels figure kind 'pie'|python3 $A/validate_deck.py $f/bad-panels.yaml"

  # ---- 編集できる図: figure 型 / split の figure: / diagram 種 ----
  # 描いた図は画像ではなく素の部品で置く。生成・監査を通し (0)、描いた図を
  # 画像で貼る宣言（image_kind: drawing）、未知の種類、宙に浮いた矢印、
  # 図も画像もない split を検証で止める (1)。抽出器は素の図を黙って箇条書きに
  # せず、読み戻せないと報告する (1)。
  "0|python3 $A/validate_deck.py $f/figure-deck.yaml"
  "0|python3 $A/build_deck.py $f/figure-deck.yaml -o $TMP/figure.pptx"
  "0|python3 $A/audit_pptx.py $TMP/figure.pptx --quiet"
  "1|python3 $A/validate_deck.py $f/bad-figure.yaml"
  "has:image_kind: drawing|python3 $A/validate_deck.py $f/bad-figure.yaml"
  "has:edge names unknown node 'zz'|python3 $A/validate_deck.py $f/bad-figure.yaml"
  "has:looks like a drawing, not a photograph|python3 $A/validate_deck.py $f/bad-figure.yaml"
  "has:it needs \`figure:\`|python3 $A/validate_deck.py $f/bad-figure.yaml"
  "1|python3 $A/extract_deck.py $TMP/figure.pptx -o $TMP/figure-back.yaml"
  "has:native figure parts|python3 $A/extract_deck.py $TMP/figure.pptx -o $TMP/figure-back2.yaml"

  # ---- 図の語彙（2.15）: cycle / matrix / bands / stack / legend と diagram の align・route・label_pos ----
  # 新しい図を含む版をその場でビルドして監査を通し (0)、図形そのものを見て約束どおりに
  # 描けているかと、新しい指定を使わない diagram の描き方が変わっていないかを確かめる (0)。
  # 2 段の輪、セルの数が合わない行、1 本だけの帯、知らない route は検証で止める (1)。
  "0|python3 $A/validate_deck.py $f/vocab-deck.yaml"
  "0|python3 $A/build_deck.py $f/vocab-deck.yaml -o $TMP/vocab.pptx"
  "0|python3 $A/audit_pptx.py $TMP/vocab.pptx --quiet"
  "0|python3 vocab_check.py"
  "1|python3 $A/validate_deck.py $f/bad-vocab.yaml"
  "has:cycle has 2 step(s)|python3 $A/validate_deck.py $f/bad-vocab.yaml"
  "has:has 2 cell(s) for 3 column(s)|python3 $A/validate_deck.py $f/bad-vocab.yaml"
  "has:cell mark 'Maybe' is not in \`marks\`|python3 $A/validate_deck.py $f/bad-vocab.yaml"
  "has:bands has 1 band(s)|python3 $A/validate_deck.py $f/bad-vocab.yaml"
  "has:edge route 'curvy'|python3 $A/validate_deck.py $f/bad-vocab.yaml"

  # ---- 図のパターン（2.16）: pyramid / funnel / venn / tree / hub / swimlane / before_after ----
  # 新しい図を含む版をその場でビルドして監査を通し (0)、図形そのものを見て約束どおりに
  # 描けているか、カタログの各項目がそろい、spec が検証を通り、見本のデッキが
  # カタログから作り直したものと一致するかを確かめる (0)。規則を破る図は検証で止める (1)。
  "0|python3 $A/validate_deck.py $f/patterns-deck.yaml"
  "0|python3 $A/build_deck.py $f/patterns-deck.yaml -o $TMP/patterns.pptx"
  "0|python3 $A/audit_pptx.py $TMP/patterns.pptx --quiet"
  "0|python3 patterns_check.py"
  "1|python3 $A/validate_deck.py $f/bad-patterns.yaml"
  "has:pyramid has 1 level(s)|python3 $A/validate_deck.py $f/bad-patterns.yaml"
  "has:venn has 4 set(s)|python3 $A/validate_deck.py $f/bad-patterns.yaml"
  "has:tree root has no \`children\`|python3 $A/validate_deck.py $f/bad-patterns.yaml"
  "has:hub has no \`center\`|python3 $A/validate_deck.py $f/bad-patterns.yaml"
  "has:names unknown lane 'zz'|python3 $A/validate_deck.py $f/bad-patterns.yaml"
  "has:edge names unknown step 'nope'|python3 $A/validate_deck.py $f/bad-patterns.yaml"
  "has:\`pairs: true\` but before has 2|python3 $A/validate_deck.py $f/bad-patterns.yaml"
  "0|python3 $A/validate_deck.py $A/samples/figure-patterns.yaml"
  "0|python3 $A/build_deck.py $A/samples/figure-patterns.yaml -o $TMP/gallery.pptx"
  "0|python3 $A/audit_pptx.py $TMP/gallery.pptx --quiet"

  # ---- find_pattern.py: 図の論理を言葉で引く ----
  # 日本語・英語の言い方で、期待するパターンが 1 位に来る (0)。何にも当たらない (1)、
  # 問いがない・カタログが読めない (2)。
  "has:1. compare-matrix|python3 $A/find_pattern.py 3つを比べる"
  "has:1. cycle|python3 $A/find_pattern.py 循環を示す"
  "has:1. swimlane|python3 $A/find_pattern.py who does what"
  "has:1. swimlane|python3 $A/find_pattern.py 部門をまたぐ受け渡し"
  "has:1. hierarchy-org|python3 $A/find_pattern.py 組織の階層"
  "has:1. venn|python3 $A/find_pattern.py 重なりを見せる"
  "has:1. logic-tree|python3 $A/find_pattern.py 課題を要素に分解したい"
  "has:1. before-after|python3 $A/find_pattern.py before and after"
  "has:1. funnel|python3 $A/find_pattern.py conversion funnel"
  "has:1. system-context|python3 $A/find_pattern.py data flows between companies"
  "has:spec:|python3 $A/find_pattern.py 3つを比べる"
  "has:img/compare-matrix.png|python3 $A/find_pattern.py 3つを比べる"
  "0|python3 $A/find_pattern.py 循環"
  "0|python3 $A/find_pattern.py --list"
  "0|python3 $A/find_pattern.py --show swimlane"
  "1|python3 $A/find_pattern.py zzzz qqq"
  "2|python3 $A/find_pattern.py"
  "2|python3 $A/find_pattern.py --show no-such-pattern"
  "2|python3 $A/find_pattern.py 循環 --catalog $f/not-a-deck.txt"
  "2|python3 $A/find_pattern.py 循環 --catalog $f/does-not-exist.yaml"

  # ---- 図の形の示唆（validate_deck.py の pattern hint、INFO で落とさない） ----
  # 一列に並べた輪、矢印のない表、すべての線が一点を通る図、散らばった三つの塗りを
  # 拾う (has)。示唆では終了コードは変わらない (0)。既存のきれいな図では何も言わない (lacks)。
  "0|python3 $A/validate_deck.py $f/hint-deck.yaml"
  "has:the edges form a loop (s → l → r → c → back)|python3 $A/validate_deck.py $f/hint-deck.yaml"
  "has:4 rows of boxes repeat the same 3 columns|python3 $A/validate_deck.py $f/hint-deck.yaml"
  "has:every edge touches 'cat'|python3 $A/validate_deck.py $f/hint-deck.yaml"
  "has:three fills recur across rows and columns|python3 $A/validate_deck.py $f/hint-deck.yaml"
  "lacks:pattern hint|python3 $A/validate_deck.py $f/figure-deck.yaml"
  "lacks:pattern hint|python3 $A/validate_deck.py $f/vocab-deck.yaml"
  "lacks:pattern hint|python3 $A/validate_deck.py $f/panels-deck.yaml"
  "lacks:pattern hint|python3 $A/validate_deck.py $f/onepagers-deck.yaml"
  "lacks:pattern hint|python3 $A/validate_deck.py $A/samples/figure-patterns.yaml"

  # ---- 1 枚物の型と lead: 行 ----
  # 報告ブリーフ（N 列 panels + 矢印）、進捗ダッシュボード（tiles）、計画タイムライン、
  # 意思決定メモ、イベント報告、lead: つきの箇条書き・表・2 列をビルドして監査を通す (0)。
  # tiles のない dashboard、5 列、選択肢にない推奨、7 枚のタイルは検証で止める (1)。
  "0|python3 $A/validate_deck.py $f/onepagers-deck.yaml --text $TMP/deck-text.md"
  "has:## 1. Launch slips two weeks|cat $TMP/deck-text.md"
  "has:**The hardware passed|cat $TMP/deck-text.md"
  "0|python3 $A/build_deck.py $f/onepagers-deck.yaml -o $TMP/onepagers.pptx"
  "0|python3 $A/audit_pptx.py $TMP/onepagers.pptx --quiet"
  "1|python3 $A/validate_deck.py $f/bad-onepagers.yaml"
  "has:dashboard has no \`tiles:\`|python3 $A/validate_deck.py $f/bad-onepagers.yaml"
  "has:5 columns|python3 $A/validate_deck.py $f/bad-onepagers.yaml"
  "has:recommend.option 'C' is not one of|python3 $A/validate_deck.py $f/bad-onepagers.yaml"
  "has:7 tile(s)|python3 $A/validate_deck.py $f/bad-onepagers.yaml"

  # ---- 同梱サンプルの 1 枚物 5 本: 検証・生成・監査が通る ----
  "0|python3 $A/validate_deck.py $A/samples/onepager-brief.yaml"
  "0|python3 $A/build_deck.py $A/samples/onepager-brief.yaml -o $TMP/s1.pptx"
  "0|python3 $A/audit_pptx.py $TMP/s1.pptx --quiet"
  "0|python3 $A/validate_deck.py $A/samples/onepager-dashboard.yaml"
  "0|python3 $A/build_deck.py $A/samples/onepager-dashboard.yaml -o $TMP/s2.pptx"
  "0|python3 $A/audit_pptx.py $TMP/s2.pptx --quiet"
  "0|python3 $A/validate_deck.py $A/samples/onepager-timeline.yaml"
  "0|python3 $A/build_deck.py $A/samples/onepager-timeline.yaml -o $TMP/s3.pptx"
  "0|python3 $A/audit_pptx.py $TMP/s3.pptx --quiet"
  "0|python3 $A/validate_deck.py $A/samples/onepager-decision.yaml"
  "0|python3 $A/build_deck.py $A/samples/onepager-decision.yaml -o $TMP/s4.pptx"
  "0|python3 $A/audit_pptx.py $TMP/s4.pptx --quiet"
  "0|python3 $A/validate_deck.py $A/samples/onepager-event.yaml"
  "0|python3 $A/build_deck.py $A/samples/onepager-event.yaml -o $TMP/s5.pptx"
  "0|python3 $A/audit_pptx.py $TMP/s5.pptx --quiet"

  # ---- AI っぽさの癖: 検証器がデッキ単位で拾う ----
  # 全部「ラベル: 説明」の箇条書き、3 項目が 4 枚連続、本文中の矢印、主題の埋もれた
  # 長いタイトル。WARN なので --strict で落ちる (1)。
  "1|python3 $A/validate_deck.py $f/bad-tells.yaml --strict"
  "has:bullets are 'label: text'|python3 $A/validate_deck.py $f/bad-tells.yaml"
  "has:four consecutive slides each show 3 items|python3 $A/validate_deck.py $f/bad-tells.yaml"
  "has:arrows or em-dashes|python3 $A/validate_deck.py $f/bad-tells.yaml"
  "has:the claim is buried in a sentence|python3 $A/validate_deck.py $f/bad-tells.yaml"
  "has:fills ~|python3 $A/validate_deck.py $f/bad-tells.yaml"

  # ---- 欠陥注入: 型の個数・軸・図の規約が効いているか ----
  "1|python3 $A/validate_deck.py $f/bad-archetypes.yaml"
  "has:matrix takes exactly 4 quadrants|python3 $A/validate_deck.py $f/bad-archetypes.yaml"
  "has:split is a figure beside its reading|python3 $A/validate_deck.py $f/bad-archetypes.yaml"

  # ---- 欠陥注入(a): 比較器が差を検出できるか ----
  "1|python3 roundtrip_check.py $f/mutated-deck.yaml $f/clean-deck.pptx"

  # ---- 欠陥注入(b): 表現できない内容を LOSS として報告するか ----
  "1|python3 $A/extract_deck.py $f/messy-deck.pptx -o $TMP/messy.yaml"
  "has:grouped drawing|python3 $A/extract_deck.py $f/messy-deck.pptx -o $TMP/messy2.yaml"
  "has:exploded pie|python3 $A/extract_deck.py $f/messy-deck.pptx -o $TMP/messy3.yaml"

  # ---- ブラウザで見るページ（preview_web.py、PC とスマホ）: 図の数・跳び先・ハッシュ・キー・章のチップ ----
  # 画像は固定の小さな JPEG を枚数ぶん写して使う（LibreOffice 不要）。spec から (0)、
  # spec のない .pptx から (0)、題の置き場のない乱雑なデッキから (0)。画像の枚数が
  # 合わないときは、黙って短いページを書かずに理由を言って止める (1)。入力なし (2)。
  "0|python3 web_preview_check.py --spec $f/clean-deck.yaml --expect-sections 現状"
  "0|python3 web_preview_check.py --pptx $f/clean-deck.pptx --expect-sections 現状"
  "0|python3 web_preview_check.py --spec $f/archetype-deck.yaml --expect-sections 打ち手"
  "0|python3 web_preview_check.py --pptx $f/messy-deck.pptx --expect-sections ''"
  "has:<button type=\"submit\">Go</button>|mkdir -p $TMP/en/img; for i in 1 2 3 4; do cp $f/web-slide.jpg $TMP/en/img/s-\$i.jpg; done; python3 $A/preview_web.py $TMP/en --pptx $f/messy-deck.pptx --lang en >/dev/null; cat $TMP/en/index.html"
  "1|python3 web_preview_check.py --spec $f/clean-deck.yaml --images 7"
  "has:7 image(s) in|python3 web_preview_check.py --spec $f/clean-deck.yaml --images 7"
  "has:but 8 slide(s) in|python3 web_preview_check.py --spec $f/clean-deck.yaml --images 9"
  "2|python3 $A/preview_web.py $TMP"
  "2|python3 $A/preview_web.py $TMP --pptx $f/not-a-deck.txt"
  "2|python3 $A/preview_web.py $TMP/no-such-dir --spec $f/clean-deck.yaml"
  "2|bash $A/preview_web.sh $f/does-not-exist.pptx -o $TMP/ph"
  "2|bash $A/preview_web.sh $f/clean-deck.pptx -q 0 -o $TMP/ph"

  # ---- レビュー欄（--comments）: 既定では何も変わらず、付けると枚ごとの欄と保存の両経路が入る ----
  # 付けないときは 2.17.0 の出力とバイト単位で同じ (0)。付けると欄・絞り込み・書き出し・db と
  # localStorage の両経路・入力中のキー無視 (0)。spec の id を文書の id に使い、使えない id と
  # 重複は pN に落とす (0)。付けたページを 2.17.0 と比べると違う、つまり比較が効いている (1)。
  "0|python3 web_preview_check.py --spec $f/clean-deck.yaml --golden $f/web-preview-2.17.0.html"
  "1|python3 web_preview_check.py --spec $f/clean-deck.yaml --comments --golden $f/web-preview-2.17.0.html"
  "0|python3 web_preview_check.py --spec $f/review-deck.yaml --comments --expect-keys cover,intro,p3,p4,p5,p6"
  "0|python3 web_preview_check.py --pptx $f/clean-deck.pptx --comments --expect-sections 現状"
  "has:<button type=\"button\" id=\"rvx\">Export</button>|mkdir -p $TMP/en2/img; for i in 1 2 3 4; do cp $f/web-slide.jpg $TMP/en2/img/s-\$i.jpg; done; python3 $A/preview_web.py $TMP/en2 --pptx $f/messy-deck.pptx --lang en --comments >/dev/null; cat $TMP/en2/index.html"
  "has:data-s=\"差し戻し\"|mkdir -p $TMP/lb/img; for i in 1 2 3 4; do cp $f/web-slide.jpg $TMP/lb/img/s-\$i.jpg; done; python3 $A/preview_web.py $TMP/lb --pptx $f/messy-deck.pptx --comments --review-labels '了承,差し戻し' >/dev/null; cat $TMP/lb/index.html"
  "2|python3 $A/preview_web.py $TMP/lb --pptx $f/messy-deck.pptx --comments --review-labels 'a:b'"
  "2|python3 $A/preview_web.py $TMP/lb --pptx $f/messy-deck.pptx --review-labels 'OK,NG'"

  # ---- 集まったコメントを戻す（preview_comments.py）: 書き出しの Markdown と db の JSON ----
  # spec の id で今のページに付け直す (0、moved を出す)。spec に無い id は指摘して残す (1)。
  # シートには箇所ごとに入り、OK だけの枚は入れず、二度流しても増えない。入力なし (2)。
  "0|python3 $A/preview_comments.py $f/review-export.md --spec $f/review-deck.yaml"
  "has:moved: [intro] p1 -> p2|python3 $A/preview_comments.py $f/review-export.md --spec $f/review-deck.yaml"
  "has:p5 質問: この 7 割は件数か金額か|python3 $A/preview_comments.py $f/review-export.md"
  "has:p3 数字の出典を入れる|python3 $A/preview_comments.py $f/review-db"
  "lacks:p4|python3 $A/preview_comments.py $f/review-db"
  "1|python3 $A/preview_comments.py $f/review-db --spec $f/review-deck.yaml"
  "has:[gone] (p9) is not in|python3 $A/preview_comments.py $f/review-db --spec $f/review-deck.yaml"
  "has:\"slide\": \"intro\"|python3 $A/preview_comments.py $f/review-db/reviews/intro.json --json"
  "has:- [ ] 要修正: 矢印の向きが逆|cp $f/review-sheet.md $TMP/sh.md; python3 $A/preview_comments.py $f/review-export.md --spec $f/review-deck.yaml --sheet $TMP/sh.md; cat $TMP/sh.md"
  "has:2 comment(s) added|cp $f/review-sheet.md $TMP/sh2.md; python3 $A/preview_comments.py $f/review-export.md --spec $f/review-deck.yaml --sheet $TMP/sh2.md"
  "has:0 comment(s) added|python3 $A/preview_comments.py $f/review-export.md --spec $f/review-deck.yaml --sheet $TMP/sh2.md"
  "lacks:- [ ] OK|cat $TMP/sh2.md"
  "1|cp $f/review-sheet.md $TMP/sh3.md; python3 $A/preview_comments.py $f/review-db --sheet $TMP/sh3.md"
  "has:no location in the sheet for: p9 [gone]|cp $f/review-sheet.md $TMP/sh4.md; python3 $A/preview_comments.py $f/review-db --sheet $TMP/sh4.md"
  "2|python3 $A/preview_comments.py $f/does-not-exist.md"
  "2|python3 $A/preview_comments.py $f/review-export.md --sheet $f/clean-deck.yaml"

  # ---- 前提なし ----
  "2|python3 $A/extract_deck.py $f/not-a-deck.txt -o $TMP/x.yaml"
  "2|python3 $A/extract_deck.py $f/does-not-exist.pptx -o $TMP/x.yaml"
  "2|python3 roundtrip_check.py $f/clean-deck.yaml"
)

# 一続きの変換（.pptx → PDF → JPEG → index.html）は LibreOffice があるときだけ見る。
if command -v soffice >/dev/null 2>&1 && command -v pdftoppm >/dev/null 2>&1; then
  CASES+=(
    "has:8 slide(s), 1 section(s)|bash $A/preview_web.sh $f/clean-deck.pptx -s $f/clean-deck.yaml -o $TMP/web -r 20"
    "0|test \$(ls $TMP/web/img/s-*.jpg | wc -l) -eq 8"
    "has:8 slide(s)|bash $A/preview_web.sh $f/clean-deck.pptx -o $TMP/web -r 20"
    "has:8 slide(s), 1 section(s), review bar on|bash $A/preview_web.sh $f/clean-deck.pptx -s $f/clean-deck.yaml -o $TMP/webc -r 20 --comments --review-labels 'OK,要修正'"
  )
else
  echo "SKIP  LibreOffice / pdftoppm が無いため、preview_web.sh の一続きの変換は見ていない"
fi

# レビュー欄をヘッドレスの Chrome で動かす（puppeteer があるときだけ）。ローカルでは書いて再読み込み
# しても残る・入力中の j/k でページが動かない・絞り込み・書き出しの Markdown、Artifact の db（偽の
# window.claude）では reviews/<spec の id> に書き、既存の文書が欄に出る。
if command -v node >/dev/null 2>&1; then
  mkdir -p "$TMP/br/img"; for i in 1 2 3 4 5 6; do cp "$f/web-slide.jpg" "$TMP/br/img/s-00$i.jpg"; done
  python3 "$A/preview_web.py" "$TMP/br" --spec "$f/review-deck.yaml" --rev test --comments >/dev/null
  timeout 180 node web_preview_browser.cjs "$TMP/br" >"$TMP/brout" 2>&1; code=$?
  if [[ $code -eq 2 ]]; then echo "SKIP  ブラウザでの確認（$(head -1 "$TMP/brout")）"
  else CASES+=("has:OK browser:|cat $TMP/brout"); fi
else
  echo "SKIP  node が無いため、レビュー欄をブラウザで動かす確認はしていない"
fi

pass=0; fail=0
run() { eval "$1" >"$TMP/out" 2>&1; echo $?; }

for case in "${CASES[@]}"; do
  want="${case%%|*}"; cmd="${case#*|}"
  code="$(run "$cmd")"
  if [[ "$want" == lacks:* ]]; then
    needle="${want#lacks:}"
    if grep -qF -- "$needle" "$TMP/out"; then
      fail=$((fail+1)); echo "NG  出力に次の文字列が出てはいけない: $needle"; echo "    $cmd"
      grep -F -- "$needle" "$TMP/out" | head -3 | sed 's/^/    | /'
    else
      pass=$((pass+1))
    fi
  elif [[ "$want" == has:* ]]; then
    needle="${want#has:}"
    if grep -qF -- "$needle" "$TMP/out"; then
      pass=$((pass+1))
    else
      fail=$((fail+1)); echo "NG  出力に次の文字列がない: $needle"; echo "    $cmd"
    fi
  elif [[ "$code" == "$want" ]]; then
    pass=$((pass+1))
  else
    fail=$((fail+1)); echo "NG  期待 exit=$want 実際 exit=$code"; echo "    $cmd"
    sed -n 1,8p "$TMP/out" | sed 's/^/    | /'
  fi
done

# ---- 連結: 乱雑なデッキを抽出して作り直すと、マスタ準拠のデッキになる ----
python3 "$A/extract_deck.py" "$f/messy-deck.pptx" -o "$TMP/chain.yaml" >/dev/null 2>&1
if python3 "$A/build_deck.py" "$TMP/chain.yaml" -o "$TMP/chain.pptx" >/dev/null 2>&1 \
   && python3 "$A/audit_pptx.py" "$TMP/chain.pptx" --quiet >"$TMP/audit" 2>&1; then
  pass=$((pass+1))
else
  fail=$((fail+1)); echo "NG  抽出→再ビルド→audit の連結が通らない"; sed -n 1,10p "$TMP/audit" | sed 's/^/    | /'
fi

echo "合格 $pass / 不合格 $fail"
[[ $fail -eq 0 ]] || exit 1
