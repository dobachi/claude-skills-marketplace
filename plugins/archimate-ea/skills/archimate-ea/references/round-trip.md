# Round-trip: merging Archi edits back into the YAML

The YAML running model is the source of truth and generate-forwards to Open
Exchange XML. When the user edits the model in **Archi**, `ingest_archi_xml.py`
brings those edits back into `ea-model.yaml` — keyed on stable ids, comment-
preserving, non-destructive by default.

## Workflow

1. Emit XML and import into Archi (`emit_archimate_xml.py` → Archi *File → Import →
   Open Exchange File*). Run Archi's auto-layout.
2. The user edits in Archi (adds/renames elements, draws relationships, changes
   properties, rearranges views).
3. In Archi: *File → Export → Open Exchange File* → `model.xml`.
4. Ingest:
   ```bash
   python3 scripts/ingest_archi_xml.py ea-model.yaml --xml model.xml --dry-run   # preview the change report
   python3 scripts/ingest_archi_xml.py ea-model.yaml --xml model.xml             # merge & write
   python3 scripts/ingest_archi_xml.py ea-model.yaml --xml model.xml --prune     # also delete items absent in Archi
   ```
5. Re-validate (`validate_model.py`) — the ingest runs it automatically unless
   `--no-validate`.

## What is and isn't recovered

| Recovered from XML | Not recovered |
|--------------------|---------------|
| New / renamed / retyped elements & relationships | Diagram **geometry** (positions, bendpoints, colours) — YAML stores logical view membership only |
| name & documentation (all languages) | Influence `strength` (not in the Exchange schema) — **preserved** from existing YAML |
| properties (values), propertyDefinitions | `version`, `viewpoint`, and any YAML-only keys — **preserved** |
| Access `accessType`, Association `isDirected` | YAML comments/formatting are preserved by ruamel, but heavy manual column-alignment may be normalized on write |
| Organizations, view membership (which elements/relationships appear) | |

## Matching by id (the `xml_id` caveat)

The emitter sanitizes ids for XML (`xml_id`: non-`[\w.\-]` → `_`, prefix `id_` if
needed). That function is not invertible in general, so the ingest does **not**
invert it — it builds the finite map `{xml_id(yaml_id): yaml_id}` from *this* model
and matches XML identifiers back through it. Consequences:

- Keep ids **NCName-clean** (kebab-case, start with a letter) so they pass through
  `xml_id` unchanged and round-trip cleanly. The validator already warns on bad ids.
- If two YAML ids sanitize to the same XML id, the ingest reports a **collision** and
  skips those (ambiguous) — disambiguate the ids.
- Items **new in Archi** (no matching id) are added with their Archi id verbatim as
  the new YAML id (Archi ids are hex and id-valid).

## Non-destructive default & `--prune`

By default, items present in the YAML but absent from the XML are **reported, not
deleted** ("REMOVED? … use --prune"). This avoids data loss when the user exported a
partial model. `--prune` deletes them and cascades: dependent relationships are
removed and the ids are scrubbed from every view and organization.

## Idempotency

`YAML → emit_archimate_xml → ingest` with no Archi edits makes **no changes** (the
ingest detects zero changes and does not rewrite the file). What protects this:
single-`en` property values are unwrapped back to scalars; name/documentation are
compared by content (scalar vs lang-map) and only updated per-language; `accessType`
and `isDirected` absences are treated as "unchanged"; `strength`/`version`/
`viewpoint`/unknown keys are never touched.
