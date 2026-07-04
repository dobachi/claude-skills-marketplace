# Adding or Updating a Skill

Operational runbook for registering a new plugin into this marketplace, or updating
an existing one. For guidance on *writing* the skill content itself, see
[skill-authoring-best-practices.md](./skill-authoring-best-practices.md).

Throughout this doc, replace `<name>` with the plugin's kebab-case name (e.g. `doc-refactor`).
The name must be identical in the directory, the `SKILL.md` frontmatter, `plugin.json`,
and `marketplace.json`.

## Target layout

Every plugin follows this structure:

```
plugins/<name>/
  .claude-plugin/
    plugin.json                 # plugin metadata
  skills/
    <name>/
      SKILL.md                  # frontmatter (name, description) + body
      references/               # optional supplementary material
      scripts/                  # optional helper scripts
```

## Adding a new skill

### Path A — importing a packaged `.skill` file

A `.skill` file is a zip archive that usually contains a `<name>/` folder with
`SKILL.md` (plus optional `references/` and `scripts/`).

1. **Extract** to a scratch location and inspect the tree and the `SKILL.md` frontmatter:
   ```bash
   mkdir -p /tmp/skill-extract && cd /tmp/skill-extract
   unzip -o /path/to/<name>.skill
   find . -type f | sort
   ```
2. **Place** the skill payload under the plugin's `skills/<name>/` directory:
   ```bash
   DEST=plugins/<name>/skills/<name>
   mkdir -p "$DEST" plugins/<name>/.claude-plugin
   cp -r /tmp/skill-extract/<name>/. "$DEST"/
   ```
3. Continue with **[Register the plugin](#register-the-plugin)** below.

### Path B — authoring from scratch

1. Create the [target layout](#target-layout) directories.
2. Write `skills/<name>/SKILL.md` following
   [skill-authoring-best-practices.md](./skill-authoring-best-practices.md)
   (frontmatter `name` + `description`, body under ~500 lines, extra detail in `references/`).
3. Continue with **Register the plugin** below.

### Register the plugin

These three registration steps are what make the plugin discoverable and installable.

1. **`plugin.json`** — create `plugins/<name>/.claude-plugin/plugin.json`:
   ```json
   {
     "name": "<name>",
     "description": "One-paragraph description of the plugin.",
     "version": "1.0.0",
     "author": {"name": "dobachi"}
   }
   ```
2. **`marketplace.json`** — add an entry to the `plugins` array in
   `.claude-plugin/marketplace.json` (place it near related plugins):
   ```json
   {
     "name": "<name>",
     "source": "./plugins/<name>",
     "description": "Same or similar to the plugin.json description."
   }
   ```
3. **README tables** — add one row to the matching category table in **both**
   `README.md` (English) and `README_ja.md` (Japanese).

## Updating an existing skill

1. Edit the skill content under `plugins/<name>/skills/<name>/`.
2. **Bump `version`** in `plugins/<name>/.claude-plugin/plugin.json` (semver:
   patch for fixes, minor for new capability, major for breaking changes).
3. If the description or scope changed, update it in **all three** places to keep
   them in sync: `plugin.json`, `marketplace.json`, and both README tables.

## Validate

Run before committing. All JSON must parse and the four `name` occurrences must match.

```bash
# JSON parses and the plugin is registered
python3 -c "import json; d=json.load(open('.claude-plugin/marketplace.json')); \
  assert any(p['name']=='<name>' for p in d['plugins']); print('marketplace OK', len(d['plugins']))"
python3 -c "import json; json.load(open('plugins/<name>/.claude-plugin/plugin.json')); print('plugin.json OK')"

# Files are in place
find plugins/<name> -type f | sort
```

Checklist:
- [ ] Directory name, `SKILL.md` `name`, `plugin.json` `name`, `marketplace.json` `name` all identical
- [ ] `SKILL.md` frontmatter parses and description is meaningful
- [ ] Entry added to `marketplace.json`
- [ ] Row added to **both** `README.md` and `README_ja.md`
- [ ] Any script dependencies documented (stdlib-only needs nothing; otherwise note requirements)

## Install / apply

`install.sh` **auto-discovers** every directory under `plugins/` that has a
`.claude-plugin/plugin.json`, so a newly added plugin needs no change to the script.

```bash
./install.sh          # registers/refreshes the marketplace and installs all plugins
```

Then, in a running Claude Code session, run `/reload-plugins` to apply immediately;
new sessions load the plugins automatically.
