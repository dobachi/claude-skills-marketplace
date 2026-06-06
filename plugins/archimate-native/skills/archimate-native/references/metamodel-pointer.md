# Metamodel: copied from `archimate-ea`

`scripts/archimate_metamodel.json` and `scripts/archimate_metamodel.py` in this skill
are **verbatim copies** from the `archimate-ea` skill:

- Canonical source: `plugins/archimate-ea/skills/archimate-ea/scripts/archimate_metamodel.{json,py}`

They hold the canonical ArchiMate 3.2 element catalog, the allowed-relationship
matrix, and the PlantUML macro / xsi maps. This skill consumes them **unchanged** —
all Archi-native vocabulary is translated to canonical names first by
`native_vocab.json` + `native_model.py` (see `vocabulary-map.md`), so the metamodel
never needs to know about Archi.

## Why copy instead of share

Plugins are independent install units; a runtime import across `plugins/*/` is
fragile (paths differ once installed). Copying ~10 KB of static data is the robust
choice.

## Sync obligation

If the canonical metamodel in `archimate-ea` changes (new element types, matrix
fixes), re-copy both files here:

```bash
SRC=plugins/archimate-ea/skills/archimate-ea/scripts
DST=plugins/archimate-native/skills/archimate-native/scripts
cp "$SRC/archimate_metamodel.json" "$DST/archimate_metamodel.json"
cp "$SRC/archimate_metamodel.py"   "$DST/archimate_metamodel.py"
```

The copies are kept byte-identical to the source on purpose, so `diff` detects drift:

```bash
diff "$SRC/archimate_metamodel.json" "$DST/archimate_metamodel.json"   # should be empty
```
