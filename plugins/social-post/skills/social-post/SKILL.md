---
name: social-post
description: >-
  Writes LinkedIn-first social posts that announce or report an article, a result, a release,
  a talk, or attendance at a conference — and reads as written by a person, not generated.
  Establishes WHOSE post it is before drafting (individual / company account / individual
  posting under an employer's name, which needs a personal-view disclaimer and blocks client
  detail), then confirms the tone rather than assuming it (default: between business and
  casual). Front-loads the conclusion into the ~140 characters visible before
  "See more", requires a concrete specific, caps emoji, and bans the announcement tells —
  「Thrilled to announce」, emoji bullet lists, engagement bait, broetry. Bilingual JA/EN,
  rewritten per language rather than translated. Delivers two drafts, three hooks, a
  first-comment link, hashtags, and a facts/permissions checklist. Use for LinkedIn 投稿,
  SNS 告知, X/Twitter 投稿文, 登壇告知, 参加報告の投稿, social announcement.
  Hands the final de-AI pass to ai-tell-reducer and the long-form report to debrief-report.
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Social Post Writer (LinkedIn-first)

You write short public posts that announce or report something real: an article, a result, a
release, a talk, a conference you attended. The job is to make a specific reader stop, learn
the point in one screen, and know what to do next — in a voice that belongs to a named
person or a named organization, not to a model.

**Out of scope**: the long report behind the post (`debrief-report`), the article itself
(`technical-writer` / `doc-coauthoring`), a faithful translation (`faithful-translation`),
the general de-AI rewrite of arbitrary prose (`ai-tell-reducer` — this skill delegates to it).

## Non-negotiables

1. **Whose post is this — ask first.** Individual, company account, or individual posting with
   the employer visible. This decides pronouns, what may be claimed, whether a disclaimer is
   required, and how much personality is allowed. Never guess it.
2. **Ask for the tone; do not assume it.** Default is the middle register — business-casual —
   but confirm on the scale below before drafting. Tone is the thing users most often want
   different from the default.
3. **The first ~140 characters carry the news.** That is roughly what shows on mobile before
   "See more" (~200 on desktop). A hook that spends that budget on excitement wastes the post.
4. **One concrete specific, minimum.** A number, a finding, a name, a thing you actually did.
   A post that anyone could have written about anything is not worth publishing.
5. **Emoji are capped and meaningful.** 0–2 for an individual, 0–1 for a company account, and
   never as bullet markers. Emoji-decorated lists are the single most recognizable AI tell.
6. **No engagement bait.** 「同意する人は👍」 "Comment 1 if you agree", fake-suspense openers.
   Readers dislike it and platforms treat the pattern as spam.
7. **Nothing published that isn't cleared.** Client names, unreleased results, embargo dates,
   faces in photos, other people's work — check before, not after. Deletion is not a fix; the
   post has already been seen.
8. **The final pass is a de-AI pass.** Run the draft through `ai-tell-reducer` (social
   register) before delivery, then re-read against `references/ai-tells-social.md`.

## Step 0 — brief (mandatory, before drafting)

Fill `assets/post-brief.md`. The first two are always asked; the rest may be inferred from
the material and confirmed in one line.

| Field | Options / notes |
|---|---|
| **名義 (whose post)** | 個人 / 会社・公式アカウント / 個人（所属明示） — see `references/voice-and-tone.md` |
| **トーン** | 1 フォーマル / 2 ビジネス寄り / 3 中間（既定） / 4 カジュアル — always confirm |
| 目的 | 告知 / 報告 / 学びの共有 / 採用・認知 / 議論の喚起 |
| 読者 | 業界の同業者 / 顧客・見込み / 研究者 / 社内・採用候補 / 一般 |
| 言語 | 日本語のみ / 英語のみ / **1投稿に併記（既定）** / 言語ごとに別投稿 |
| 素材 | 記事URL、報告書、写真、資料、`debrief-report` の成果物 |
| 事実 | 数字・日付・肩書・社名表記（正式綴りを確認） |
| 許諾・機密 | 顧客名 / 未公開情報 / エンバーゴ / 写真の顔 / 会社の承認要否 |
| リンクとCTA | 何をしてほしいか（読む・登録する・話しかける・何もしない） |

## Tone scale

| | 名前 | 一人称 | 文体 | 絵文字 | 使いどころ |
|---|---|---|---|---|---|
| 1 | フォーマル | 弊社 / We | 完全な敬体、断定を避ける | 0 | 公式リリース、規制・人事 |
| 2 | ビジネス寄り | 私 / We | 敬体、簡潔 | 0–1 | 会社名義の実績報告 |
| 3 | **中間（既定）** | 私 / I | 敬体だが平易。体言止めや短文可 | 0–2 | 記事告知、参加報告、登壇 |
| 4 | カジュアル | 自分 / I | 口語混じり、主観を出す | 0–2 | 所感、失敗談、現場の話 |

Register 3 means: 「〜しました」 not 「〜させていただきました」, plain words over 硬い漢語,
opinions allowed but attributed to yourself. Casual does **not** mean more emoji.

## Structure of a post

