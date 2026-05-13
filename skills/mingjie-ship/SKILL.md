---
name: mingjie-ship
description: Use after acceptance when deciding how to package, commit, push, create PRs, or hand off work across personal GitHub, local-only, and internal/Uber repositories.
---

# Mingjie Ship

Purpose: choose the correct delivery backend without mixing personal, open source, and internal workflows.

Ship runs only after Review, Verify, and Accept have evidence. It never bypasses Guard.

## Ship Backends

- **local:** create or leave local commits only.
- **github:** push to the configured GitHub remote when explicitly allowed.
- **internal-pr:** use the organization's PR/diff workflow.
- **uber:** use required Uber workflow skills.
- **none:** no repo or user asked not to package work.

## Backend Selection

Use Intake evidence:

- Uber repo: `uber` backend only. Generic GitHub push/PR is prohibited.
- Company/internal non-Uber repo: `internal-pr` if the project exposes a known PR skill/tool; otherwise stop and ask.
- Personal GitHub repo: `github` only when user says `ship allowed`, `push allowed`, or equivalent.
- No remote or local-only work: `local`.

## Uber Ship Rules

For Uber repos, call or require the relevant skills:

- Diff: `uber-dev:diff-create`, `uber-dev:diff-update`, `uber-dev:diff-rebase`
- PR: `uber-dev:pr-create`, `uber-dev:pr-update`
- Stack babysitting: `uber-dev:babysit-stack`, `uber-dev:babysit-diff`, `uber-dev:babysit-pr`
- Verification: `uber-dev:verify`

If these are unavailable, stop. Do not push to GitHub or create a generic PR.

## PR / Push Body

Generate a concise handoff from Harness evidence:

```text
Summary
Changes
Verification
Risks
Rollback
```

## Rules

- Local commits are allowed after successful verification unless the user forbids commits.
- Push, deploy, merge, release, and production actions require explicit authorization.
- Never ship with failed or missing required verification unless final state is `blocked` or `deferred`.
- Report the final ship state: local-only / pushed / PR-created / blocked / not requested.
- End with a stage transition prompt only if a follow-up is needed, such as babysitting CI, updating a PR, or recording a Harness lesson candidate. Otherwise state that no next skill is needed.
