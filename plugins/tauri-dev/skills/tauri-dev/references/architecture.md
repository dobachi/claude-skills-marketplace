# Tauri v2 Architecture Reference

Detailed architecture patterns and code examples for Tauri v2 development.

## Detailed Directory Structure

```
my-app/
  src-tauri/
    src/
      lib.rs                  # App builder setup
      main.rs                 # Entry point: calls tauri::run()
      commands/
        mod.rs                # Re-exports command modules
        file_ops.rs           # File operation commands
        settings.rs           # Settings/config commands
        data.rs               # Data processing commands
      models/
        mod.rs                # Data structures
      errors.rs               # Custom error types
      state.rs                # App state definitions
    capabilities/
      default.json            # Default capability set
      admin.json              # Extended permissions
    icons/                    # App icons (various sizes)
    Cargo.toml
    tauri.conf.json
    build.rs                  # Tauri build script
  src/                        # Frontend
    App.tsx                   # (or .vue, .svelte)
    components/
    lib/
      commands.ts             # Typed invoke wrappers
    styles/
  package.json
  vite.config.ts              # (or equivalent bundler config)
```

## Command Implementation Patterns

### Module Organization

```rust
// src/commands/mod.rs
mod file_ops;
mod settings;

pub use file_ops::*;
pub use settings::*;
```

```rust
// src/commands/file_ops.rs
use crate::errors::AppError;

#[tauri::command]
pub fn read_file(path: String) -> Result<String, AppError> {
    std::fs::read_to_string(&path).map_err(AppError::from)
}

#[tauri::command]
pub fn write_file(path: String, content: String) -> Result<(), AppError> {
    std::fs::write(&path, &content).map_err(AppError::from)
}
```

### Typed Frontend Wrappers

Create typed wrappers in TypeScript to catch errors early:

```typescript
// src/lib/commands.ts
import { invoke } from '@tauri-apps/api/core';

export async function readFile(path: string): Promise<string> {
  return invoke<string>('read_file', { path });
}

export async function writeFile(path: string, content: string): Promise<void> {
  return invoke<void>('write_file', { path, content });
}

export interface Settings {
  theme: 'light' | 'dark';
  language: string;
}

export async function getSettings(): Promise<Settings> {
  return invoke<Settings>('get_settings');
}
```

## State Management Patterns

### Single Mutable State

```rust
use std::sync::Mutex;
use serde::{Deserialize, Serialize};

#[derive(Default, Serialize, Deserialize)]
pub struct AppConfig {
    pub theme: String,
    pub language: String,
}

pub struct ConfigState(pub Mutex<AppConfig>);

#[tauri::command]
pub fn get_config(state: tauri::State<'_, ConfigState>) -> AppConfig {
    state.0.lock().unwrap().clone()
}

#[tauri::command]
pub fn set_theme(theme: String, state: tauri::State<'_, ConfigState>) -> Result<(), String> {
    state.0.lock().unwrap().theme = theme;
    Ok(())
}
```

### Read-Heavy State with RwLock

```rust
use std::sync::RwLock;
use std::collections::HashMap;

pub struct CacheState(pub RwLock<HashMap<String, String>>);

#[tauri::command]
pub fn cache_get(key: String, state: tauri::State<'_, CacheState>) -> Option<String> {
    state.0.read().unwrap().get(&key).cloned()
}

#[tauri::command]
pub fn cache_set(key: String, value: String, state: tauri::State<'_, CacheState>) {
    state.0.write().unwrap().insert(key, value);
}
```

### Database-Backed State

```rust
use tauri_plugin_sql::{Migration, MigrationKind};

// Register in lib.rs:
// .plugin(
//     tauri_plugin_sql::Builder::default()
//         .add_migrations("sqlite:app.db", vec![
//             Migration {
//                 version: 1,
//                 description: "create tables",
//                 sql: "CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT NOT NULL);",
//                 kind: MigrationKind::Up,
//             }
//         ])
//         .build()
// )
```

## Plugin Usage Guide

### Registering Plugins

```rust
// src/lib.rs
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_store::Builder::new().build())
        .invoke_handler(tauri::generate_handler![
            commands::read_file,
            commands::write_file,
        ])
        .run(tauri::generate_context!())
        .expect("error running tauri app");
}
```

### Using Store Plugin for Persistence

```typescript
import { Store } from '@tauri-apps/plugin-store';

const store = await Store.load('settings.json');
await store.set('theme', 'dark');
await store.save();

const theme = await store.get<string>('theme');
```

## Multi-Window Management

### Creating Windows

```rust
use tauri::{Manager, WebviewUrl, WebviewWindowBuilder};

#[tauri::command]
async fn open_settings(app: tauri::AppHandle) -> Result<(), String> {
    WebviewWindowBuilder::new(
        &app,
        "settings",
        WebviewUrl::App("settings.html".into()),
    )
    .title("Settings")
    .inner_size(600.0, 400.0)
    .build()
    .map_err(|e| e.to_string())?;
    Ok(())
}
```

### Cross-Window Communication via Events

```rust
// Emit from backend to all windows
app.emit("data-updated", payload)?;

// Emit to a specific window
app.get_webview_window("main").unwrap().emit("refresh", ())?;
```

```typescript
// Listen in frontend
import { listen } from '@tauri-apps/api/event';

const unlisten = await listen<string>('data-updated', (event) => {
  console.log('Data updated:', event.payload);
});
```

## Performance Optimization

### Cargo.toml Release Profile

```toml
[profile.release]
lto = true          # Link-Time Optimization (smaller binary)
opt-level = "s"     # Optimize for size ("z" for even smaller)
strip = true        # Strip debug symbols
codegen-units = 1   # Better optimization, slower compile
panic = "abort"     # Smaller binary, no unwinding
```

### Frontend Bundle Optimization

- Use code splitting to reduce initial load
- Lazy-load routes and heavy components
- Minimize JS bundle size (tree-shaking, minification)
- Prefer CSS over JavaScript for animations

### IPC Performance Tips

- Batch related data into single commands instead of multiple small calls
- Use events for one-way notifications (lower overhead than commands)
- For large data transfers, consider writing to a temp file and passing the path
- Avoid sending large binary data through IPC; use `tauri-plugin-fs` paths instead

## Event System Patterns

### Progress Reporting

```rust
use tauri::Emitter;

#[tauri::command]
async fn process_files(app: tauri::AppHandle, paths: Vec<String>) -> Result<(), AppError> {
    let total = paths.len();
    for (i, path) in paths.iter().enumerate() {
        // Process file...
        app.emit("progress", (i + 1, total))?;
    }
    Ok(())
}
```

### Backend-Initiated Events

```rust
// In a background thread or async task
use tauri::Emitter;

std::thread::spawn(move || {
    loop {
        std::thread::sleep(std::time::Duration::from_secs(60));
        app_handle.emit("health-check", "ok").unwrap();
    }
});
```
