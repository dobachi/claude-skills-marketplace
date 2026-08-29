#!/usr/bin/env python3
"""design-for-agents の書式検査。

docs/format-spec.md 第9節のチェックリストを機械的に確認する。
標準ライブラリのみで動く。

終了コード:
  0  違反なし
  1  違反あり
  2  検査できない（対象ファイルが無い、下限を割っている）

使い方:
  python3 tools/lint.py            # 既定の検査
  python3 tools/lint.py --vocab    # 用語集の「使わない語」も照合する（警告のみ）
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

TIER_TO_KIND = {"MUST": "normative", "SHOULD": "consensus", "HOUSE": "house"}
PREDICATES = {"exists", "absent", "count", "member", "ratio", "equal"}
APPLIES_TO = {"deck", "slide", "element"}
CHECKS = {"manual", "automated"}
AXES = {"mode", "deck", "element", "constraint"}
SCOPES = {"core", "pptx"}
TOPICS = {
    "type", "color", "layout", "density", "emphasis", "title", "structure",
    "chart", "table", "diagram", "image", "a11y", "master", "source", "file",
    "ornament",
}
BANNED = ["検討", "適切に", "必要に応じて", "バランスを取"]
RANGE_RE = re.compile(r"\d\s*[〜~]\s*\d")

RULE_REQUIRED = [
    "id", "status", "tier", "media", "topic", "statement", "values",
    "not_applicable_when", "source", "done_when",
]
DONE_WHEN_REQUIRED = ["id", "applies_to", "predicate", "statement", "check", "floor"]
PLAYBOOK_REQUIRED = ["id", "axis", "media", "when", "ambiguous_if", "uses_rules"]
ANTIPATTERN_REQUIRED = ["id", "media", "statement", "why_it_appears", "instead", "violates"]

# 下限: 削除によって「違反0件」を達成させないための最小値
FLOOR_RULES = 1
FLOOR_SOURCE_KEYS = 1


# --------------------------------------------------------------------------
# frontmatter の読み取り（本リポジトリが使う YAML の部分集合のみ）
# --------------------------------------------------------------------------

def _strip(value: str):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    if value == "[]":
        return []
    if value.startswith("[") and value.endswith("]"):
        return [_strip(v) for v in value[1:-1].split(",") if v.strip()]
    return value


def _parse(lines: list[str], start: int, indent: int):
    """indent 桁のブロックを読み、(値, 次の行番号) を返す。"""
    i = start
    items: list = []
    mapping: dict = {}
    while i < len(lines):
        raw = lines[i]
        if not raw.strip() or raw.lstrip().startswith("#"):
            i += 1
            continue
        cur = len(raw) - len(raw.lstrip())
        if cur < indent:
            break
        if cur > indent:
            raise ValueError(f"{i + 1} 行目: 予期しない字下げ")
        body = raw.strip()
        if body.startswith("- "):
            entry = body[2:].strip()
            if re.match(r"^[A-Za-z_][\w-]*:", entry):
                key, _, rest = entry.partition(":")
                sub = {key.strip(): _strip(rest)} if rest.strip() else {}
                if not rest.strip():
                    value, i = _parse(lines, i + 1, indent + 2)
                    sub[key.strip()] = value
                    items.append(sub)
                    continue
                i += 1
                nested, i = _parse(lines, i, indent + 2)
                if isinstance(nested, dict):
                    sub.update(nested)
                items.append(sub)
            else:
                items.append(_strip(entry))
                i += 1
            continue
        key, _, rest = body.partition(":")
        key = key.strip()
        if rest.strip():
            mapping[key] = _strip(rest)
            i += 1
        else:
            value, i = _parse(lines, i + 1, indent + 2)
            mapping[key] = value
    return (items if items else mapping), i


def read_frontmatter(path: pathlib.Path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return None, ""
    data, _ = _parse(m.group(1).split("\n"), 0, 0)
    return (data if isinstance(data, dict) else {}), m.group(2)


# --------------------------------------------------------------------------

class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, path, message: str) -> None:
        self.errors.append(f"{path}: {message}")

    def warn(self, path, message: str) -> None:
        self.warnings.append(f"{path}: {message}")


def load_source_keys(report: Report) -> set[str]:
    path = ROOT / "docs" / "sources.md"
    if not path.exists():
        report.error("docs/sources.md", "出典台帳が無い")
        return set()
    return set(re.findall(r"^\| `([a-z0-9-]+)` \|", path.read_text(encoding="utf-8"), re.M))


def check_banned(report: Report, rel: str, fm: dict) -> None:
    flat = json.dumps(fm, ensure_ascii=False)
    for word in BANNED:
        if word in flat:
            report.error(rel, f"禁止語『{word}』が frontmatter にある")


def check_done_when(report: Report, rel: str, entries, owner: str) -> None:
    if not isinstance(entries, list) or not entries:
        report.error(rel, f"{owner}: done_when が1つ以上必要")
        return
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            report.error(rel, "done_when の項目が対応表になっていない")
            continue
        name = entry.get("id", "(id 無し)")
        for field in DONE_WHEN_REQUIRED:
            if not entry.get(field):
                report.error(rel, f"done_when[{name}]: {field} が空")
        if name in seen:
            report.error(rel, f"done_when[{name}]: id が重複している")
        seen.add(name)
        pred = entry.get("predicate")
        if pred and pred not in PREDICATES:
            report.error(rel, f"done_when[{name}]: predicate『{pred}』は6つの述語にない")
        scope = entry.get("applies_to")
        if scope and scope not in APPLIES_TO:
            report.error(rel, f"done_when[{name}]: applies_to『{scope}』が不正")
        check = entry.get("check")
        if check and check not in CHECKS:
            report.error(rel, f"done_when[{name}]: check『{check}』が不正")
        if check == "automated" and not entry.get("detector"):
            report.error(rel, f"done_when[{name}]: automated なのに detector が空")
        statement = entry.get("statement", "")
        for word in ("適切", "十分", "読みやすい", "きれい", "バランス"):
            if word in statement:
                report.error(rel, f"done_when[{name}]: statement に評価語『{word}』がある")


def check_rules(report: Report, source_keys: set[str]) -> set[str]:
    ids: set[str] = set()
    paths = sorted((ROOT / "rules").glob("*.md")) if (ROOT / "rules").exists() else []
    for path in paths:
        rel = f"rules/{path.name}"
        fm, body = read_frontmatter(path)
        if fm is None:
            report.error(rel, "frontmatter が無い")
            continue
        ids.add(path.stem)
        for field in RULE_REQUIRED:
            if field not in fm or (fm[field] == "" and field != "values"):
                report.error(rel, f"必須フィールド {field} が無い、または空")
        if fm.get("id") != path.stem:
            report.error(rel, f"id『{fm.get('id')}』がファイル名と一致しない")
        parts = path.stem.split("-")
        if len(parts) < 3 or parts[0] not in SCOPES:
            report.error(rel, f"ID の scope が {sorted(SCOPES)} にない")
        elif parts[1] not in TOPICS:
            report.error(rel, f"ID の topic『{parts[1]}』が一覧にない")
        if fm.get("topic") and parts[1:2] and fm["topic"] != parts[1]:
            report.error(rel, f"topic『{fm['topic']}』が ID の topic と食い違う")
        if fm.get("status") not in ("active", "deprecated"):
            report.error(rel, f"status『{fm.get('status')}』が不正")
        if fm.get("status") == "deprecated" and not fm.get("superseded_by"):
            report.error(rel, "deprecated なのに superseded_by が無い")
        tier = fm.get("tier")
        source = fm.get("source") if isinstance(fm.get("source"), dict) else {}
        if tier not in TIER_TO_KIND:
            report.error(rel, f"tier『{tier}』が不正")
        elif source.get("kind") != TIER_TO_KIND[tier]:
            report.error(rel, f"tier {tier} と source.kind『{source.get('kind')}』が対応しない")
        key = source.get("key")
        if not key:
            report.error(rel, "source.key が無い")
        elif key not in source_keys:
            report.error(rel, f"source.key『{key}』が docs/sources.md に無い")
        if not source.get("ref"):
            report.error(rel, "source.ref が無い")
        if not fm.get("not_applicable_when"):
            report.error(rel, "not_applicable_when が空（例外が無いなら「なし」と書く）")
        for value in fm.get("values") or []:
            if RANGE_RE.search(str(value)):
                report.error(rel, f"values に範囲がある『{value}』。1つの値に決める")
        check_banned(report, rel, fm)
        check_done_when(report, rel, fm.get("done_when"), "rule")
    return ids


def check_playbooks(report: Report, rule_ids: set[str]) -> None:
    directory = ROOT / "playbooks"
    if not directory.exists():
        return
    for path in sorted(directory.glob("*.md")):
        rel = f"playbooks/{path.name}"
        fm, _ = read_frontmatter(path)
        if fm is None:
            report.error(rel, "frontmatter が無い")
            continue
        for field in PLAYBOOK_REQUIRED:
            if not fm.get(field):
                report.error(rel, f"必須フィールド {field} が無い、または空")
        if fm.get("id") != path.stem:
            report.error(rel, f"id『{fm.get('id')}』がファイル名と一致しない")
        if fm.get("axis") not in AXES:
            report.error(rel, f"axis『{fm.get('axis')}』が不正")
        for ref in fm.get("uses_rules") or []:
            if ref not in rule_ids:
                report.error(rel, f"uses_rules の『{ref}』が rules/ に無い")
        check_banned(report, rel, fm)
        if fm.get("done_when"):
            check_done_when(report, rel, fm["done_when"], "playbook")


def check_antipatterns(report: Report, rule_ids: set[str]) -> None:
    directory = ROOT / "antipatterns"
    if not directory.exists():
        return
    for path in sorted(directory.glob("*.md")):
        if "-" not in path.stem:      # <media>.md は一覧ファイルであってレコードではない
            continue
        rel = f"antipatterns/{path.name}"
        fm, _ = read_frontmatter(path)
        if fm is None:
            report.error(rel, "frontmatter が無い")
            continue
        for field in ANTIPATTERN_REQUIRED:
            if not fm.get(field):
                report.error(rel, f"必須フィールド {field} が無い、または空")
        if fm.get("id") != path.stem:
            report.error(rel, f"id『{fm.get('id')}』がファイル名と一致しない")
        for ref in fm.get("violates") or []:
            if ref not in rule_ids:
                report.error(rel, f"violates の『{ref}』が rules/ に無い")
        check_banned(report, rel, fm)


def check_antipattern_index(report: Report) -> None:
    """各アンチパターンが一覧ファイルに載っているか（転記の取りこぼしを防ぐ）。"""
    directory = ROOT / "antipatterns"
    if not directory.exists():
        return
    for index in sorted(directory.glob("*.md")):
        if "-" in index.stem:         # レコード側は一覧ではない
            continue
        listed = index.read_text(encoding="utf-8")
        rel = index.relative_to(ROOT).as_posix()
        entries = sorted(directory.glob(f"{index.stem}-*.md"))
        if not entries:
            continue
        for entry in entries:
            if f"`{entry.stem}`" not in listed:
                report.error(rel, f"一覧に『{entry.stem}』が載っていない")


def check_cross_references(report: Report, rule_ids: set[str]) -> None:
    """本文中の `<scope>-<topic>-...` 形式の参照が実在するか。

    topic が一覧にあるものだけを ID とみなす。`pptx-build` のような
    スキル名を誤検出しないため。
    """
    pattern = re.compile(r"`((?:core|pptx)-([a-z]+)-[a-z0-9-]+)`")
    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts:
            continue
        rel = path.relative_to(ROOT).as_posix()
        for ref, topic in pattern.findall(path.read_text(encoding="utf-8")):
            if topic in TOPICS and ref not in rule_ids:
                report.error(rel, f"本文が参照する rule『{ref}』が存在しない")


def check_tokens(report: Report) -> None:
    directory = ROOT / "tokens"
    if not directory.exists():
        return
    for path in sorted(directory.glob("*.tokens.json")):
        rel = f"tokens/{path.name}"
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            report.error(rel, f"JSON として読めない: {exc}")


def check_vocabulary(report: Report) -> None:
    """用語集の「使わない語」を照合する。警告のみで終了コードに影響させない。

    2つの誤検出を避ける:
      - それ自体が定義語である語（「テンプレート」「レイアウト」）は除く
      - 定義語の一部として現れる語（「側マージン」の中の「マージン」、
        「主張タイトル」の中の「タイトル」）は数えない
    """
    path = ROOT / "glossary.md"
    if not path.exists():
        report.warn("glossary.md", "用語集が無いので照合できない")
        return
    rows = re.findall(r"^\| ([^|]+) \| [^|]* \| [^|]* \| ([^|]+) \|$",
                      path.read_text(encoding="utf-8"), re.M)
    defined = {term.strip() for term, _ in rows if term.strip() != "用語"}
    banned: dict[str, str] = {}
    for term, avoid in rows:
        term = term.strip()
        if avoid.strip() in ("—", "使わない語", ""):
            continue
        for word in (w.strip() for w in avoid.split("、")):
            # 定義語そのものは禁止語にしない
            if len(word) >= 3 and word not in defined:
                banned.setdefault(word, term)
    # 長い定義語から順に伏せ字にして、部分一致での誤検出を防ぐ
    masks = sorted(defined, key=len, reverse=True)

    targets = list((ROOT / "rules").glob("*.md"))
    for extra in ("playbooks", "antipatterns"):
        if (ROOT / extra).exists():
            targets += list((ROOT / extra).glob("*.md"))
    for target in sorted(targets):
        rel = target.relative_to(ROOT).as_posix()
        text = target.read_text(encoding="utf-8")
        for mask in masks:
            text = text.replace(mask, "\u3000" * len(mask))
        for word, term in banned.items():
            if word in text:
                report.warn(rel, f"用語集が使わないとした『{word}』がある（『{term}』を使う）")


def main() -> int:
    parser = argparse.ArgumentParser(description="design-for-agents の書式検査")
    parser.add_argument("--vocab", action="store_true",
                        help="用語集の「使わない語」も照合する（警告のみ）")
    args = parser.parse_args()

    report = Report()
    source_keys = load_source_keys(report)
    rule_ids = check_rules(report, source_keys)
    check_playbooks(report, rule_ids)
    check_antipatterns(report, rule_ids)
    check_antipattern_index(report)
    check_cross_references(report, rule_ids)
    check_tokens(report)
    if args.vocab:
        check_vocabulary(report)

    print(f"rules {len(rule_ids)} 枚 / 出典台帳 {len(source_keys)} 件", flush=True)

    # 下限: 対象を消して「違反0件」にするのを防ぐ
    if len(rule_ids) < FLOOR_RULES or len(source_keys) < FLOOR_SOURCE_KEYS:
        print(f"下限を割っている（rules >= {FLOOR_RULES}、出典 >= {FLOOR_SOURCE_KEYS} が必要）",
              file=sys.stderr)
        return 2

    for warning in report.warnings:
        print(f"警告 {warning}")
    for error in report.errors:
        print(f"違反 {error}", file=sys.stderr)

    if report.errors:
        print(f"\n違反 {len(report.errors)} 件", file=sys.stderr)
        return 1
    print("違反なし")
    return 0


if __name__ == "__main__":
    sys.exit(main())
