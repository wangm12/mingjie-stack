# mingjie-stack

A lean guarded automation workflow for Claude Code and Codex, plus a tmux-session agent bridge for cross-agent coordination.

```
Intake -> Frame -> Plan -> Guard -> Build -> Review -> Verify -> Accept -> Ship
```

Autopilot mode runs the route end to end with conservative assumptions and stops only on hard blockers: destructive ops, production/data, security ambiguity, org workflow mismatch, scope creep, unsafe parallelism, missing verification, or loop limit.

## Layout

```
skills/                          Canonical skills (source of truth)
  mingjie-stack/                 Orchestrator: routing, autopilot, hard stops
  mingjie-intake/                Auto-discover project commands, docs, risk, repo class
  mingjie-frame/                 Clarify / challenge / shape / abandon
  mingjie-plan/                  Split into waves and small verifiable tasks
  mingjie-guard/                 Safety, org workflow, dependency, ship boundaries
  mingjie-build/                 Implement surgically (TDD where practical)
  mingjie-review/                Production-confidence gate
  mingjie-verify/                UAT/workflow verification and fix loop
  mingjie-accept/                Final state + fresh verification evidence
  mingjie-ship/                  Local/GitHub/internal/Uber delivery routing
  mingjie-harness/               Persistent state, evidence, scoped learning
  mingjie-bridge/                Sidecar: cross-agent coordination

mcp/
  agent_bridge_core.py           Event-sourced JSONL message log
  agent_bridge_server.py         MCP server (JSON-RPC over stdio)

scripts/
  mingjie-bridge                 CLI wrapper around AgentBridge
  launch-pair                    Create a tmux session with Claude + Codex panes
  install-cursor-rules           Generate .cursor/rules/*.mdc from skills/

install                          Interactive installer (one-liner setup)

templates/
  claude/.mcp.json               Bridge MCP snippet for Claude Code
  codex/mcp-config-snippet.toml  Bridge MCP snippet for Codex
  cursor/.mcp.json               Bridge MCP snippet for Cursor

tests/                           Unit + integration tests for the bridge and skills
.codex-plugin/plugin.json        Codex plugin manifest
```

## Install

Requires Python 3.9+, tmux, and stdlib only. No third-party packages.

### One-liner (recommended)

From the repo root:

```bash
./install
```

Interactive wizard. Detects which agents you have (Claude Code / Codex / Cursor / AIFX), asks per step, never overwrites existing config without showing a diff first. Fully idempotent — safe to re-run.

Flags:

```bash
./install --yes                  # accept all defaults non-interactively
./install --dry-run              # show what would happen, no changes
./install --only claude,codex    # subset: cli|claude|codex|cursor
```

