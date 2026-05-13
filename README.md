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
    references/                  Workflow references, including multi-agent planning
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
  mingjie-harness                Project-scope Harness state/evidence CLI
  mingjie-hook                   Claude/Codex hook adapter
  launch-pair                    Create a tmux session with Claude + Codex panes
  install-cursor-rules           Generate .cursor/rules/*.mdc from skills/

install                          Interactive installer (one-liner setup)

templates/
  claude/.mcp.json               Bridge MCP snippet for Claude Code
  claude/settings-hooks.json     Optional Claude Code hooks snippet
  codex/mcp-config-snippet.toml  Bridge MCP snippet for Codex
  codex/hooks.json               Optional Codex hooks snippet
  codex/config-hooks-snippet.toml Optional Codex hook feature snippet
  cursor/.mcp.json               Bridge MCP snippet for Cursor

tests/                           Unit + integration tests for the bridge and skills
.codex-plugin/plugin.json        Codex plugin manifest
```

## Install

Requires Python 3.9+, tmux, and stdlib only. No third-party packages.

### One-liner (recommended)

From the repo root:

```bash
./setup
```

This runs the installer non-interactively with safe defaults, verifies bridge config snippets, and prints the next `launch-pair` command. It does not overwrite differing existing config unless you run the lower-level installer interactively and approve the overwrite.

Useful setup flags:

```bash
./setup --dry-run                 # show what would happen
./setup --hooks                   # also configure optional Claude/Codex hooks
./setup --cursor-rules            # also generate .cursor/rules for the current project
./setup --launch --layout 2       # install, then launch claude | codex
./setup --launch --layout 3       # install, then launch claude | shell | codex
```

### Installer wizard

For step-by-step prompts:

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

### CLI on PATH (optional, but useful for bridge and Harness)

The installer links `mingjie-bridge`, `mingjie-harness`, and `launch-pair` into `~/.local/bin`. For manual install:

```bash
mkdir -p ~/.local/bin
ln -s "$(pwd)/scripts/mingjie-bridge" ~/.local/bin/mingjie-bridge
ln -s "$(pwd)/scripts/mingjie-harness" ~/.local/bin/mingjie-harness
ln -s "$(pwd)/scripts/launch-pair" ~/.local/bin/launch-pair
```

After this, the CLI examples work from any cwd. Without it, prefix commands with this repo's `scripts/` path.

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

### Multi-agent planning

Mingjie Stack does not run its own agent runtime. For plan debate, it coordinates Claude Code and Codex in tmux panes, then produces one final `mingjie-plan`.

Use it when you explicitly ask for multiple agents or different planning personalities, or when the work is large, risky, unknown, or high ambiguity:

```text
Intake -> Frame -> Multi-Agent Plan Drafts -> Synthesis -> Judge Final Plan -> Guard -> Build
```

Typical setup:

```bash
cd /path/to/your/project
launch-pair --layout 3
```

Example prompts:

```text
多个 agent 同时 draft plan，然后综合保守/激进/实用/质疑视角
different personalities plan debate before implementation
large risky change, use tmux agents and native subagents if safe
```

Draft roles:

- `Conservative Planner`: minimal risk, reversible steps, proven patterns
- `Aggressive Planner`: higher-leverage automation and bolder architecture options
- `Pragmatic Planner`: fastest reliable implementation sequence
- `Skeptic-Guard`: hard stops, org/security/git/workflow risks, missing verification

Draft agents are advisory/read-only by default. Claude Code and Codex may use their native subagents only inside the role and ownership constraints in the judged final plan. The main orchestrator must synthesize all drafts into one final plan before Build.

### Harness

For normal, large, risky, or long-running work, Mingjie Harness may persist project-scope state:

```text
docs/mingjie-stack/
  PROJECT.md
  RUNS_INDEX.md
  STATE.md
  RUNBOOK.md
  ROADMAP.md
  lessons.md
  runs/<timestamp>/
    INTAKE.md
    PLAN.md
    multi-agent/
      BRIEF.md
      draft-conservative.md
      draft-aggressive.md
      draft-pragmatic.md
      draft-skeptic-guard.md
      synthesis.md
      final-plan.md
    GUARD.md
    EVIDENCE.md
    REVIEW.md
    VERIFY.md
    ACCEPT.md
    LESSONS.md
    archive/
      2026-05.md
```

Project facts and run evidence can be written automatically. User-scope lessons, org profiles, and global skill changes require explicit approval. New writes use `docs/mingjie-stack/`; legacy `.mingjie/STATE.md` is still read for resume compatibility.

Initialize or update state with:

```bash
mingjie-harness init
mingjie-harness start-run
mingjie-harness update-state --run-id <id> --stage build --next review
mingjie-harness append-evidence --run-id <id> --title tests --command "python3 -m unittest discover tests" --result OK
mingjie-harness status
```

Keep run history small with:

```bash
mingjie-harness runs list
mingjie-harness runs summarize --run-id <id>
mingjie-harness runs prune --keep 10        # dry-run preview by default
mingjie-harness runs prune --keep 10 --yes  # summarize then delete old raw run dirs
mingjie-harness runs pin <id>
mingjie-harness runs unpin <id>
```

`runs prune` never deletes a run containing `PINNED`. Pruned runs are summarized into `RUNS_INDEX.md` and `runs/archive/YYYY-MM.md` before raw artifacts are removed.

Create multi-agent planning artifacts with:

```bash
mingjie-harness multi-agent init --run-id <id> --goal "Implement X"
mingjie-harness multi-agent status --run-id <id>
mingjie-harness multi-agent send-bridge --run-id <id> --dry-run
```

This creates `BRIEF.md`, the four role draft files, `synthesis.md`, and `final-plan.md` under `docs/mingjie-stack/runs/<id>/multi-agent/`. `send-bridge` can route advisory draft requests through `mingjie-bridge`; use `--dry-run` first to inspect the messages.

Volatile state is ignored by default:

```gitignore
docs/mingjie-stack/STATE.md
docs/mingjie-stack/runs/
```

### Stage transitions

Every stage ends by naming the next suggested skill.

Manual mode asks before moving on:

```text
Next suggested skill: `mingjie-plan`
Reason: Intake found commands and no hard blockers.
Options:
1. Proceed to `mingjie-plan`.
2. Discuss extra items outside the active plan.
3. Update plan/implementation before continuing.
Proceed?
```

Autopilot announces and continues unless a hard stop appears:

```text
Next suggested skill: `mingjie-plan`
Autopilot: proceeding because no hard blocker was found.
Interruption options remain available: exit to discussion, update plan/implementation, or stop.
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
launch-pair --layout 2     # claude | codex
launch-pair --layout 3     # claude | shell | codex
launch-pair my-name        # explicit name
launch-pair --yes          # skip confirmation
```

What it does:

1. Creates a tmux session (default name = current directory basename)
2. Splits into 2 or 3 vertical panes: `claude | codex` or `claude | shell | codex`
3. Pre-registers both agents (auto-register on first MCP tool call also works as a fallback)
4. Launches `aifx agent run claude` and `aifx agent run codex`
5. Attaches you to the session

If the named session already exists, it just attaches — safe to re-run.

### Hooks

Hooks are opt-in. They add automatic context, guard checks, evidence capture, and a final verification gate around the skill workflow:

```bash
./setup --hooks
```

This installs `mingjie-hook` and merges hook config for Claude Code and Codex. The adapter reads hook JSON from stdin and writes project evidence through `mingjie-harness`.

What the adapter does:

- `SessionStart` / `UserPromptSubmit`: prints current `docs/mingjie-stack/STATE.md` context when present.
- `PreToolUse` / `PermissionRequest`: blocks destructive git/filesystem commands, unapproved push/deploy actions, and generic GitHub push/PR in Uber repos.
- `PostToolUse` / `PostToolUseFailure`: appends Bash command evidence to the active Harness run.
- `Stop`: blocks completion claims when the active run has no fresh `Result: OK` Harness evidence.

Hooks are a workflow backstop, not a complete security boundary. Keep Guard and Review in the skill flow.

### Model effort hook (Claude Code)

The older `scripts/model-effort-check` hook is still available if you only want model-effort reminders. To wire it manually as a `PreToolUse` hook in `~/.claude/settings.json`:

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

The cross-platform `mingjie-hook` adapter above is the preferred default. Keep `model-effort-check` only if you want a narrower hook that does not write Harness evidence or block risky commands.

Bridge data lives at `~/.mingjie-stack/agent-bridge/sessions/<tmux-session>/`.

## Testing

```bash
python3 -m unittest discover tests
```

## Conventions

- `skills/` is the only place to edit skill markdown. Claude Code loads it via the symlink under `~/.claude/skills/`; Codex (incl. AIFX) loads it via the symlink under `~/.codex/skills/`; Cursor loads it via MDC files generated by `scripts/install-cursor-rules`.
- Skills are markdown only — no executable code. Implementation lives in `mcp/` and `scripts/`.
- Bridge writes are append-only and protected with `fcntl.LOCK_EX`; readers take `fcntl.LOCK_SH`. Safe for concurrent writers and concurrent readers.
