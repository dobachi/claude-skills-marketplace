---
name: commit-safe
description: 安全なコミットから任意でリリースまでを一続きで支援するスキル。開始時に「今回はリリースまで含めるか？」を一度だけ確認し、No ならコミットのみで終了、Yes ならバージョン更新・CHANGELOG・タグ・push・GitHub Release・パッケージ公開まで、各段階でユーザー承認ゲートを挟みながら進める。変更内容を確認してから選択的にコミットし、大きな変更ではファイル指定コミットを提案、git add -A の使用を防止。バンドルした commit.sh が AI署名付きコミットを防ぎ、release-preflight.sh がリリース前の状態を読み取り専用で点検する。「コミットして」「commit this」「リリースして」「release」「タグ打って」「バージョン上げて」「publish」などで使う。
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# 安全コミット & リリース スキル

変更内容を確認して選択的にコミットし、必要ならそのままリリースまで運ぶスキルです。
バンドル済みスクリプトを使うため、リポジトリ側に準備は要りません。

`<skill-path>` は、このスキルが展開されているディレクトリを指します。

## ステップ0: リリースまで含むかを最初に確認する（必須）

**他の作業を始める前に、一度だけ**次を確認します。

> 今回はリリースまで含めますか？
> - **No**（既定）: コミットのみ。push もタグもしません。
> - **Yes**: コミット後、バージョン更新 → CHANGELOG → タグ → push → GitHub Release → パッケージ公開まで進めます（各段階で確認します）。

- ユーザーの依頼文で意図が既に明確なとき（「コミットだけして」「リリースまでやって」など）は**聞き直さない**。
- 一度決めたら、そのセッション内で聞き直さない。途中で方針が変わったらユーザーの指示に従う。
- 迷ったら **No 扱い**（コミットのみ）。リリースは外部に出る不可逆な操作なので、暗黙に進めない。

---

# フェーズA: コミット（常に実行）

## A1. 変更内容の確認

```bash
git status --short
git diff --stat
```

## A2. ファイル指定でステージング

```bash
git add [指定ファイル...]
git diff --staged      # 必ず内容を目視確認
```

- `git add -A` / `git add .` は使わない。関連する変更ごとにファイルを列挙する。
- 変更が大きいときは「意味のまとまり」ごとに複数コミットへ分割することを提案する。
- 機密ファイル（`.env`、鍵、認証情報、生成物）が混ざっていないか確認する。

## A3. コミット

```bash
bash <skill-path>/scripts/commit.sh "feat: 新機能追加"
```

リポジトリ側に `scripts/commit.sh` があればそちらを使ってもよい。

### コミットメッセージ規約

```
<type>: <description>

feat     新機能追加
fix      バグ修正
docs     ドキュメント更新
refactor リファクタリング
test     テスト追加・修正
chore    雑務・ビルド周り
```

破壊的変更は `feat!:` のように `!` を付けるか、本文に `BREAKING CHANGE:` を書く。

**ステップ0が No なら、ここで終了**（push しない）。Yes ならフェーズBへ。

---

# フェーズB: リリース（ステップ0が Yes のときだけ）

各段階は**ユーザーの明示的な承認**を得てから実行する。承認なしに次へ進まない。

## B0. プリフライト（読み取り専用）

```bash
bash <skill-path>/scripts/release-preflight.sh            # 現状を点検
bash <skill-path>/scripts/release-preflight.sh --tag v1.2.0   # 予定タグの重複も確認
```

作業ツリーの汚れ、upstream との差分、既存タグ、バージョン記載ファイルと現在値、
CHANGELOG の有無、公開先（npm/PyPI/crates.io 等）、`gh` の認証状態をまとめて出力する。
**BLOCKER が出たら先へ進まず、内容をユーザーに報告して指示を仰ぐ。**

## B1. バージョン決定とファイル更新

1. 前回タグからのコミットを確認する:
   ```bash
   git log $(git describe --tags --abbrev=0 2>/dev/null)..HEAD --oneline
   ```
2. SemVer の上げ幅を**提案**する（`BREAKING CHANGE`/`!` → major、`feat` → minor、それ以外 → patch）。
   最終判断はユーザー。
3. プリフライトが検出したバージョン記載箇所をすべて更新する（例: `package.json`、
   `.claude-plugin/plugin.json`、`pyproject.toml`、`Cargo.toml`、`VERSION`、`__init__.py`）。
   README やドキュメントに版数が書かれていないかも `grep` で確認し、取りこぼさない。
4. CHANGELOG を更新する（形式は `references/release-playbook.md` を参照）。無ければ作成を提案する。
5. `git diff` をユーザーに見せて承認を得てから、`commit.sh` で `chore(release): vX.Y.Z` としてコミットする。

## B2. タグ付与

```bash
git tag -a v1.2.0 -m "v1.2.0"
```

- annotated タグ（`-a`）を使う。タグメッセージにも AI署名を入れない。
- **既存タグの上書き（`-f`）や、push 済みタグの貼り替えはしない。** 間違えたら新しい版を切る。

## B3. push（★外部に出る操作 — 承認必須）

```bash
git push origin <branch>
git push origin v1.2.0
```

- `--force` / `--force-with-lease` は使わない。
- push 前に、何が公開されるか（コミット数・タグ名・対象リモート）をユーザーに提示する。

## B4. GitHub Release（★承認必須）

```bash
gh release create v1.2.0 --title "v1.2.0" --notes-file <notes>
```

- リリースノートは CHANGELOG の該当セクションから作る。ドラフト（`--draft`）で作って確認する運用も可。
- `gh` が未認証／未インストールなら、その旨を伝えて手動手順を案内する（勝手に認証を始めない）。

## B5. パッケージ公開（★承認必須・最も不可逆）

1. まず dry-run を実行して出力をユーザーに見せる:
   ```bash
   npm publish --dry-run          # npm
   python -m build && twine check dist/*   # PyPI
   cargo publish --dry-run        # crates.io
   ```
2. 同梱ファイル一覧・パッケージ名・バージョンを確認してもらう。
3. 明示的な「はい」を得てから本番公開する。エコシステム別の詳細は
   `references/release-playbook.md` を参照。

**公開は取り消せない**（npm unpublish は制限あり、PyPI/crates.io は同一版の再公開不可）。
少しでも不明点があれば止めて確認する。

## B6. 完了報告

実行したこと（版数、タグ、push 先、Release URL、公開先）と、**やらなかったこと**を明示して報告する。

---

## 安全ルール（全フェーズ共通）

- `git add -A` / `git add .` を使わない。
- コミットメッセージ・タグ・リリースノートに AI署名（Co-Authored-By、Generated with 等）を入れない。
- 承認済みの範囲を超えない。「push まで」の承認は「公開」の承認ではない。
- 失敗したコマンドを回避策で強行しない（force push、認証バイパス、`--no-verify` 等）。止めて報告する。
- 汚れた作業ツリーのままタグ付け・公開をしない。
- 機密情報をコミット・公開しない。

## バンドルファイル

| ファイル | 役割 |
|----------|------|
| `scripts/commit.sh` | ステージ済み変更のみをコミット。AI署名を付けない。日英ロケール対応・依存なし。 |
| `scripts/release-preflight.sh` | リリース前状態の読み取り専用点検（tree/upstream/tag/版数記載/CHANGELOG/公開先/gh）。BLOCKER 検出時は終了コード 1。 |
| `references/release-playbook.md` | CHANGELOG 形式、バージョン記載箇所の探し方、エコシステム別の公開手順とロールバック可否。 |
