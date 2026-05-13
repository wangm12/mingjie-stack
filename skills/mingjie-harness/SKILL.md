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
.mingjie/
  PROJECT.md
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
```

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

When `.mingjie/STATE.md` exists, use it to resume:

- Current phase
- Last successful verification
- Open blockers
- Next planned step

If state conflicts with the actual repo, trust the repo and update Harness before proceeding.

## Golden Examples

Use fixtures or run records to validate behavior:

- Tiny route
- Normal feature route
- Risky route that must stop
- Uber route that requires Uber skills
- Personal GitHub route that requires push authorization
- Non-English Autopilot trigger route
