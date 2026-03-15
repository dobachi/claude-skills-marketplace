---
name: tauri-dev
description: Development expert for designing and building Tauri v2 desktop and mobile applications with Rust backend and WebView frontend
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Tauri Development Expert

As a Tauri v2 development expert, designs and implements high-quality desktop and mobile applications using the Tauri framework.

## Core Principles

- **Tauri Version**: v2 (stable, released October 2024)
- **Architecture**: Rust backend (core process) + WebView frontend (webview process)
- **Security Level**: High (capabilities-based permission system)
- **Target Platforms**: Windows, macOS, Linux, iOS, Android
- **Frontend**: Framework-agnostic (React, Vue, Svelte, Solid, vanilla)

## Architecture Overview

Tauri apps consist of two processes:

| Process | Language | Role |
|---------|----------|------|
| **Core** | Rust | System access, business logic, commands, plugins |
| **WebView** | JS/TS + HTML/CSS | UI rendering, user interaction |

Communication between processes uses IPC (Inter-Process Communication) via commands and events.

## Project Structure Best Practices

```
my-app/
  src-tauri/
    src/
      lib.rs          # App setup, plugin registration
      main.rs         # Entry point (calls lib)
      commands/        # Command modules
    capabilities/      # Permission definitions (JSON)
    Cargo.toml
    tauri.conf.json    # App configuration
  src/                 # Frontend source
  package.json
```

- Organize Rust commands into modules by domain (e.g., `commands/file_ops.rs`, `commands/settings.rs`)
- Keep `lib.rs` focused on app builder setup and plugin registration
- Use `tauri.conf.json` for app metadata, window config, and bundle settings

## Command Design

### Basic Pattern

```rust
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}
```

### Error Handling

Always return `Result` for commands that can fail:

```rust
#[derive(Debug, thiserror::Error)]
enum AppError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    #[error("Not found: {0}")]
    NotFound(String),
}

impl serde::Serialize for AppError {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where S: serde::Serializer {
        serializer.serialize_str(self.to_string().as_str())
    }
}

#[tauri::command]
fn read_data(path: String) -> Result<String, AppError> {
    std::fs::read_to_string(&path).map_err(AppError::from)
}
```

### Async Commands

Use `async` for I/O-bound operations:

```rust
#[tauri::command]
async fn fetch_data(url: String) -> Result<String, AppError> {
    let response = reqwest::get(&url).await?.text().await?;
    Ok(response)
}
```

## State Management

Use `manage()` to share state across commands:

```rust
use std::sync::Mutex;
use tauri::State;

struct AppState {
    counter: Mutex<i32>,
}

#[tauri::command]
fn increment(state: State<'_, AppState>) -> i32 {
    let mut counter = state.counter.lock().unwrap();
    *counter += 1;
    *counter
}

// In lib.rs setup:
// app.manage(AppState { counter: Mutex::new(0) });
```

- Use `Mutex<T>` for mutable shared state
- Use `RwLock<T>` when reads greatly outnumber writes
- Keep state structs focused; prefer multiple small states over one large one

## IPC Design: Commands vs Events

| Mechanism | Direction | Use When |
|-----------|-----------|----------|
| **Commands** | Frontend -> Backend (request/response) | CRUD operations, data fetching, actions with return values |
| **Events** | Any direction (fire-and-forget) | Notifications, progress updates, background task status, cross-window communication |

## Security Requirements

### Capabilities / ACL (v2)

- **Principle of least privilege**: Only grant permissions the app actually needs
- Define capabilities in `src-tauri/capabilities/*.json`
- Each capability specifies allowed commands and scoped permissions
- Default deny: commands are inaccessible unless explicitly permitted

### Content Security Policy (CSP)

Configure in `tauri.conf.json`:
- Restrict `script-src`, `style-src`, `connect-src` to trusted origins
- Never use `unsafe-eval` in production
- Allow `ipc:` scheme for Tauri IPC

### Input Validation

- Validate all data received from the frontend in Rust commands
- Use strong types (enums, newtypes) instead of raw strings where possible
- Sanitize file paths to prevent directory traversal

## Frontend Integration

Register commands in `lib.rs`:

```rust
tauri::Builder::default()
    .plugin(tauri_plugin_shell::init())
    .invoke_handler(tauri::generate_handler![greet, read_data, increment])
    .manage(AppState { counter: Mutex::new(0) })
    .run(tauri::generate_context!())
    .expect("error running tauri app");
```

Call from frontend (any framework):

```typescript
import { invoke } from '@tauri-apps/api/core';

const result = await invoke<string>('greet', { name: 'World' });
```

## Testing Strategy

| Test Type | Scope | Tools |
|-----------|-------|-------|
| **Rust Unit** | Command logic, state management | `cargo test`, standard Rust testing |
| **Frontend Unit** | UI components, store logic | Vitest, Jest, Testing Library |
| **Integration** | Command invocation, IPC flow | `tauri::test` utilities |
| **E2E** | Full app behavior | WebDriver (via `tauri-driver`) |

- Test Rust commands as pure functions by extracting logic from the `#[tauri::command]` wrapper
- Mock `State<T>` in unit tests using Tauri's test utilities
- Use `tauri::test::mock_builder()` for integration tests

## Build and Distribution

### Release Build

```bash
cargo tauri build
```

- Configure release profile in `Cargo.toml` for size optimization:
  ```toml
  [profile.release]
  lto = true
  opt-level = "s"
  strip = true
  ```

### Code Signing

- **macOS**: Requires Apple Developer certificate and notarization
- **Windows**: Requires code signing certificate (EV recommended for SmartScreen)
- Configure signing in `tauri.conf.json` under `bundle`

### Auto-Updater

- Use `tauri-plugin-updater` for in-app updates
- Requires a static update endpoint serving JSON manifest
- Supports differential updates

## Key Plugins (v2)

Most v2 functionality is provided via plugins:

| Plugin | Purpose |
|--------|---------|
| `tauri-plugin-shell` | Execute external commands |
| `tauri-plugin-fs` | File system access (scoped) |
| `tauri-plugin-dialog` | Native file/message dialogs |
| `tauri-plugin-store` | Persistent key-value storage |
| `tauri-plugin-updater` | Auto-update mechanism |
| `tauri-plugin-notification` | System notifications |
| `tauri-plugin-http` | HTTP client |
| `tauri-plugin-sql` | SQLite/MySQL/PostgreSQL access |

Register plugins in `lib.rs` via `.plugin()` and grant permissions in capabilities.
