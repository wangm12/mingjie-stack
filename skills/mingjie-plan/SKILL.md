---
name: mingjie-plan
description: Use after framing to split accepted direction into small executable and verifiable tasks, with dependencies, risk, and planned-safe parallelization.
---

# Mingjie Plan

Purpose: split the chosen direction into executable, verifiable work.

**Before planning**: This stage requires the top-tier model + max effort (see Model Effort Policy in `mingjie-stack`). If the current model is not Claude Opus 4.7 effort:max (Claude Code) or gpt-5.5 effort:extra-high (Codex), stop and ask the user to switch via `/model` before continuing.

## Task Requirements

Each task must include:

- What changes
- Files or areas touched
- Verification check
- Dependencies
- Parallelization status
- Suggested executor: main agent / subagent / bridge review
- Full workflow verification, if the change affects a user or system path
- Risk

Task format:

```markdown
### Task N: <name>
What changes:
Files/areas:
Depends on:
Parallelization: sequential / can run with Task X / must be isolated
Suggested executor: main agent / subagent / bridge review
Verification: unit/integration/static checks
Workflow verification: complete path or E2E check, or "not applicable" with reason
Risk:
```

## Review Passes

- **Research/reuse pass:** Does an existing repo pattern, library, vendor API, MCP, or skill solve this with less custom code?
- **Scope pass:** Is any task unnecessary for the stated goal?
- **Engineering pass:** Are data flow, failure modes, tests, and edge cases clear?
- **Bridge pass:** If the user requested Codex/Claude coordination, identify exactly what to ask the other agent, what files/context to include, and how the answer will be verified.
- **Design/UX pass:** Required for user-facing UI; check flow clarity, states, accessibility, and visual quality.
- **Security/privacy pass:** Required for auth, user data, LLM output, external URLs, shell commands, SQL, payments, or secrets.
- **DX/API pass:** Required for CLIs, APIs, SDKs, docs, developer onboarding, or config changes.
- **Context-budget pass:** Are only the relevant docs, rules, files, and agents needed? Avoid loading broad rule packs or unrelated references.

## Autopilot Planning

When Autopilot is active:

- Infer conservative defaults from the existing codebase and user request.
- Ask only when ambiguity can materially change product behavior, data safety, security posture, public API, or user-visible outcome.
- Create the full plan without waiting for approval.
- Mark parallel-safe tasks and suggested subagent executors explicitly.
- Keep tightly coupled, risky, or blocking tasks with the main agent.
- Include workflow verification before Build starts.
- If the plan cannot identify meaningful verification, stop as blocked.

## Plan Convergence Loop

Loop: `Target -> Critique -> Modify -> Verify -> Decide`.

Target:

- Success criteria are explicit.
- Tasks are small, executable, and independently verifiable.
- Dependencies, risk, ownership, parallel safety, and suggested executor are visible.
- Unit-level and full workflow verification are both considered.
- Bridge/subagent review requests are scoped when used.
- No task exists only because of speculative flexibility.

Process:

1. Draft the plan.
2. Critique it against the review passes.
3. If blocking gaps exist, revise the plan.
4. Verify the revised plan against the target.
5. Repeat until target is reached or the loop limit is hit.

Loop limits:

- Normal work: up to 3 plan loops.
- Large/risky work: up to 5 plan loops.
- After the limit, stop and report blocked status with the unresolved gaps.

## Parallelization Map

For normal and large plans, explicitly separate:

- Sequential tasks
- Parallelizable tasks
- Risky tasks needing extra review
- Tasks suitable for subagents
- Tasks that must stay with the main agent because they are tightly coupled, risky, or blocking

Only mark tasks parallelizable when they have disjoint file/module ownership or a clearly safe integration contract.

When a task is marked parallelizable, include:

- Exact file/module ownership.
- What it must not touch.
- Required verification command.
- Integration point back into the main plan.

Do not mark tasks parallelizable just because they are independent conceptually; they must also be safe to edit in parallel.

## Verification Map

Every plan must distinguish:

- **Local verification:** unit tests, focused integration tests, lint, type checks, static checks.
- **Workflow verification:** the full user/system path affected by the change, such as browser E2E, API-to-database flow, CLI command end-to-end, migration dry run, or manual smoke test.

If workflow verification is not needed, state why. If it is needed but unavailable, mark the risk before Build starts.

## Rules

- Split large work into small units.
- Every unit must be independently verifiable.
- Mark parallel work in the plan before build starts.
- Do not use a subagent for implementation unless the plan explicitly marks the task as parallel-safe.
- Mark bridge work as advisory unless the user explicitly assigned the other agent edit ownership.
- If a plan spans independent subsystems, split it into separate plans.
- If the plan is too vague to verify, revise before building.
- Do not proceed to Build while blocking plan criteria are unmet.
- In Autopilot, proceed to Build automatically once the plan target converges.
- Do not create heavyweight docs unless risk justifies it.
- Select language/framework rules only for the current project, not every available ecosystem.