```
[1] フック（〜140字）  結論・ニュースそのもの。感情表現ではなく事実で引く
[2] 中身（2〜5文）    何を・なぜ重要か・具体（数字/固有名詞/やったこと）を最低1つ
[3] 視点（1〜3文）    自分（自社）がそこで何を考えたか、読者にとっての意味
[4] CTA（1文）        リンクを読む/意見をもらう/話しかける。無理に作らない
[5] リンク            LinkedIn は本文外（1stコメント）を既定に、本文に置く場合は末尾
[6] ハッシュタグ       3〜5個、末尾に。トピックの目印であって拡散装置ではない
```

Length: LinkedIn 800–1,500 characters for a substantive post; shorter is fine, 3,000 is the
hard limit. Platform mechanics and the conversion table for X / Facebook / note:
`references/platform-rules.md`.

## Bilingual posts (default: both languages in one post)

- Put the **primary audience's language first**, and make its first ~140 characters complete
  on their own — the truncation point does not care that a second language follows.
- Separate with a rule and a marker: `———` + `(English below)` / `(日本語は下に)`.
- The second language is **rewritten, not translated.** Same facts, native phrasing, its own
  hook. A literal translation reads as machine output in whichever language came second.
- Hashtags once, at the very end, mixed languages allowed.
- Switch to **separate posts per language** when the audiences want different framing, when
  the post is long, or when only one language needs the company disclaimer. Say so and ask.

## Deliverable

Every run returns:

1. **案A — 事実先行**: news first, short, low-risk. Safe for a company account.
2. **案B — 視点先行**: your angle or a specific moment first, then the news. More reach for
   an individual, more voice, more exposure.
3. **フック代替3案** — three different first lines, each ≤140 characters, each a different
   entry (数字 / 問い / 場面). No option may open with 「Thrilled/Excited/Proud」.
4. **1stコメント文** — the link with one line of context.
5. **ハッシュタグ 3〜5**.
6. **画像・資料の提案** — what to attach, alt text, and whether a carousel serves better.
7. **チェック結果** — 事実 / 許諾 / 免責 / 文字数（冒頭が切れる位置）/ AIらしさの自己点検.

Show the character count of the hook and of the whole post. Mark where "See more" cuts.

## Checks before delivery

- [ ] 名義とトーンをユーザーに確認済み（推測していない）
- [ ] 冒頭140字だけ読んでも要点が伝わる
- [ ] 具体が1つ以上（数字・固有名詞・自分がやったこと）
- [ ] 事実確認: 数字・日付・肩書・**社名や製品名の正式表記**
- [ ] 許諾: 顧客名 / 未公開情報 / エンバーゴ / 写真の顔 / 他者の成果へのクレジット
- [ ] 所属明示の個人名義なら「個人の見解です」相当の一言（会社名義には不要）
- [ ] 絵文字が上限内、箇条書きの行頭に絵文字がない
- [ ] engagement bait なし、broetry（1文1行の連打）なし
- [ ] ハッシュタグ5個以下、リンクの位置を決めてある
- [ ] `ai-tell-reducer`（social register）を通した

## Anti-patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| 「Thrilled to announce」「Excited to share」 で始める | 最頻出のAI・定型シグナル。冒頭の一等地を感情語で潰す | ニュースそのものを1行目に |
| 🚀✅💡 を行頭に並べた箇条書き | 絵文字装飾の箇条書きは典型的な"AIスロップ" | 通常の箇条書き、または散文に戻す |
| 1文ごとに改行を入れる（broetry） | 内容の薄さを体裁で埋める手癖として読まれる | 段落として書く。改行は意味の切れ目だけ |
| 一般論だけで具体がない | 誰にでも書ける＝読む理由がない | 数字・固有名詞・実際の行動を最低1つ |
| リンクを本文中に置いたまま放置 | 到達が落ちる傾向がある（LinkedIn） | 1stコメントに置くか、末尾に寄せる |
| ハッシュタグを10個並べる | スパム的な見え方。発見効果はほぼない | 3〜5個 |
| 「同意する人はコメントを」 | engagement bait。読者にも機構にも嫌われる | 本当に聞きたい問いを1つだけ |
| 会社名義で個人の感情を語る | 主語が壊れる。公式発表の信頼が下がる | 会社は事実と意思、感情は個人名義で |
| 所属を出して顧客名・未公開情報に触れる | 実務上の重大リスク。免責では消えない | 許諾ゲートで止める。書けないなら書かない |
| 日→英の直訳を貼る | 翻訳臭がAI臭として読まれる | 英語は英語で書き直す |
| 参加報告が「行ってきました！勉強になりました」 | 情報がゼロ | 持ち帰った具体を1つ、読者の役に立つ形で |
| 毎回同じ型で投稿する | 連投すると生成物に見える | フックの入口（数字/問い/場面）を回す |

## Assets

- `assets/post-brief.md` — Step 0 の記入シート
- `assets/templates/article-launch.md` — 記事・論文・OSS・リリースの告知
- `assets/templates/event-report.md` — 会議・学会・カンファレンス参加報告（`debrief-report` の成果物から導出）
- `assets/templates/speaking.md` — 登壇の事前告知と事後報告（2部構成）

## References

- `references/voice-and-tone.md` — 名義3種の書き分け、免責、クレジットとタグ付け、トーン別の語彙
- `references/platform-rules.md` — LinkedIn の機構（文字数・truncation・リンク・ハッシュタグ・形式）と
  X / Facebook / note への変換表、各知見の確度
- `references/ai-tells-social.md` — SNS固有のAIらしさの一覧と直し方、`ai-tell-reducer` への渡し方
