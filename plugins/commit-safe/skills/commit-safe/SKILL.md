---
name: commit-safe
description: 安全なコミットを支援するスキル。変更内容を確認してから選択的にコミット。大きな変更時にファイル指定コミットを提案、git add -Aの使用を防止。バンドルした commit.sh でAI署名付きコミットを防ぐ。
---

# 安全コミットスキル

変更内容を確認してから、選択的にコミットを行うスキルです。バンドルした `scripts/commit.sh` を使うため、リポジトリ側にスクリプトを用意する必要はありません。

## 自動提案のタイミング

| 状況 | 提案内容 |
|------|----------|
| コード変更後 | 「変更をコミットしますか？」 |
| 複数ファイル変更時 | 「ファイルを選択してコミットしますか？」 |
| git add -A 使用時 | 「ファイルを指定してコミットすることを推奨します」 |

## 実行手順

### 1. 変更内容の確認

```bash
git status --short
git diff --stat
```

### 2. ファイル指定コミット

```bash
# ファイルを指定してステージング
git add [指定ファイル...]

# バンドルされた commit.sh でコミット（AI署名なし）
bash <skill-path>/scripts/commit.sh "コミットメッセージ"
```

`<skill-path>` はこのスキルが展開されているディレクトリです。リポジトリ側に `scripts/commit.sh` があればそちらを使っても構いません。

### 3. コミットメッセージ規約

```
<type>: <description>

- feat: 新機能追加
- fix: バグ修正
- docs: ドキュメント更新
- refactor: リファクタリング
- test: テスト追加・修正
```

## 使用例

```bash
# 特定ファイルのみコミット
git add src/main.py src/utils.py
bash <skill-path>/scripts/commit.sh "feat: 新機能追加"

# ドキュメントのみコミット
git add README.md docs/guide.md
bash <skill-path>/scripts/commit.sh "docs: README更新"
```

## 推奨ワークフロー

1. `git status` で変更を確認
2. 関連する変更をグループ化
3. ファイルを指定してコミット
4. 大きな変更は複数の小さなコミットに分割

## 注意事項

- `git add -A` や `git add .` の使用は避ける
- コミットには `commit.sh` を使用（AI署名防止）
- 機密ファイル（.env, credentials等）をコミットしない
- コミット前に必ず `git diff --staged` で内容を確認

## バンドルスクリプト

| ファイル | 役割 |
|----------|------|
| `scripts/commit.sh` | ステージ済み変更のみをコミット。AIメッセージを付けない。日英ロケール対応・依存なしの自己完結スクリプト。 |
