# リリース プレイブック

`commit-safe` のフェーズB（リリース）で参照する詳細手順。SKILL.md 本体は流れとゲートだけを持ち、
エコシステム固有の細部はここに置く。

## バージョンの決め方（SemVer）

前回タグからのコミットを見て**提案**し、最終判断はユーザーに委ねる。

| コミットに含まれるもの | 上げ幅 | 例 |
|---|---|---|
| `BREAKING CHANGE:` / `feat!:` / `fix!:` | major | 1.4.2 → 2.0.0 |
| `feat:` | minor | 1.4.2 → 1.5.0 |
| `fix:` / `docs:` / `refactor:` / `chore:` のみ | patch | 1.4.2 → 1.4.3 |

```bash
LAST=$(git describe --tags --abbrev=0 2>/dev/null)
git log ${LAST:+$LAST..}HEAD --oneline
```

0.x 系は破壊的変更でも minor に留める運用が一般的。既存の履歴（`git tag --sort=-v:refname | head`）に合わせる。

## バージョン記載箇所を取りこぼさない

`release-preflight.sh` が主要なファイルを検出するが、ドキュメントやサンプルに版数が
埋まっていることがある。旧版数で grep して確認する。

```bash
OLD=1.4.2
git grep -n --fixed-strings "$OLD" -- . ':!CHANGELOG.md' ':!*.lock'
```

よくある記載箇所:

| ファイル | 記法 |
|---|---|
| `package.json` / `composer.json` | `"version": "X.Y.Z"` |
| `.claude-plugin/plugin.json` | `"version": "X.Y.Z"` |
| `pyproject.toml` | `version = "X.Y.Z"`（`[project]` または `[tool.poetry]`） |
| `Cargo.toml` | `[package]` の `version = "X.Y.Z"` |
| `VERSION` | 版数のみ1行 |
| `src/<pkg>/__init__.py` | `__version__ = "X.Y.Z"` |
| `gradle.properties` | `version=X.Y.Z` |
| README / docs / インストール手順 | 埋め込みの版数・タグ名 |

lock ファイル（`package-lock.json`、`Cargo.lock` 等）は手で書かず、各ツールで再生成する。

## CHANGELOG

[Keep a Changelog](https://keepachangelog.com/) 形式を既定とする。既存ファイルがあれば**その形式に合わせる**。

```markdown
## [1.5.0] - 2026-08-11

### Added
- 新機能の説明

### Changed
- 変更点

### Fixed
- 修正点

### Removed / Deprecated / Security
- 必要な場合のみ
```

- 日付はリリース日（`date +%F`）。
- 「利用者から見て何が変わるか」を書く。内部リファクタは省いてよい。
- コミットメッセージの丸写しではなく、まとめ直す。

## タグ

```bash
git tag -a v1.5.0 -m "v1.5.0"
git tag -n1 v1.5.0        # 確認
git push origin v1.5.0
```

- 既存タグの `-f` 上書き、push 済みタグの削除・貼り替えはしない。誤ったら次の版を切る。
- 命名は既存履歴に合わせる（`v` 接頭辞の有無、モノレポなら `pkg-name@1.5.0` など）。

## GitHub Release

```bash
# CHANGELOG の該当セクションをノートにする
gh release create v1.5.0 --title "v1.5.0" --notes-file /tmp/notes.md

# 自動生成ノートを使う場合
gh release create v1.5.0 --generate-notes

# まず下書きで確認したい場合
gh release create v1.5.0 --draft --notes-file /tmp/notes.md
```

- ビルド成果物を添付するなら `gh release upload v1.5.0 dist/*`。
- `gh` 未認証なら、そこで止めてユーザーに `gh auth login` を促す（代理で認証を進めない）。
- 事前リリースは `--prerelease`（タグも `v1.5.0-rc.1` のように付ける）。

## パッケージ公開（★不可逆）

必ず dry-run → 内容確認 → ユーザーの明示的な承認 → 本番公開の順。

### npm

```bash
npm publish --dry-run          # 同梱ファイル一覧・名前・版数を確認
npm publish                    # 公開（scoped で公開したいなら --access public）
```

- `"private": true` なら公開されない。意図的に公開するなら外す判断をユーザーに確認する。
- 取り消し: 公開後72時間以内かつ条件を満たす場合のみ `npm unpublish`。以後は `npm deprecate` のみ。

### PyPI

```bash
rm -rf dist && python -m build
twine check dist/*
twine upload --repository testpypi dist/*   # 任意: TestPyPI で先に確認
twine upload dist/*
```

- 同一バージョンの再アップロードは不可。ミスは次のパッチ版で直す。
- 認証は API トークン（`~/.pypirc` または `TWINE_*` 環境変数）。トークンを画面に出さない。

### crates.io

```bash
cargo publish --dry-run
cargo publish
```

- 一度公開した版は取り消せない（`cargo yank` は新規利用を止めるだけ）。

### Go モジュール

タグを push すれば公開される。追加コマンドは不要。`v2` 以降はモジュールパスに `/v2` が必要。

### コンテナイメージ

```bash
docker build -t <registry>/<image>:1.5.0 .
docker push <registry>/<image>:1.5.0
docker push <registry>/<image>:latest     # latest を動かすかは要確認
```

## 失敗したときの扱い

| 状況 | 対応 |
|---|---|
| push が rejected | force しない。`git pull --rebase` の可否をユーザーに確認する |
| タグを間違えて push した | 貼り替えず、正しい版を新しく切る（既に取得済みの利用者を壊さない） |
| CI が失敗した | 修正 → 新しいパッチ版。公開済みなら告知も検討 |
| 公開後に不備が判明 | npm: `deprecate` / crates.io: `yank` / PyPI: 該当版を削除せず次版で修正 |

## 完了報告のテンプレート

```
リリース完了: v1.5.0
- バージョン更新: package.json, README.md
- CHANGELOG: 1.5.0 セクション追加
- タグ: v1.5.0（origin へ push 済み）
- GitHub Release: https://github.com/<owner>/<repo>/releases/tag/v1.5.0
- パッケージ公開: npm <name>@1.5.0
未実施: (例) TestPyPI での確認、latest タグの更新
```
