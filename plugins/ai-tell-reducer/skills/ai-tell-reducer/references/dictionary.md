# The dictionary scan

`scripts/dict_scan.py` reads the bundled dictionary (`dict/ja.ini`) and lists the places in a text where a known tell *may* be present. It finds places. It does not judge them.

## Contents

- Where it fits
- Commands
- Three files
- Dictionary format
- What the evidence says, and the evidence field
- Sources
- Adding to it
- Promoting and retiring
- Other languages
- Relation to textlint

## Where it fits

SKILL.md says a count is how you notice a place worth looking at and never how you decide. The dictionary is that noticing step made mechanical, for documents too long to hold in one reading. Three consequences:

- A hit is a candidate. Apply the category's `test` before changing anything.
- No hits does not mean the text is clean. The stance layer and most of the expression layer cannot be found by a word list, and words not yet in the dictionary are invisible to it.
- Do not report hit counts as a quality score, and do not edit until the count reaches zero.

Use it when the input is a file of more than a few hundred lines, when the same document will be edited again, or when the user asks for an inventory (洗い出し). For a short inline draft, read it instead.

## Commands

```
python3 scripts/dict_scan.py FILE...                  candidates with context and a suggested direction
python3 scripts/dict_scan.py FILE... --summary        counts per entry, grouped by category
python3 scripts/dict_scan.py FILE... --format tsv     ledger with an empty `decision` column
python3 scripts/dict_scan.py FILE... --headings       every heading; sentence-shaped ones marked 文
python3 scripts/dict_scan.py FILE... --only vogue     one category or one entry id
python3 scripts/dict_scan.py FILE... --evidence measured --evidence guideline
                                                      only entries with that kind of support
python3 scripts/dict_scan.py --selftest               every entry matches its own example
```

Exit `0` no candidates, `1` candidates, `2` bad arguments, unreadable input, or a broken dictionary.

Front matter, fenced code, inline code, URLs, citation keys, cross-references and heading attributes are not scanned.

## Three files

| File | Holds | Who decides |
|---|---|---|
| `dict/ja.ini` (bundled) | Tells that would be a tell in any document of this register | The skill maintainer |
| `.ai-tell-dict.ini` (project) | Words this project decided to replace, and that are not general | The author |
| `.ai-tell-allow.txt` (project) | Phrases this project decided to keep | The author |

The two project files are read automatically from the working directory. `--dict PATH` and `--allow PATH` name them explicitly. A project entry with the same id as a bundled one replaces it.

The allow list takes one phrase per line. A candidate is dropped only when it lies inside an occurrence of an allowed phrase, so allowing `効く施策` keeps that term and still reports `この分類が見直しに効く`. A line `id:<entry id>` turns an entry off altogether.

## Dictionary format

```ini
[category:wago-figurative]
label = 和語の比喩的な転用
test = 字義どおりの動詞・漢語に置き換えて意味が通るか
ref = japanese-word-choice.md#1

[wago-tatamu]
category = wago-figurative
pattern = 畳(む|み|ん|ま|め)
example = 例外規定を本則の中に畳む
counter = (optional) a phrase the pattern must NOT match
fix = (optional) direction specific to this word
scope = (optional) any | heading | body
evidence = (optional here) overrides the category's level
source = (optional) key from the Sources table below
note = (optional) what the source actually says
added = 2026-10
```

`pattern` is a Python regular expression. `example` is required: `--selftest` fails an entry that does not match its own example, matches its `counter`, or matches the empty string. `fix` names a direction, never a single replacement, because the right word depends on what the sentence means.

## What the evidence says, and the evidence field

Most published lists of "AI words" in Japanese are not backed by measurement. A 2025 undergraduate thesis at Hiroshima University collected 148 reader statements about what makes a text feel AI-written and compared them with measured features of generated and human texts. One statement matched: heavier use of 読点. No statement about vocabulary, content or expression matched. Some claims ran the other way (体言止め was far more common in the human texts). The features that did separate the two were ones readers rarely name: low variation in sentence length and in sentences per paragraph, sentence endings that avoid assertion (「ている」), a high type-token ratio, and a high noun ratio in formal text. A separate count over 180 generated samples found 「〜を浮き彫りにする」 zero times, and 「いかがでしたか」 was being discussed as a mark of mass-produced web articles before ChatGPT was released.

Two consequences for this dictionary:

- An entry is a reason to look, for the reason its category gives (the phrase carries no information, or is opaque, or is a stock figure). It is not evidence that a model wrote the text, and the report must not say so.
- Each entry records why it is listed, so a user can scan with only the better-supported entries.

| `evidence` | Meaning |
|---|---|
| `measured` | Reported as more frequent in generated text by a count over samples |
| `guideline` | A public body's writing guidance recommends replacing or avoiding it |
| `curated` | Listed by another tool or catalog, without measurement |
| `observed` | Found in an actual editing job done with this skill |
| `folk` | Widely claimed, and unmeasured or contradicted by measurement |

