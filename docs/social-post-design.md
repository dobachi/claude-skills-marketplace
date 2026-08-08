# social-post — Design Notes

Why the `social-post` skill is shaped the way it is, and how much to trust the numbers behind
its platform rules. Written **2026-08-08** alongside the skill. Rationale lives here;
`SKILL.md` and `references/` carry rules only.

Method note: a targeted best-practice review (five web searches, no full-text deep dive), not
a `grounded-research` run. Most LinkedIn "algorithm" material is published by tool vendors
who sell against the answer, so the skill tags every borrowed number by confidence and
instructs the agent not to write copy on the strength of a contested multiplier.

## The problem this skill solves

Announcement posts fail in two directions at once. Written by hand under time pressure they
become 「参加してきました。学びが多かったです」 — zero information. Written by a model they
become 「Thrilled to announce…」 plus emoji bullets — the shape readers now actively hunt for
and mock. Both failures are about the same missing thing: a specific, in a voice that belongs
to someone.

The second failure got worse in 2026: Bloomberg and TechRadar both covered LinkedIn users
scrutinizing em dashes, emoji patterns and repeated openers to call out AI-written posts. A
skill that generates posts has to be built against that scrutiny, not blind to it.

## Design decisions

**Whose post it is, asked first.** The three voices — 個人 / 会社 / 個人（所属明示）— differ
in what may be claimed, not just in tone. The third is the trap: with the employer visible,
readers treat the post as semi-official. Japanese corporate guidance (総務省 and the standard
corporate SNS guidelines) converges on two rules for it — state that views are personal, and
never post confidential or client information, during or after employment. Encoded as a
required disclaimer plus a permissions gate, with the explicit note that the disclaimer does
not widen what may be said.

**Tone is confirmed, never assumed.** The user asked for a default between business and
casual, and for the tone to be checked each time. Implemented as a four-level scale with
worked JA and EN examples per level, because "business-casual" alone is not actionable —
whether 「〜させていただきました」 is allowed is the kind of thing that has to be shown.

**~140 characters, not "write a hook".** The truncation point is the one platform fact with
real leverage and it is well established (≈140 mobile, ≈200–210 desktop, 3,000 limit). It
makes an otherwise vague instruction mechanical: the news goes above the fold, emotional
framing goes below it.

**Emoji capped rather than banned.** A ban is a different tell — text with a suspicious
absence of everything. The rule is 0–2 (0–1 corporate), never as bullet markers, and only
where deleting it would change meaning. Emoji bullet lists are called out separately because
they are the single most recognizable pattern.

**De-AI work delegated to `ai-tell-reducer`.** That skill already covers rhythm, hedging,
inflated diction, em-dash and tricolon overuse, in both languages, and it explicitly handles
the social register. Duplicating its lists would produce a worse copy that drifts. This skill
keeps only the platform-specific tells (announcement openers, emoji bullets, broetry,
engagement bait, hashtag stuffing, empty attendance reports) and the handoff protocol.

**Bilingual in one post, rewritten per language.** The user chose a single post carrying both
languages. That collides with the truncation rule — only the first language is above the fold
— so the skill requires naming which language leads and making its first 140 characters
self-contained, with a rule and marker between the two halves. The second language is
transcreated, never translated: a literal translation is itself read as machine output.

**Two drafts plus three hooks.** 案A (fact-first, safe for a corporate account) and 案B
(angle-first, more voice) differ in *strategy*, not in polish, so the user picks a stance
rather than a wording. Three hooks give the entry points that matter — 数字 / 問い / 場面.

**Genre templates: article launch, event report, speaking.** Chosen by the user. The event
report template deliberately narrows the input: `debrief-report` output is often 社内限, and a
post is public, so the template forces a disclosure pass and one single takeaway rather than
a compressed report. Awards/hiring/team posts were left out of the assets; the voice
reference covers the corporate-account rules they would need.

**No fabricated humanity.** Adding invented anecdotes or numbers to make a post feel lived-in
is a worse defect than sounding like AI. Stated as a guardrail in both the skill and the
tells reference, matching `ai-tell-reducer`'s line, and paired with a refusal to do detector
evasion (invisible characters, deliberate typos).

## Confidence in the platform numbers

`references/platform-rules.md` tags each rule 確 / 傾 / 説:

- **確** — 3,000-character limit, the "See more" cutoff, and the AI-tell reporting.
- **傾** — hashtags 3–5 with little discovery value, carousels outperforming plain text,
  personal profiles outperforming company pages, engagement bait treated as spam.
- **説** — the −18.8% reach figure for an in-body link (one vendor's 1.3M-post dataset), the
  68% penalty for 6+ hashtags, and every "8x / 14x personal vs company" multiplier. Usable as
  operating heuristics; not to be asserted as fact, and not a basis for copy decisions.

Posting-time advice was deliberately excluded from the rules: it varies by audience and would
not change a single word of a draft.

## Sources

- [ChatGPT-Written LinkedIn Posts Have Users Analyzing Emojis, Other AI Signs — Bloomberg](https://www.bloomberg.com/news/articles/2026-01-30/chatgpt-written-linkedin-posts-have-users-analyzing-emojis-other-ai-signs)
- [Blade Runners of LinkedIn are hunting for replicants – one em dash at a time — TechRadar](https://www.techradar.com/computing/artificial-intelligence/blade-runners-of-linkedin-are-hunting-for-replicants-one-em-dash-at-a-time)
- [LinkedIn Character Limits 2026 — AuthoredUp](https://authoredup.com/blog/linkedin-character-limit)
- [LinkedIn Post Best Practices 2026 — ConnectSafely.ai](https://connectsafely.ai/articles/linkedin-post-best-practices-guide-2026)
- [How the LinkedIn Algorithm Works (2026) — Sprout Social](https://sproutsocial.com/insights/linkedin-algorithm/)
- [LinkedIn Personal Profiles vs Company Pages — Digital Applied](https://www.digitalapplied.com/blog/linkedin-personal-profiles-vs-company-pages-8x-engagement)
- [SNSの正しい利用 — 総務省 国民のためのサイバーセキュリティサイト](https://www.soumu.go.jp/main_sosiki/cybersecurity/kokumin/security/business/staff/13/)
- [従業員・企業アカウント担当者が学んでおくべきSNS利用時のリスクと対策 — 三菱電機デジタルイノベーション](https://www.mdsol.co.jp/column/column_120_1594.html)
- [企業が定めるべき従業員のSNSガイドラインとは — エルテス](https://eltes-solution.jp/column/digitalrisk-102)
