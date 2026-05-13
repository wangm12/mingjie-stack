---
name: mingjie-harness
description: Use to persist Mingjie Stack run state, evidence, project runbooks, golden examples, and learning candidates across sessions without unsafe global self-modification.
---

# Mingjie Harness

Purpose: make long-running automated work resumable and evidence-backed.

Harness can learn, but learning is scoped. Project facts may be written automatically. User, org, or global behavior changes require approval.

## Project scope

Default writable location:

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
    GUARD.md
    EVIDENCE.md
    REVIEW.md
    VERIFY.md
    ACCEPT.md
    LESSONS.md
    archive/YYYY-MM.md
```

Use `mingjie-harness init` to create this directory and add ignore rules for volatile state. New writes use `docs/mingjie-stack/`; legacy `.mingjie/STATE.md` is read only for resume compatibility.

Project scope may record automatically:

- Detected commands and repo conventions
- Current phase and next step
- Verification evidence
- Project-specific failures and fixes
- Known risk areas

## User scope

Suggested location:

```text
~/.mingjie-stack/user-lessons.md
```

User scope requires approval. It can store cross-project preferences such as:

- Default to guarded Autopilot
- Ask before push
- Prefer baseline commits before risky work
- Recognize multilingual Autopilot intent

Harness may propose a user-scope lesson, but must not apply it without approval.

## Org scope

Suggested location:

```text
~/.mingjie-stack/org-profiles/
  uber.md
  personal-github.md
```

Org scope requires approval. It can store organization-specific workflows, such as Uber requiring `uber-dev:*` and `uber-reviewer:*` skills.

Never leak org-specific lessons into personal projects unless the lesson is explicitly generic and approved.

## Learning Rules

- Automatically write project facts and run evidence.
- Automatically create lesson candidates with evidence.
- Do not rewrite skills, user lessons, or org profiles without approval.
- Do not learn from a single ambiguous failure as a global rule.
- Do not record secrets, tokens, private data snippets, or production data.
- Every promoted lesson needs scope, evidence, proposed rule, and rollback note.

## Next Step Detection

When `docs/mingjie-stack/STATE.md` exists, use it to resume. If it is missing but legacy `.mingjie/STATE.md` exists, read the legacy state, verify it against the repo, then write future state to `docs/mingjie-stack/`.

- Current phase
- Last successful verification
- Open blockers
- Next planned step

If state conflicts with the actual repo, trust the repo and update Harness before proceeding.

## CLI

Use the project-scope CLI instead of hand-writing state when available:

```bash
mingjie-harness init
mingjie-harness start-run
mingjie-harness update-state --run-id <id> --stage build --next review
mingjie-harness append-evidence --run-id <id> --title tests --command "python3 -m unittest discover tests" --result OK
mingjie-harness status
mingjie-harness runs list
mingjie-harness runs summarize --run-id <id>
mingjie-harness runs prune --keep 10
mingjie-harness runs prune --keep 10 --yes
mingjie-harness runs pin <id>
mingjie-harness runs unpin <id>
```

Volatile files should stay untracked:

```text
docs/mingjie-stack/STATE.md
docs/mingjie-stack/runs/
```

Hooks installed with `./setup --hooks` may call `mingjie-harness` automatically to surface state at session start and append command evidence after tool use.

## Run Retention

When runs grow too large, summarize before deleting raw artifacts:

- Keep the newest unpinned runs; default retention is 10.
- `runs prune` is a dry-run preview unless `--yes` is passed.
- `runs pin <id>` creates a `PINNED` marker; pinned runs are never pruned.
- Summaries are written to `RUNS_INDEX.md` and `runs/archive/YYYY-MM.md`.
- Failed, blocked, risky, or surprising runs should be pinned before pruning.

## Stage Transitions

When Harness is active, record:

- Current skill/stage
- Last completed stage
- Next suggested skill
- Whether Autopilot is proceeding or waiting for approval
- Blocker, if any

## Golden Examples

Use fixtures or run records to validate behavior:

- Tiny route
- Normal feature route
- Risky route that must stop
- Uber route that requires Uber skills
- Personal GitHub route that requires push authorization
- Non-English Autopilot trigger route
- Manual mode stage transition prompt
