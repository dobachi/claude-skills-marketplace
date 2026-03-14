---
name: checkpoint
description: Checkpoint management for AI instruction systems, tracking task progress
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Checkpoint Execution

Runs the AI instruction system checkpoint script and manages task progress.

## Usage

```
/checkpoint <command> [arguments]
```

## Available Commands

### Task Management
- `start <name> <steps>` - Start a new task (task ID is auto-generated)
- `progress <task-id> <current> <total> <status> <next>` - Report progress (requires: instruction in use)
- `complete <task-id> <result>` - Complete a task (requires: all instructions completed)
- `error <task-id> <message>` - Report an error

### Instruction Management
- `instruction-start <path> <purpose> [task-id]` - Start using an instruction
- `instruction-complete <path> <result> [task-id]` - Complete instruction usage

### Status Check
- `pending` - Show list of incomplete tasks
- `summary <task-id>` - Show detailed task history
- `help` - Show help message

## Execution Steps

1. **Run checkpoint command**
   ```bash
   bash scripts/checkpoint.sh $ARGUMENTS
   ```

2. **Display results**
   - Execution results based on the command
   - Error messages (if applicable)
   - Suggested next actions

## Examples

```
/checkpoint pending
/checkpoint start "Implement new feature" 5
/checkpoint progress TASK-123456-abc123 2 5 "Design complete" "Start implementation"
/checkpoint instruction-start "instructions/ja/presets/web_api_production.md" "REST API development" TASK-123456-abc123
/checkpoint complete TASK-123456-abc123 "Implemented 3 API endpoints"
```

## Notes

- Running without arguments defaults to the `pending` command
- Task IDs are auto-generated when running the `start` command
- The `progress` command can only be run while an instruction is in use
- System instructions are not recommended due to workflow constraints
