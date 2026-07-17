# Skill Authoring Best Practices

Guidelines for creating effective Claude Code skills in this marketplace.

> For the step-by-step procedure to register or update a plugin in this repo (which
> files to touch, how to validate, how to install), see
> [adding-or-updating-a-skill.md](./adding-or-updating-a-skill.md). This document
> covers how to write the skill *content*.

## SKILL.md Structure

Every skill requires a `SKILL.md` file with YAML frontmatter:

```yaml
---
name: skill-name
description: One-line description of what this skill does
---
```

### Frontmatter Rules

- **name**: Lowercase, hyphenated, matches the directory name
- **description**: The primary triggering mechanism — Claude reads it to decide whether to load the skill. Write it in **third person**, and include both *what the skill does* and *when to use it* (trigger phrases, in Japanese and English if the skill is bilingual), plus what it does **not** do and which sibling skill to hand off to.

  **Length.** Two different limits apply, and they are not the same thing:

  | Limit | Applies to | Source |
  |---|---|---|
  | **1,024 characters** max, non-empty, no XML tags | The `description` field, per the Claude **API** Agent Skills docs | [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) |
  | **1,536 characters** | `description` + `when_to_use` **combined**, truncated *in the skill listing* — a display cap, not a field limit. Configurable via `skillListingMaxDescChars` | [Extend Claude with skills](https://code.claude.com/docs/en/skills) |

  Claude Code does not appear to enforce the 1,024 cap: Anthropic's own `claude-api` skill ships a
  1,068-character description and loads fine. Treat 1,024 as the portable ceiling anyway, and stay
  under it unless you have a reason.

  **Practical target: roughly 200–900 characters.** Longer than one line is normal and correct —
  all 17 skills Anthropic ships under `anthropics/skills` exceed 200 characters (shortest: 204;
  longest: 1,068). Anthropic's own `skill-creator` advises making descriptions "a little bit
  *pushy*", because "Claude has a tendency to *undertrigger* skills — to not use them when they'd
  be useful."

  > A previous version of this document specified "Under 200 characters". That rule had no basis in
  > any official source and was contradicted by both Anthropic's practice and this repo's own
  > skills. See [grounded-research-design.md](./grounded-research-design.md#validation-the-skill-was-dogfooded-on-a-live-question)
  > for the investigation. Short, one-line descriptions in older skills here are legacy, not the target.

### Body Structure

After the frontmatter, include:

1. **Language directive** (recommended):
   ```
   > **Language:** Respond in the user's language. If unclear, default to the language of the user's message.
   ```
2. **Title and role statement**: One sentence defining the skill's persona
3. **Core principles or configuration**: Key parameters and standards
4. **Domain-specific sections**: The actual expertise content
5. **Deliverable structure** (optional): What output to produce

## Optimal Size

- **Target: under 500 lines** per SKILL.md
- Existing skills in this project range from ~34 to ~168 lines (average ~100 lines)
- If content exceeds 500 lines, split into a `references/` directory

## Using `references/` Directory

Place detailed reference material in `skills/<skill-name>/references/`:

```
skills/my-skill/
  SKILL.md              # Core guidance (under 500 lines)
  references/
    architecture.md     # Detailed architecture patterns
    security.md         # Security reference
    examples.md         # Code examples
```

Reference files contain supplementary detail that the AI can consult when needed, keeping the main SKILL.md focused and concise.

## Modular vs Monolithic

**Prefer modular (multiple small skills) when:**
- The skill covers distinct use cases triggered at different times
- Different users would want different subsets
- A single SKILL.md would exceed 500 lines even after extracting references

**Keep monolithic (single skill) when:**
- All content is needed together in every invocation
- The topic is naturally cohesive and under 500 lines

## Plugin Directory Structure

```
plugins/<plugin-name>/
  .claude-plugin/
    plugin.json         # Plugin metadata
  skills/
    <skill-name>/
      SKILL.md          # Main skill file
      references/       # Optional supplementary material
```

### plugin.json Format

```json
{
  "name": "plugin-name",
  "description": "Brief description of the plugin.",
  "version": "1.0.0",
  "author": {"name": "dobachi"}
}
```

## Marketplace Registration

Add new plugins to `.claude-plugin/marketplace.json` in the `plugins` array:

```json
{
  "name": "plugin-name",
  "source": "./plugins/plugin-name",
  "description": "Same or similar to plugin.json description."
}
```

## Writing Effective Content

### Do
- Be specific and actionable (provide concrete patterns, not vague advice)
- Include decision criteria (when to use X vs Y)
- Use tables for structured comparisons
- Provide code examples in reference files
- State constraints and targets with numbers

### Don't
- Repeat information available in official documentation
- Include tutorial-level explanations (assume the AI has base knowledge)
- Add filler content or excessive caveats
- Duplicate content between SKILL.md and references

## Testing and Iteration

1. **Syntax check**: Verify YAML frontmatter and JSON files parse correctly
2. **Size check**: Confirm SKILL.md is under 500 lines
3. **Consistency check**: Directory names match `name` fields in frontmatter and plugin.json
4. **Invocation test**: Use the skill in a real conversation to verify it triggers correctly and produces useful output
5. **Iterate**: Refine based on actual usage patterns

## Patterns from This Project

Observations from existing skills:

- Skills that combine "expert persona" + "concrete rules/constraints" + "deliverable format" work best
- Tables are effective for summarizing test strategies, configuration options, etc.
- A clear "Core Principles" section at the top sets the right context quickly
- Listing specific tools/frameworks shows scope without being exhaustive
