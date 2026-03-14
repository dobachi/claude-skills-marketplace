---
name: reload-instructions
description: Updates AI instruction submodules to the latest version and reloads ROOT_INSTRUCTION
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Instruction System Reload

Updates the AI instruction system to the latest version and reloads ROOT_INSTRUCTION.

## Execution Steps

1. **Update submodule**
   ```bash
   git submodule update --remote instructions/ai_instruction_kits
   ```

2. **Verify update**
   ```bash
   echo "AI instruction system updated"
   git submodule status instructions/ai_instruction_kits
   ```

3. **Load ROOT_INSTRUCTION**
   Loads `instructions/ai_instruction_kits/instructions/ja/system/ROOT_INSTRUCTION.md`.

## Usage

```
/reload-instructions
```

No arguments required. Fetches the latest AI instruction system and displays the ROOT_INSTRUCTION content.
