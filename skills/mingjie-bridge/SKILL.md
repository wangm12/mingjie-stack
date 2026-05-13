---
name: mingjie-bridge
description: Use when coordinating Codex and Claude Code through the Mingjie Stack agent bridge, especially inside tmux panes or when asking one agent to review, plan, or respond to the other.
---

# Mingjie Bridge

Purpose: coordinate agents through an explicit user-level bridge instead of scraping terminal panes.

The bridge is user-level and tmux-session scoped:

```text
~/.mingjie-stack/agent-bridge/sessions/<tmux-session>/
  messages.jsonl
  artifacts/
```

Each message includes the current working directory, inferred project root, relevant files, sender, recipient, subject, body, and thread id.

## Agent Rules

- Use the bridge only when the user asks for cross-agent coordination or when a task explicitly mentions Codex, Claude, tmux panes, or the bridge.
- Treat bridge replies as advice until verified locally.
- Do not assume the other agent saw terminal output, diffs, browser state, or conversation context. Put the needed context in the message.
- Do not create infinite loops. One request and one reply is the default; ask the user before starting another round.
- Do not ask the other agent to edit files unless the user explicitly assigned ownership.
- When files are relevant, include short paths and a precise requested action.
- If the MCP tool is unavailable, use the CLI fallback from this repo.

## MCP Tools

Preferred operations:

```text
bridge_send
bridge_inbox
bridge_read
bridge_reply
bridge_mark_done
bridge_threads
bridge_register_agent
bridge_status
bridge_notify
```

## CLI Fallback

Requires `mingjie-bridge` on PATH (see repo README install step). From inside the mingjie-stack repo, prefix with `scripts/` instead.

```bash
mingjie-bridge status
mingjie-bridge register codex --pane %1
mingjie-bridge register claude --pane %2
mingjie-bridge send --from codex --to claude --subject "Review plan" --body-file /tmp/message.md --file plan.md
mingjie-bridge inbox --for codex
mingjie-bridge read msg_123
mingjie-bridge reply msg_123 --from codex --body-file /tmp/reply.md
mingjie-bridge done msg_123
mingjie-bridge threads
```

## Message Shape

Keep messages concise:

```text
Goal:
Context:
Files:
Requested action:
Expected output:
```

## Registering Panes

Use stable tmux pane ids:

```bash
tmux list-panes -F '#{pane_index} #{pane_id} #{pane_current_command} #{pane_current_path}'
```

Then register each agent:

```bash
mingjie-bridge register codex --pane %1
mingjie-bridge register claude --pane %2
```

`bridge_notify` sends a short prompt into the registered pane. It is only a notification layer; the message content still lives in the bridge log.
