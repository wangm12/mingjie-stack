---
name: mingjie-build
description: Use to implement an approved Mingjie Plan surgically, using TDD where practical, root-cause investigation for bugs, worktrees for risky work, and subagents only for plan-marked parallel-safe tasks.
---

# Mingjie Build

Purpose: implement surgically.

**Before building**: This stage uses the standard model — top-tier reasoning is wasted on mechanical implementation. If the current model is top-tier (e.g. Opus 4.7 effort:max), suggest the user switch down to the standard tier (Sonnet for Claude Code, gpt-5.5 effort:high for Codex) to save effort. Skip the suggestion if the user has explicitly chosen to stay on top-tier.

## Rules

- Use TDD for behavior changes and bug fixes where practical.
- For a bug, first reproduce or locate root cause; do not patch guesses.
- Match existing code style.
- No speculative abstractions.
- No unrelated cleanup.
- Use worktrees for large/risky work.
- Respect the Intake runbook and Guard write scope.
- Use subagents only for plan-marked parallel-safe tasks.
- Before using a subagent, confirm the task has explicit file/module ownership, forbidden touch areas, verification command, and integration point.
- Give parallel agents disjoint file/module ownership.
- Parallel agents are not alone in the codebase; they must not revert or overwrite others' work.
- Commit or checkpoint at sensible task boundaries when the repo workflow supports it.
- If the repo is clean and the task is independently verified, prefer an atomic local commit per completed task; never push from Build.
- Before destructive commands, force-pushes, data changes, deploys, broad deletes, or autonomous edits, stop and ask for explicit confirmation.
- When work should be isolated to a directory/module, treat that as a write boundary and do not edit outside it without revising the plan.
- Use only task-relevant rules/docs/context; do not load broad unrelated skill packs.

## TDD Loop

For applicable tasks:

1. Write the smallest failing test for one behavior.
2. Run it and confirm it fails for the expected reason.
3. Implement the minimal code to pass.
4. Run targeted tests.
5. Refactor only after green.
6. Run broader verification when the change can affect shared behavior.

## Autopilot Build

When Autopilot is active:

- Execute the approved plan without asking between tasks.
- Dispatch subagents automatically only for plan-marked parallel-safe tasks.
- If platform rules prohibit automatic subagents, run the tasks sequentially in the main agent and note the downgrade.
- Keep the main agent on blocking, risky, or tightly coupled tasks.
- Run each task's local verification before considering it done.
- Run full workflow verification after integrating parallel work.
- Stop before hard-stop actions: destructive commands, production/data changes, migrations, broad rewrites, or ambiguous product/security decisions.
- Stop if an Uber repo requires `uber-dev:*` skills and they are unavailable.
- If a task reveals new scope or invalidates the plan, return to Plan instead of improvising.

## Task Convergence Loop

Loop: `Target -> Critique -> Modify -> Verify -> Decide`.

Target:

- The current planned task is implemented, not adjacent wishes.
- Acceptance criteria and verification checks pass.
- The required local and workflow verification for the task have run, or unavailable workflow verification is reported as risk.
- Blocking review findings are fixed.
- New risks are either handled or returned to Plan.
- No unrelated files or behavior changed.

Process:

1. Build the smallest planned unit.
2. Run the task verification.
3. Critique the result against the plan, diff scope, and test evidence.
4. If blocking issues remain, modify the implementation and verify again.
5. Repeat until target is reached or the loop limit is hit.

Loop limits:

- Normal work: up to 3 build loops per task.
- Large/risky work: up to 5 build loops per task.
- After the limit, stop and report blocked status with the exact remaining issue.

Do not move to the next planned task while the current task has blocking verification or review failures.

## Parallel Build Rules

Parallel execution is allowed only for tasks marked by the plan as `can run with Task X` or `must be isolated`.

Before dispatching a subagent, provide:

- Goal and task text.
- Exact owned files/modules.
- Files/modules it must not touch.
- Expected integration contract.
- Local verification command.
- Required workflow verification or explicit note that the main agent will run it after integration.

After subagents return:

- Review their changed files before integration.
- Run each task's local verification.
- Run the relevant full workflow verification after integrating parallel work.
- If outputs conflict, stop and resolve intentionally; do not merge by guess.
- In Autopilot, resolve only low-risk mechanical conflicts; ask before behavior-changing conflict resolution.

## Subagent Rules

Use subagents only when the plan marks work as independent.

Each subagent prompt must include:

- Goal
- Exact task text
- File/module ownership
- What not to touch
- Verification command
- Workflow verification responsibility
- Expected final report

Do not dispatch parallel agents that may write the same files unless the user explicitly accepts the merge risk.

## Harness Updates

When Harness is active, update `.mingjie/STATE.md` after each verified task with:

- Task id and status
- Files changed
- Verification command and result
- Commit id, if a local commit was created
- Next step or blocker
