---
name: build
description: Detects and runs the appropriate build command for your project
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Project Build Runner

Runs the appropriate build command based on the project configuration.

## Usage

```
/build [options]
```

## Options

- `--clean` - Run a clean build
- `--watch` - Build in watch mode (if supported)
- `--prod` - Production build
- `--test` - Include tests

## Execution Steps

1. **Detect project type**
   ```bash
   # Check for package.json (Node.js/npm/yarn/pnpm)
   if [ -f "package.json" ]; then
     # Detect package manager
     if [ -f "pnpm-lock.yaml" ]; then
       PM="pnpm"
     elif [ -f "yarn.lock" ]; then
       PM="yarn"
     else
       PM="npm"
     fi
   fi

   # Other project types
   # - Cargo.toml (Rust)
   # - pom.xml (Maven)
   # - build.gradle (Gradle)
   # - Makefile
   # - pyproject.toml (Python)
   # - go.mod (Go)
   ```

2. **Run build command**
   ```bash
   # Node.js project
   $PM run build

   # Rust project
   cargo build --release

   # Python project
   python -m build

   # Go project
   go build

   # If Makefile exists
   make
   ```

3. **Post-build verification**
   - Verify build artifacts exist
   - Check for errors
   - Report success/failure

## Examples

```
/build
/build --clean
/build --prod
/build --test
```

## Project-Specific Configuration

You can specify custom build commands in `CLAUDE.md` or `PROJECT.md`:

```markdown
## Build Configuration
- Build command: `npm run custom-build`
- Test command: `npm run test:all`
- Production build: `npm run build:prod`
```

## Smart Features

1. **Automatic Dependency Installation**
   - Automatically runs `npm install` if `node_modules` is missing
   - Resolves dependencies if `Cargo.lock` is missing

2. **Build Script Detection**
   - Parses the scripts section of package.json
   - Suggests available build commands

3. **Error Handling**
   - Analyzes build errors and suggests solutions
   - Attempts automatic fixes for common issues
