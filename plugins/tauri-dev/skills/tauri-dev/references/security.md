# Tauri v2 Security Reference

Detailed security configuration and best practices for Tauri v2 applications.

## Capabilities / ACL System

Tauri v2 uses a capabilities-based permission system that replaces v1's allowlist. Every command and plugin API is denied by default and must be explicitly permitted.

### Capability File Structure

```json
// src-tauri/capabilities/default.json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "default",
  "description": "Default permissions for the main window",
  "windows": ["main"],
  "permissions": [
    "core:default",
    "shell:allow-open",
    "dialog:allow-open",
    "dialog:allow-save",
    "fs:allow-read-text-file",
    {
      "identifier": "fs:allow-write-text-file",
      "allow": [
        { "path": "$APPDATA/**" }
      ]
    }
  ]
}
```

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Capability** | A named set of permissions assigned to specific windows |
| **Permission** | An allow/deny rule for a specific command or plugin API |
| **Scope** | Restricts a permission to specific resources (paths, URLs, etc.) |

### Permission Naming Convention

```
<plugin>:allow-<command>    # Allow a specific command
<plugin>:deny-<command>     # Explicitly deny a command
<plugin>:default            # Plugin's default permission set
core:default                # Core Tauri default permissions
```

### Scoped Permissions

Restrict file system access to specific directories:

```json
{
  "identifier": "fs:allow-read-text-file",
  "allow": [
    { "path": "$APPDATA/**" },
    { "path": "$RESOURCE/**" }
  ],
  "deny": [
    { "path": "$APPDATA/secrets/**" }
  ]
}
```

### Path Variables

| Variable | Description |
|----------|-------------|
| `$APPDATA` | App-specific data directory |
| `$APPCONFIG` | App-specific config directory |
| `$APPLOCALDATA` | App-specific local data directory |
| `$RESOURCE` | App resource directory (bundled files) |
| `$HOME` | User's home directory |
| `$DESKTOP` | User's desktop directory |
| `$DOCUMENT` | User's documents directory |
| `$DOWNLOAD` | User's downloads directory |
| `$TEMP` | System temp directory |

### Per-Window Capabilities

Assign different permission sets to different windows:

```json
// capabilities/settings.json
{
  "identifier": "settings-window",
  "description": "Limited permissions for settings window",
  "windows": ["settings"],
  "permissions": [
    "core:default",
    "store:allow-get",
    "store:allow-set"
  ]
}
```

## Content Security Policy (CSP)

### Configuration in tauri.conf.json

```json
{
  "app": {
    "security": {
      "csp": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' asset: https://asset.localhost; connect-src ipc: http://ipc.localhost"
    }
  }
}
```

### CSP Guidelines

| Directive | Recommended Value | Notes |
|-----------|-------------------|-------|
| `default-src` | `'self'` | Fallback for unspecified directives |
| `script-src` | `'self'` | Never use `'unsafe-eval'` in production |
| `style-src` | `'self' 'unsafe-inline'` | `unsafe-inline` often needed for CSS-in-JS |
| `img-src` | `'self' asset: https://asset.localhost` | For bundled assets |
| `connect-src` | `ipc: http://ipc.localhost` | Required for Tauri IPC |
| `font-src` | `'self' data:` | For bundled fonts |

### Common Pitfalls

- **`unsafe-eval`**: Never enable in production. If a library requires it, find an alternative
- **Wildcard `*`**: Avoid broad wildcards; be as specific as possible
- **External CDN**: Avoid loading scripts from CDNs; bundle dependencies instead
- **Dev vs Prod**: Use a stricter CSP for production than development

## File System Access Security

### Scoped Access Pattern

Always scope file system access to the minimum required directories:

```json
{
  "permissions": [
    {
      "identifier": "fs:allow-read-text-file",
      "allow": [{ "path": "$APPDATA/projects/**" }]
    },
    {
      "identifier": "fs:allow-write-text-file",
      "allow": [{ "path": "$APPDATA/projects/**" }],
      "deny": [{ "path": "**.exe" }, { "path": "**.sh" }]
    }
  ]
}
```

### Path Traversal Prevention

In Rust commands, always validate and canonicalize paths:

```rust
use std::path::{Path, PathBuf};

fn validate_path(base: &Path, requested: &str) -> Result<PathBuf, AppError> {
    let full_path = base.join(requested).canonicalize()?;
    if !full_path.starts_with(base) {
        return Err(AppError::SecurityViolation("Path traversal detected".into()));
    }
    Ok(full_path)
}
```

## Code Signing

### macOS

1. Obtain an Apple Developer certificate (Developer ID Application)
2. Set environment variables:
   ```bash
   export APPLE_SIGNING_IDENTITY="Developer ID Application: Your Name (TEAMID)"
   export APPLE_ID="your@email.com"
   export APPLE_PASSWORD="app-specific-password"
   export APPLE_TEAM_ID="TEAMID"
   ```
3. Configure in `tauri.conf.json`:
   ```json
   {
     "bundle": {
       "macOS": {
         "signingIdentity": null,
         "entitlements": null
       }
     }
   }
   ```
4. Tauri handles notarization automatically when credentials are set

### Windows

1. Obtain a code signing certificate (EV certificate recommended for SmartScreen reputation)
2. Set environment variables:
   ```bash
   export TAURI_SIGNING_PRIVATE_KEY="path/to/private-key"
   export TAURI_SIGNING_PRIVATE_KEY_PASSWORD="password"
   ```
3. For EV certificates, use `signtool.exe` with the certificate

### Linux

- Linux packages are typically signed via the package manager's signing mechanism
- For AppImage, use `appimagetool --sign`

## Input Validation in Commands

### Strong Typing Pattern

Prefer enums and newtypes over raw strings:

```rust
#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
enum SortOrder {
    Ascending,
    Descending,
}

#[derive(Deserialize)]
struct QueryParams {
    search: String,
    sort: SortOrder,
    #[serde(default = "default_limit")]
    limit: u32,
}

fn default_limit() -> u32 { 50 }

#[tauri::command]
fn search_items(params: QueryParams) -> Result<Vec<Item>, AppError> {
    if params.limit > 1000 {
        return Err(AppError::Validation("limit must be <= 1000".into()));
    }
    // ...
}
```

### Sanitization Checklist

- Validate string lengths (prevent memory exhaustion)
- Check numeric ranges (prevent overflow)
- Sanitize file paths (prevent traversal)
- Validate URLs before making HTTP requests
- Never pass user input directly to shell commands
