#!/usr/bin/env python3
"""Score middleware/runtime candidates for a tech-selector decision.

Reads a `criteria.yaml` (schema: references/criteria-schema.md), min-max normalizes
each candidate's raw scores per criterion (respecting direction: max|min), computes
weighted totals and a ranking, then runs a sensitivity pass: it perturbs each
criterion's weight and reports whether the winner flips. A decision whose winner
flips under a small weight change is fragile and should be recorded as such.

Ranking uses the unnormalized weighted sum S = Σ wₖ·nₖ; dividing by Σw is order-
preserving, so the winner is independent of that denominator. The reported total is
normalized to 0..1 (S / Σw) purely for readability.

Usage:
    score.py CRITERIA.yaml [--format text|json]

Exit codes: 0 = scored, 2 = invalid criteria file.
"""

from __future__ import annotations

import argparse
import json
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("PyYAML is required: pip install -r scripts/requirements.txt\n")
    sys.exit(3)

# Weight multipliers applied one-at-a-time in the sensitivity pass. 0.0 = drop the
# criterion entirely; 2.0 = double its influence.
SENSITIVITY_MULTIPLIERS = [0.0, 0.5, 0.75, 1.25, 1.5, 2.0]


def _fail(msg: str):
    sys.stderr.write(f"error: {msg}\n")
    sys.exit(2)


def _text(v) -> str:
    """A criterion/candidate label may be a plain string or a lang-keyed map."""
    if isinstance(v, dict):
        for k in ("en", "ja"):
            if k in v:
                return str(v[k])
        return str(next(iter(v.values()))) if v else ""
    return str(v)


