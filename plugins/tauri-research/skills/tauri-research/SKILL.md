---
name: tauri-research
description: Research assistant that investigates Tauri-related questions via web search, prioritizing official documentation and trusted sources
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Tauri Research Assistant

Investigates Tauri-related unknowns by searching official documentation, GitHub, and community resources. Use this skill when encountering unfamiliar Tauri APIs, undocumented behavior, migration questions, or platform-specific issues.

## When to Use

- Unknown or undocumented Tauri API behavior
- Migration questions (v1 -> v2, or between v2 minor versions)
- Platform-specific issues (macOS, Windows, Linux, iOS, Android)
- Plugin compatibility or configuration questions
- Build/packaging errors with no obvious solution
- Comparing Tauri approaches with alternatives

## Research Flow

### Step 1: Define the Question

Clearly state what needs to be investigated before searching. Break vague questions into specific, searchable sub-questions.

### Step 2: Search Trusted Sources (in priority order)

1. **Official Tauri Documentation** — Most authoritative, always check first
2. **Tauri GitHub Repository** — Issues, discussions, and source code
3. **Tauri Discord / Community Forums** — Community solutions and workarounds
4. **Crates.io / npm Registry** — Plugin versions and compatibility
5. **Developer Blog Posts** — Practical implementation experiences (verify recency)
6. **Stack Overflow** — Check answer dates and vote counts carefully

### Step 3: Validate Findings

- **Version check**: Confirm the information applies to Tauri v2 (not v1)
- **Date check**: Prefer sources from October 2024 or later (v2 stable release)
- **Cross-reference**: Verify critical findings against at least two sources
- **Test feasibility**: Note if the solution is untested or has known caveats

### Step 4: Report Results

Structure findings as:

1. **Answer**: Direct answer to the question
2. **Sources**: URLs with brief description of each source
3. **Confidence Level**: High / Medium / Low with reasoning
4. **Caveats**: Version constraints, platform limitations, known issues
5. **Next Steps**: Suggested actions or further investigation if needed

## Official Resources

| Resource | URL | Use For |
|----------|-----|---------|
| Documentation | https://v2.tauri.app | API reference, guides, configuration |
| GitHub | https://github.com/tauri-apps/tauri | Source code, issues, releases |
| Plugins | https://github.com/tauri-apps/plugins-workspace | Official plugin source and docs |
| Discord | https://discord.com/invite/tauri | Community help, real-time discussion |
| Blog | https://v2.tauri.app/blog | Release notes, announcements |
| Awesome Tauri | https://github.com/tauri-apps/awesome-tauri | Community plugins and examples |

## Search Tips

### Effective Search Queries

- Prefix with `tauri v2` to filter out v1 results
- Include the specific plugin name (e.g., `tauri-plugin-fs scope`)
- Add `site:github.com/tauri-apps` for GitHub-specific searches
- Use `after:2024-10` to filter for post-v2-stable content

### Common Pitfalls

- **v1 vs v2 confusion**: Many search results still reference Tauri v1. The API surface changed significantly — always verify the version
- **Outdated blog posts**: Tauri evolved rapidly during beta. Pre-October 2024 content about v2 may be outdated
- **Platform-specific behavior**: Solutions for one OS may not apply to others. Always note the platform context
- **Plugin version mismatches**: Ensure plugin versions are compatible with the Tauri core version in use

## Reporting Format

When reporting research results, use this template:

```markdown
## Research: [Topic]

**Question:** [What was investigated]

**Answer:**
[Clear, concise answer]

**Sources:**
- [Source 1 title](URL) — [brief note]
- [Source 2 title](URL) — [brief note]

**Confidence:** [High/Medium/Low] — [reason]

**Caveats:**
- [Any limitations or version constraints]

**Suggested Next Steps:**
- [Action items if applicable]
```
