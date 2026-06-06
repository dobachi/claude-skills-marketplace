# Operations reference

All read/review ops are in `review_native.py`; all edits in `edit_native.py`.
Edits mutate only targeted nodes, preview as a unified diff (`--dry-run`), and
abort if they would introduce a dangling reference.

## Read / review (`review_native.py`, read-only)

| Subcommand | Purpose |
|------------|---------|
| `summary MODEL` | header, era, counts by layer/folder, red-flag counts |
| `list MODEL [--layer L] [--type T] [--folder F]` | enumerate concepts |
| `trace MODEL --concept ID\|NAME [--direction in\|out\|both] [--depth N] [--rel TYPE]` | walk relationships ("what serves X") |
| `orphans MODEL` | concepts with no relationships + goals/requirements nothing realizes |
| `violations MODEL [--format text\|json]` | metamodel + integrity check; exit 2 on errors |
| `interpret-view MODEL --view ID\|NAME` | what a view shows (concepts, connections, layers) |

## Edit (`edit_native.py`, in place)

| Subcommand | Mutates | Confirmation |
|------------|---------|--------------|
| `add-concept --type CANON --name N [--folder F] [--doc T]` | one `<element>` in the layer's folder | dry-run |
| `add-rel --type CANON --source ID --target ID [--name N]` | one relationship in `relations`; **validated** against the matrix first (refused if illegal, with allowed alternatives) | dry-run |
| `rename --id ID --name N` | `name` attr of one node | dry-run |
| `set-property --id ID --key K [--value V]` / `remove-property --id ID --key K` | a `<property>` child | dry-run |
| `set-doc --id ID --text T` | the `<documentation>` child | dry-run |
| `add-to-view --view ID --concept ID [--near ID]` | new `DiagramObject` + `<bounds>`; existing bounds untouched | dry-run |
| `delete-concept --id ID [--yes]` | concept + its relationships + referencing diagram objects/connections (**cascade**); strips freed ids from `targetConnections` | needs `--yes` (preview with `--dry-run`) |

Every edit takes `--dry-run` to print the diff without writing. Always dry-run first,
show the user the diff, get confirmation, then apply.

## add-to-view placement

Never moves existing objects. With `--near ID`, places the new object to the right
of that neighbour (`near.x + near.width + 40`, same y). Otherwise drops it on a new
row below everything (`x=24`, `y = maxY + 40`), default size 120×55. To draw
connections too, the relationship's endpoints must both already be in the view.

## delete-concept cascade algorithm

1. Collect the concept's relationships (in + out).
2. Collect its diagram objects (per view).
3. Collect connections whose relationship is being removed **or** whose source/target
   diagram object is being removed.
4. Strip the removed connection ids from any `targetConnections` attribute (delete the
   attribute if it becomes empty).
5. Remove connections, then diagram objects, then relationships, then the concept.
6. Re-parse the result and **abort** if any dangling concept/relationship reference
   remains.

## Stable ids

New ids are fresh 8-hex tokens checked for collision against every id in the file.
Existing ids are never reused or renumbered (round-trip anchor). The minimal-diff
helpers keep 2-space indentation so a one-element edit is a one-line diff.