def load_criteria(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    criteria = raw.get("criteria") or []
    candidates = raw.get("candidates") or []
    if not criteria:
        _fail("no `criteria` defined")
    if len(candidates) < 2:
        _fail("need at least 2 `candidates` to compare")

    keys = [c.get("key") for c in criteria]
    if None in keys:
        _fail("every criterion needs a `key`")
    if len(set(keys)) != len(keys):
        _fail("criterion `key`s must be unique")

    for c in criteria:
        w = c.get("weight", 1)
        if not isinstance(w, (int, float)) or w < 0:
            _fail(f"criterion '{c['key']}' weight must be a non-negative number")
        d = c.get("direction", "max")
        if d not in ("max", "min"):
            _fail(f"criterion '{c['key']}' direction must be max|min")

    for cand in candidates:
        if not cand.get("id"):
            _fail("every candidate needs an `id`")
        scores = cand.get("scores") or {}
        missing = [k for k in keys if k not in scores]
        if missing:
            _fail(f"candidate '{cand['id']}' missing scores for: {', '.join(missing)}")
        for k in keys:
            if not isinstance(scores[k], (int, float)):
                _fail(f"candidate '{cand['id']}' score for '{k}' must be numeric")
    return raw


def normalize(criteria: list, candidates: list) -> dict:
    """Per-criterion min-max normalization to 0..1 goodness (higher = better)."""
    norm: dict = {c["id"]: {} for c in candidates}
    for crit in criteria:
        k = crit["key"]
        vals = [cand["scores"][k] for cand in candidates]
        lo, hi = min(vals), max(vals)
        span = hi - lo
        for cand in candidates:
            v = cand["scores"][k]
            if span == 0:
                g = 1.0  # all candidates equal on this axis
            elif crit.get("direction", "max") == "max":
                g = (v - lo) / span
            else:
                g = (hi - v) / span
            norm[cand["id"]][k] = g
    return norm


def weighted_sum(criteria: list, norm: dict, cand_id: str, weight_of=None) -> float:
    weight_of = weight_of or {c["key"]: c.get("weight", 1) for c in criteria}
    return sum(weight_of[c["key"]] * norm[cand_id][c["key"]] for c in criteria)


def rank(criteria: list, candidates: list, norm: dict, weight_of=None):
    scored = [(cand["id"], weighted_sum(criteria, norm, cand["id"], weight_of))
              for cand in candidates]
    scored.sort(key=lambda t: t[1], reverse=True)
    return scored


def sensitivity(criteria: list, candidates: list, norm: dict):
    base = rank(criteria, candidates, norm)
    base_winner = base[0][0]
    total_w = sum(c.get("weight", 1) for c in criteria) or 1.0
    margin = (base[0][1] - base[1][1]) / total_w  # top1 - top2, normalized 0..1

    rows = []
    fragile = False
    for crit in criteria:
        k = crit["key"]
        flips = {}
        for m in SENSITIVITY_MULTIPLIERS:
            w = {c["key"]: c.get("weight", 1) for c in criteria}
            w[k] = crit.get("weight", 1) * m
            winner = rank(criteria, candidates, norm, w)[0][0]
            flips[m] = winner
        flipped = {m: win for m, win in flips.items() if win != base_winner}
        # A flip within ±50% (m in [0.5, 1.5]) marks the decision fragile.
        if any(m in (0.5, 1.5) for m in flipped):
            fragile = True
        rows.append({"key": k, "flips": flips, "flipped": flipped})
    return {"base_winner": base_winner, "margin": margin,
            "fragile": fragile, "rows": rows}


def build_report(raw: dict) -> dict:
    criteria = raw["criteria"]
    candidates = raw["candidates"]
    norm = normalize(criteria, candidates)
    total_w = sum(c.get("weight", 1) for c in criteria) or 1.0
    ranking = rank(criteria, candidates, norm)
    totals = {cid: s / total_w for cid, s in ranking}
    sens = sensitivity(criteria, candidates, norm)
    return {"criteria": criteria, "candidates": candidates, "norm": norm,
            "totals": totals, "ranking": ranking, "sensitivity": sens}


def render_text(raw: dict, rep: dict) -> str:
    criteria, candidates = rep["criteria"], rep["candidates"]
    norm, totals = rep["norm"], rep["totals"]
    dec = raw.get("decision", {}) or {}
    out = []
    title = _text(dec.get("title")) if dec.get("title") else dec.get("id", "decision")
    out.append(f"# Tech selection: {title}")
    if dec.get("target"):
        out.append(f"\nTarget element: `{dec['target']}`  ")
    drivers = dec.get("drivers") or []
    if drivers:
        out.append(f"Driving requirements: {', '.join('`%s`' % d for d in drivers)}")

    # Weighted matrix (normalized goodness × weight shown per cell).
    out.append("\n## Weighted matrix\n")
    header = "| Criterion | Weight | Dir | " + " | ".join(
        _text(c.get("name") or c["id"]) for c in candidates) + " |"
    sep = "|" + "---|" * (3 + len(candidates))
    out.append(header)
    out.append(sep)
    for crit in criteria:
        k = crit["key"]
        cells = []
        for cand in candidates:
            raw_v = cand["scores"][k]
            g = norm[cand["id"]][k]
            cells.append(f"{raw_v:g} ({g:.2f})")
        driver = crit.get("driver")
        name = _text(crit.get("name") or k) + (f" ←`{driver}`" if driver else "")
        out.append(f"| {name} | {crit.get('weight', 1):g} | "
                   f"{crit.get('direction', 'max')} | " + " | ".join(cells) + " |")
    # Totals row.
    tcells = [f"**{totals[cand['id']]:.3f}**" for cand in candidates]
    out.append(f"| **Weighted total (0..1)** |  |  | " + " | ".join(tcells) + " |")
    out.append("\n_Cell = raw score (normalized goodness 0..1)._")

    # Ranking.
    out.append("\n## Ranking\n")
    name_of = {c["id"]: _text(c.get("name") or c["id"]) for c in candidates}
    for i, (cid, _s) in enumerate(rep["ranking"], 1):
        marker = " ← winner" if i == 1 else ""
        out.append(f"{i}. **{name_of[cid]}** — {totals[cid]:.3f}{marker}")

    # Sensitivity.
    sens = rep["sensitivity"]
    out.append("\n## Sensitivity (one-at-a-time weight perturbation)\n")
    out.append(f"Winner: **{name_of[sens['base_winner']]}** · "
               f"top1−top2 margin: {sens['margin']:.3f} · "
               + ("⚠️ **fragile** (winner flips within ±50% of a weight)"
                  if sens["fragile"] else "robust (no flip within ±50%)"))
    out.append("\n| Criterion | ×0 (drop) | ×0.5 | ×1.5 | ×2 | flips? |")
    out.append("|---|---|---|---|---|---|")
    for row in sens["rows"]:
        f = row["flips"]

        def w(m):
            return name_of.get(f[m], f[m]) if f[m] != sens["base_winner"] else "—"
        flag = "yes" if row["flipped"] else "no"
        out.append(f"| {row['key']} | {w(0.0)} | {w(0.5)} | {w(1.5)} | {w(2.0)} | {flag} |")
    out.append("\n_“—” = winner unchanged; a name = the criterion's weight change "
               "hands the win to that candidate._")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Score tech-selector candidates.")
    ap.add_argument("criteria", help="path to criteria.yaml")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    args = ap.parse_args()

    raw = load_criteria(args.criteria)
    rep = build_report(raw)

    if args.format == "json":
        payload = {
            "decision": raw.get("decision", {}),
            "totals": rep["totals"],
            "ranking": [{"id": cid, "total": rep["totals"][cid]} for cid, _ in rep["ranking"]],
            "sensitivity": {
                "base_winner": rep["sensitivity"]["base_winner"],
                "margin": rep["sensitivity"]["margin"],
                "fragile": rep["sensitivity"]["fragile"],
                "rows": rep["sensitivity"]["rows"],
            },
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_text(raw, rep))


if __name__ == "__main__":
    main()