Cursor rules are per-project (Cursor's design), so the installer skips them and prints the per-project command at the end. To set up a specific project:

```bash
cd /path/to/your/project
/path/to/mingjie-stack/scripts/install-cursor-rules
```

### Manual install

If you want to do it by hand instead of the wizard, see the per-target sections below.

### Codex

Codex (including AIFX-launched `aifx agent run codex`) reads skills from `~/.codex/skills/`. The one-liner installer symlinks `skills/` there; for manual install, mirror the Claude Code approach:

```bash
mkdir -p ~/.codex/skills
ln -s "$(pwd)/skills/"* ~/.codex/skills/
```

For the bridge MCP server, copy `templates/codex/mcp-config-snippet.toml` into `~/.codex/config.toml` and replace `/ABSOLUTE/PATH/TO/mingjie-stack` with this repo's absolute path. (Vanilla Codex without AIFX may also load skills via the repo's `.codex-plugin/plugin.json` — that path still works but the installer doesn't use it.)

### Claude Code

Symlink the skills under `~/.claude/skills/` so updates to this repo propagate automatically:

```bash
mkdir -p ~/.claude/skills
ln -s "$(pwd)/skills/"* ~/.claude/skills/
# or, if symlinks aren't supported in your environment:
cp -r skills/* ~/.claude/skills/
```

Add the bridge MCP server to your Claude Code MCP config (snippet at `templates/claude/.mcp.json`):

```json
{
  "mcpServers": {
    "mingjie-agent-bridge": {
      "command": "python3",
      "args": ["/ABSOLUTE/PATH/TO/mingjie-stack/mcp/agent_bridge_server.py"]
    }
  }
}
```

The CLI also prints the right snippet for either tool:

```bash
scripts/mingjie-bridge config --tool codex
scripts/mingjie-bridge config --tool claude
```

### Cursor (IDE and CLI)

Cursor uses project-scoped rules at `.cursor/rules/*.mdc`. Generate them from the canonical skills into a target project:

```bash
cd /path/to/your/project
/path/to/mingjie-stack/scripts/install-cursor-rules
# or, with an explicit target:
/path/to/mingjie-stack/scripts/install-cursor-rules --target /path/to/project
```

This writes `mingjie-*.mdc` files into `.cursor/rules/`. The orchestrator (`mingjie-stack`) is `alwaysApply: true`; every stage skill is agent-requested (Cursor's agent loads it on demand based on its description). Re-run the script after editing any `skills/*/SKILL.md` to refresh.

Add the bridge MCP server at `~/.cursor/mcp.json` (user-level, recommended) or `.cursor/mcp.json` (project-level). Snippet at `templates/cursor/.mcp.json`:

```json
{
  "mcpServers": {
    "mingjie-agent-bridge": {
      "command": "python3",
      "args": ["/ABSOLUTE/PATH/TO/mingjie-stack/mcp/agent_bridge_server.py"]
    }
  }
}
```

Cursor CLI uses the same `.cursor/rules/` and MCP config conventions as the IDE, so the steps above cover both. If a future Cursor CLI release diverges, edit `scripts/install-cursor-rules` to retarget.

### CLI on PATH (optional, but needed for the bridge CLI fallback)

The bridge MCP server above is the primary interface. If you also want to call `mingjie-bridge` directly from any project (the CLI fallback path the bridge skill mentions), put it on PATH:

```bash
mkdir -p ~/.local/bin
ln -s "$(pwd)/scripts/mingjie-bridge" ~/.local/bin/mingjie-bridge
```

After this, `mingjie-bridge ...` works from any cwd. Without it, the CLI examples in the bridge skill only resolve from inside this repo.

## Quick start

### Autopilot

Trigger phrases and clear equivalent intent:

- `autopilot`
- `minimal interaction`
- `handle end to end`
- `use mingjie-stack and proceed`
- `全自动`
- `端到端处理`
- `从0到1`
- `少问我`

If the user says in any language to complete the work autonomously with minimal interaction and stop only on hard blockers, the orchestrator may enter Autopilot after stating assumptions once.

Optional controls:

- Bridge override: append `bridge full`, `bridge review-only`, or `no bridge`
- Ship authorization: append `ship allowed`
- Deploy authorization: append `deploy allowed`

Example:

```
autopilot — add rate limiting to /api/upload
全自动 — 给这个 CLI 增加 doctor 命令，最后跑完整测试
autopilot ship allowed — update README and push this personal GitHub repo
```

Uber/internal repos are different: if Intake detects an Uber repo, generic GitHub push/PR/review is prohibited. The agent must use the relevant locked `uber-dev:*` and `uber-reviewer:*` skills, such as `uber-dev:diff-create`, `uber-dev:pr-create`, `uber-dev:verify`, and `uber-reviewer:ureview`. If those skills are unavailable, the task must stop as blocked.

### Manual route

Pick the lightest route that still protects correctness:

| Size       | Route                                                         |
|------------|---------------------------------------------------------------|
| Tiny       | Intake lite -> Mini Frame -> Guard -> Build -> Verify -> Accept |
| Normal     | Intake -> Frame -> Plan -> Guard -> Build -> Review -> Verify -> Accept |
| Large/risky| Intake/map-codebase -> Frame -> Plan (waves) -> Guard -> Worktree -> Build -> Review/QA -> Verify -> Accept -> Ship decision |

Invoke each stage by name (`mingjie-intake`, `mingjie-frame`, `mingjie-plan`, etc.) or let the orchestrator route.

### Harness

For normal, large, risky, or long-running work, Mingjie Harness may persist project-scope state:

```text
.mingjie/
  PROJECT.md
  STATE.md
  RUNBOOK.md
  ROADMAP.md
  runs/<timestamp>/
    INTAKE.md
    PLAN.md
    GUARD.md
    EVIDENCE.md
    REVIEW.md
    VERIFY.md
    ACCEPT.md
    LESSONS.md
```

Project facts and run evidence can be written automatically. User-scope lessons, org profiles, and global skill changes require explicit approval.

### Stage transitions

Every stage ends by naming the next suggested skill.

Manual mode asks before moving on:

```text
Next suggested skill: `mingjie-plan`
Reason: Intake found commands and no hard blockers.
Proceed?
```

Autopilot announces and continues unless a hard stop appears:

```text
Next suggested skill: `mingjie-plan`
Autopilot: proceeding because no hard blocker was found.
```

### Bridge

Cross-agent coordination via tmux panes (assumes `mingjie-bridge` is on PATH; otherwise prefix with `scripts/` from inside the repo):

```bash
tmux list-panes -F '#{pane_index} #{pane_id} #{pane_current_command}'
mingjie-bridge register codex --pane %1
mingjie-bridge register claude --pane %2
mingjie-bridge send --from codex --to claude \
  --subject "Review plan" --body-file /tmp/plan.md --file plan.md
mingjie-bridge inbox --for claude
```

### One-command paired session

To skip the manual tmux + register dance, use `launch-pair` (installed to PATH by the installer):

```bash
cd /path/to/your/project
launch-pair                # session name = current dir basename, asks for confirmation
launch-pair my-name        # explicit name
launch-pair --yes          # skip confirmation
```

What it does:

1. Creates a tmux session (default name = current directory basename)
2. Splits into 3 vertical panes: `claude | shell | codex`
3. Pre-registers both agents (auto-register on first MCP tool call also works as a fallback)
4. Launches `aifx agent run claude` in pane 0 and `aifx agent run codex` in pane 2
5. Attaches you to the session

If the named session already exists, it just attaches — safe to re-run.

### Model effort hook (Claude Code)

The skills already document the model-effort policy and ask the agent to surface it. To make sure the agent never misses it on stage entry, wire `scripts/model-effort-check` as a `PreToolUse` hook in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Skill",
        "hooks": [
          {
            "type": "command",
            "command": "/ABSOLUTE/PATH/TO/mingjie-stack/scripts/model-effort-check"
          }
        ]
      }
    ]
  }
}
```

Replace `/ABSOLUTE/PATH/TO/mingjie-stack` with this repo's absolute path. The hook fires on every Skill invocation, prints a one-line reminder when entering `mingjie-plan` / `mingjie-review` / `mingjie-build`, and is a no-op otherwise.

Codex doesn't use the same hook system, so for Codex the policy lives only in the skill text — works the same way (agent reads, surfaces to user) just without the extra reminder layer.

Bridge data lives at `~/.mingjie-stack/agent-bridge/sessions/<tmux-session>/`.

## Testing

```bash
python3 -m unittest discover tests
```

## Conventions

- `skills/` is the only place to edit skill markdown. Claude Code loads it via the symlink under `~/.claude/skills/`; Codex (incl. AIFX) loads it via the symlink under `~/.codex/skills/`; Cursor loads it via MDC files generated by `scripts/install-cursor-rules`.
- Skills are markdown only — no executable code. Implementation lives in `mcp/` and `scripts/`.
- Bridge writes are append-only and protected with `fcntl.LOCK_EX`; readers take `fcntl.LOCK_SH`. Safe for concurrent writers and concurrent readers.