A category sets the default level and an entry may override it. Bundled entries must have a level. Project entries default to `observed`. `folk` entries stay in the dictionary when the phrase fails a test on its own merits, with a `note` saying what the measurement found.

The statistical features above are not word-level, so the dictionary does not cover them. They belong to SKILL.md cause 11 (uniform rhythm) and cause 1 (reflexive hedging), and are judged by reading.

## Sources

| Key | Source | Used for |
|---|---|---|
| `koyobun-2022` | 文化審議会「公用文作成の考え方（建議）」2022-01-07. <https://www.bunka.go.jp/seisaku/bunkashingikai/kokugo/hokoku/pdf/93651301_01.pdf> | Headings, redundant phrasing, double negatives, 喫緊の課題 |
| `ninjal-2006` | 国立国語研究所「外来語」委員会『「外来語」言い換え提案 第1回〜第4回 総集編』2006-03. <https://www2.ninjal.ac.jp/gairaigo/Teian1_4/iikae_teian1_4.pdf> | Loanwords with low measured comprehension. Only a business-prose subset is bundled. The survey is from 2006, so a word may have settled since |
| `textlint-ai-writing` | textlint-ja/textlint-rule-preset-ai-writing (MIT). <https://github.com/textlint-ja/textlint-rule-preset-ai-writing> | Hype expressions, some redundant phrasing |
| `onishi-2025` | 大西夢「AI生成文からみた『自然な日本語』についての研究」広島大学文学部 令和7年度卒業論文. Not peer reviewed. <https://home.hiroshima-u.ac.jp/jshira/papers/AI生成文からみた「自然な日本語」についての研究（大西夢）.pdf> | The 148-statement comparison and the statistical features |
| `imoto-2026` | Count over 180 generated samples (6 models × 10 topics × 3 runs) attributed to 井本賢, 2026-08. Read only through `fyve-2026`. The primary source was not located | Frequencies of 適切な, 重要です, 本記事では, を活用する, 不可欠 |
| `fyve-2026` | 「AI文章の見分け方」検証記事, fyve. Secondary. <https://fyve.co.jp/ai-advisor/articles/ai-text-detection-myths-japan> | Summary of the two items above, and the dating of いかがでしたか |
| `jst-2006` | Science Portal (JST) column on stock phrases in news writing, 2006-10-15. An essay. <https://scienceportal.jst.go.jp/explore/review/20061015_01/index.html> | 「成り行きが注目される」「議論が期待される」 |

`imoto-2026` entries are marked `measured` on the strength of a secondary report. If the primary source is found and says otherwise, change the level.

## Adding to it

Add an entry when a tell was found by reading and the dictionary missed it.

1. Decide where it belongs. Would the word be a tell in a different document of the same register? Then it goes in the bundled dictionary. If it is only a tell here, because this project chose another term, it goes in the project dictionary.
2. Write the narrowest pattern that catches the tell. A bare common word produces candidates nobody will read. Constrain it with the particle or noun it appears with (`(軸|尺度)に載せ`, not `載せ`), and add a `counter` for the ordinary use.
3. Set `evidence` honestly, with a `source` when there is one. A word you believe is a tell and cannot support is `folk`. A word found in the user's document during a job is `observed`.
4. Give it a category that already exists if one fits. A new category needs a `test` phrased as a question about the reader and a `ref` to the reference section that explains it.
5. Run `python3 scripts/dict_scan.py --selftest`, then `tests/run_tests.sh`.
6. For a bundled entry, add a line to a fixture in `tests/fixtures/` so its detection is covered, and bump the plugin version.

## Promoting and retiring

At the end of a job, look at the project dictionary. Entries that would apply to the next document belong in the bundled one. Propose them to the user and do not move them silently, since the bundled dictionary ships to every project.

Vogue words date. `added` records when an entry went in. An entry that has produced no true candidate across several documents, or whose word has passed into ordinary use, should be removed. A dictionary that only grows turns into the ban list this skill is meant to avoid.

## Other languages

`--lang CODE` selects `dict/CODE.ini`. Only `ja` ships. An English dictionary would take its entries from `english-patterns.md`.

## Relation to textlint

textlint with `prh` is the common tool in Japanese technical writing for enforcing a fixed term list in CI. It needs one expected replacement per entry, which suits decisions already made (表記ゆれ, a settled 言い換え表) and does not suit candidates that need judgment. Use this scan to reach the decisions, and copy the settled ones into the project's `prh.yml` if the project runs textlint. `@textlint-ja/textlint-rule-preset-ai-writing` covers mechanical list formatting, hype words, emphasis patterns and colon continuation, which overlap this skill's surface layer and not its word-choice entries.
