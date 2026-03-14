---
name: reload-and-reset
description: Updates the AI instruction system to the latest version and resets AI behavior to follow instructions
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# AI Instruction Reload & Reset

Updates the AI instruction system to the latest version and corrects AI behavior to properly follow instructions.

## Execution Steps

1. **Save current task state**
   ```bash
   echo "Saving current task state..."
   scripts/checkpoint.sh pending > /tmp/ai_tasks_backup.txt 2>&1 || echo "No task information"
   ```

2. **Update submodule (skip if this is the project itself)**
   ```bash
   if [ -d "instructions/ai_instruction_kits/.git" ]; then
     echo "Updating AI instruction system..."
     git submodule update --remote instructions/ai_instruction_kits
   else
     echo "Running in AI instruction kit dev environment (skipping submodule update)"
   fi
   ```

3. **Verify update status**
   ```bash
   echo "Current instruction system status:"
   if [ -d "instructions/ai_instruction_kits/.git" ]; then
     git submodule status instructions/ai_instruction_kits
   else
     echo "Dev environment: $(git rev-parse --short HEAD)"
   fi
   ```

4. **System reset declaration**
   Reset the AI system with the following procedure:

   ### Reset Complete

   I have now been reset to the following state:
   - Recognized the latest version of the AI instruction system
   - Operating in ROOT_INSTRUCTION-compliant mode
   - Task management system ready
   - Preset-priority instruction selection

   ### Applied Base Rules
   1. **Task management**: Progress tracking using checkpoint.sh
   2. **Instruction selection**: Priority order: Preset > Modular > Legacy
   3. **Work procedure**: Start task > Select instruction > Execute > Report completion
   4. **Path recognition**: Automatic detection of dev vs. submodule environment

5. **Reload ROOT_INSTRUCTION**
   Auto-detect path and load:
   `instructions/ja/system/ROOT_INSTRUCTION.md` or
   `instructions/ai_instruction_kits/instructions/ja/system/ROOT_INSTRUCTION.md`

6. **Check saved task state**
   ```bash
   if [ -f "/tmp/ai_tasks_backup.txt" ]; then
     echo "Saved tasks:"
     cat /tmp/ai_tasks_backup.txt
     rm /tmp/ai_tasks_backup.txt
   fi
   ```

## Usage

```
/reload-and-reset
```

No arguments required. The AI system will be fully reset and will operate according to the latest instructions.

## Effects

- AI behavior is reset to follow instructions
- Latest instruction system is loaded
- Task management system is reinitialized

## Recommended Timing

- When the AI is not following instructions properly
- After long work sessions
- When the instruction system has been updated
- Before starting a new task session
