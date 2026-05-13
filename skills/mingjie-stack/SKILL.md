---
name: mingjie-stack
description: Use as the orchestrator for adaptive coding work. Routes tasks through Mingjie Intake, Frame, Plan, Guard, Build, Review, Verify, Accept, and Ship based on size, risk, repo class, and authorization.
---

# Mingjie Stack

Self-contained guarded automation workflow. It borrows useful mechanics from Superpowers, gstack, and GSD while staying small.

```text
Intake -> Frame -> Plan -> Guard -> Build -> Review -> Verify -> Accept -> Ship
```

Sidecars:

- `Harness` persists run state, evidence, and scoped learning.
- `Bridge` coordinates Codex/Claude advice when requested or policy allows.
- `Multi-Agent Planning` coordinates tmux-based Claude Code/Codex plan drafts when large, risky, unknown, or explicitly requested.

Convergence rule: for planning, building, review, and verification, iterate `Target -> Critique -> Modify -> Verify -> Decide` until the target is reached or a bounded loop exposes a blocker.

## Source Extraction Map

- **Superpowers:** hard gates, TDD, worktrees, small verified tasks, subagent review loops, fresh verification before completion.
- **gstack:** product reframing, role-based plan review, browser QA, pre-landing review, ship readiness, lightweight retro.
- **GSD:** project state artifacts, codebase mapping, phase/wave execution, `next` continuation, verify/fix loops, atomic commits, package legitimacy checks.
- **Claude/Codex reality:** selective skill activation, context-budget hygiene, platform limits, and user-approved safety boundaries.

Do not require those systems to be installed. Apply the distilled behavior directly.

## Routing

- **Tiny:** Intake lite -> Mini Frame -> Guard -> Build -> Verify -> Accept
- **Normal:** Intake -> Frame -> Plan -> Guard -> Build -> Review -> Verify -> Accept
- **Large/risky:** Intake/map-codebase -> Frame -> Plan with waves -> Guard -> Build -> Review/QA -> Verify -> Accept -> Ship decision
- **Multi-agent planning:** Intake -> Frame -> Multi-Agent Plan Drafts -> Synthesis -> Judge Final Plan -> Guard -> Build
- **Rough idea:** Frame first after Intake; valid outcomes include reshape, defer, or abandon
- **Bug or unexpected behavior:** Intake -> reproduce/root cause -> Plan/Build -> Verify

Use the lightest route that protects correctness. Treat production behavior, data, auth, security, money, migrations, broad UI flows, public APIs, and company-internal workflows as large/risky.

## Multi-Agent Planning

Use this as a workflow layer over Claude Code and Codex, not as a custom agent runtime. Trigger it when the user explicitly asks for multiple agents, plan debate, different planning personalities, or when large/risky/unknown work would benefit from stronger planning pressure.

Default flow:

```text
Intake -> Frame -> Multi-Agent Plan Drafts -> Synthesis -> Judge Final Plan -> Guard -> Build
```

Use tmux panes as visible agent seats: Claude Code, Codex, and optionally shell. Claude Code and Codex may use their native subagents when available, but only within the role and ownership constraints in the judged final plan.

Required plan draft roles:

- `Conservative Planner`: minimal risk, reversible steps, proven patterns.
- `Aggressive Planner`: higher-leverage automation, bolder architecture options, under-scope challenges.
- `Pragmatic Planner`: fastest reliable path, dependency order, practical verification.
- `Skeptic-Guard`: hard stops, org/security/git/workflow risks, unsafe parallelism, missing verification.

Draft agents are advisory/read-only by default. Do not ask them to edit files unless the final plan grants explicit disjoint ownership. Before Build, the orchestrator must synthesize the drafts and produce one final `mingjie-plan` that marks each task as sequential, parallel-safe, bridge-review-only, or native-subagent-allowed.

Bridge messages for draft agents use:

```text
Goal:
Context:
Role:
Constraints:
Files:
Requested action:
Expected output:
```

When Harness is active, store evidence at:

```text
.mingjie/runs/<run-id>/multi-agent/
  BRIEF.md
  draft-conservative.md
  draft-aggressive.md
  draft-pragmatic.md
  draft-skeptic-guard.md
  synthesis.md
  final-plan.md
```

Full reference: `references/multi-agent-planning.md`.

## Autopilot Mode

Trigger Autopilot when the user uses an explicit phrase or clear equivalent intent in any language.

Explicit examples:

- `autopilot`
- `minimal interaction`
- `handle end to end`
- `use mingjie-stack and proceed`
- `全自动`
- `端到端处理`
- `从0到1`
- `少问我`

Intent rule: if the user says, in any language, to complete the work autonomously with minimal interaction and stop only on hard blockers, enter Autopilot after stating assumptions once.

In Autopilot:

- Run Intake automatically before Frame/Plan.
- Announce each stage transition before entering the next skill.
- Ask no clarifying questions unless ambiguity changes product behavior, data safety, security posture, public API, org workflow, or user-visible outcome.
- Use Harness to persist `.mingjie/` state when the task is normal, large, risky, or long-running.
- Use waves for independent work and subagents only when platform rules allow and the Plan marks disjoint ownership.
- If the platform prohibits automatic subagents, downgrade to sequential main-agent execution and note the constraint.
- Run local verification and workflow verification before Accept.
- Fix low-risk mechanical review findings automatically.
- Keep Bridge and Ship governed by policy below.

## Autopilot Hard Stops

- Destructive git/filesystem actions: force push, hard reset, broad delete, irreversible overwrite.
- Production deploys, production data writes, migrations, schema changes, or data backfills.
- Auth, security, privacy, payment, legal/compliance, or public API behavior changes where intent is ambiguous.
- Scope expansion beyond the user's stated goal.
- Parallel/subagent execution without disjoint ownership.
- Asking another tmux-pane agent to edit files unless the user explicitly assigned ownership.
- Required verification cannot run and the risk is material.
- Any convergence loop reaches its limit with blocking criteria unmet.
- Uber repo workflow skills are unavailable or cannot be used.

## Uber Repo Hard Stop

If Intake identifies an Uber repo, the agent must use the relevant locked Uber skills. Generic fallback is prohibited.

Required families:

- `uber-dev:diff-create`, `uber-dev:diff-update`, `uber-dev:diff-rebase`, `uber-dev:stacked-diffs`
- `uber-dev:pr-create`, `uber-dev:pr-update`, `uber-dev:babysit-pr`, `uber-dev:babysit-pr-stack`
- `uber-dev:babysit-diff`, `uber-dev:babysit-sq`, `uber-dev:babysit-stack`
- `uber-dev:verify`, `uber-dev:code-inbox`, `uber-dev:diff-notify`, `uber-dev:diff-reply`, `uber-dev:share-session`
- `uber-reviewer:checklist-reviewer`, `uber-reviewer:pr-commenting`, `uber-reviewer:ureview`

If an Uber repo is detected and those skills are unavailable or not usable, stop:

```text
Blocked: Uber repo requires Uber workflow skills. Generic GitHub push/PR/review is prohibited.
```

Never use personal GitHub push, generic PR creation, or generic review as a substitute for an Uber repo.

## Bridge Policy

- `off`: do not use bridge unless the user asks.
- `review-only`: use bridge for plan/final review on large or risky work when available.
- `full`: use bridge for plan and final review whenever available.
- `multi-agent`: use bridge/tmux seats for role-based plan drafts, synthesis inputs, and advisory review only.

Default: `off` for tiny/normal work, `review-only` for large/risky work. The user can say `bridge full`, `bridge review-only`, or `no bridge`.

## Ship Policy

- Local commits are allowed after verified tasks unless the user forbids commits.
- Push, deploy, merge, release, and production actions require explicit authorization.
- `ship allowed` permits the appropriate non-production ship backend after Guard approval.
- `deploy allowed` is required for deployment.
- Uber repos must ship through Uber skills only.

## Stage Skills

- Use `mingjie-intake` to discover project commands, instructions, risks, repo class, and ship path.
- Use `mingjie-frame` to clarify, challenge, reshape, defer, or abandon an idea before planning.
- Use `mingjie-plan` to split accepted direction into small executable tasks, waves, verification, and ownership.
- Use `mingjie-guard` before dangerous actions, org workflows, dependency changes, parallelism, and ship.
- Use `mingjie-build` to implement surgically with TDD where practical.
- Use `mingjie-review` to check quality, scope, risk, and production confidence.
- Use `mingjie-verify` to prove the user-visible or system-visible workflow.
- Use `mingjie-accept` to report evidence, risks, convergence, and final state.
- Use `mingjie-ship` to choose local/GitHub/internal/Uber delivery after acceptance.
- Use `mingjie-harness` to persist state and learning candidates across sessions.
- Use `mingjie-bridge` only for explicit or policy-approved cross-agent coordination.
- Use the Multi-Agent Planning reference when explicit multi-agent planning is requested or large/risky/unknown work needs role-based plan pressure.

## Stage Transition Prompts

At the end of every stage, state the next suggested skill and whether user approval is needed.

Manual mode format:

```text
Next suggested skill: `mingjie-plan`
Reason: Intake found commands and no hard blockers.
Options:
1. Proceed to `mingjie-plan`.
2. Discuss extra items outside the active plan.
3. Update plan/implementation before continuing.
Proceed?
```

Autopilot format:

```text
Next suggested skill: `mingjie-plan`
Autopilot: proceeding because no hard blocker was found.
Interruption options remain available: exit to discussion, update plan/implementation, or stop.
```

Rules:

- Do not silently jump between skills in manual mode.
- In Autopilot, do not wait for approval unless a hard stop or material ambiguity appears.
- If the next step is optional, name both the default and the alternative.
- Always include options to discuss extra items or update plan/implementation in manual mode.
- If the user chooses "Discuss extra items", exit the active plan/automation, pause stage progression, and switch to normal discussion mode. Do not keep executing the plan while discussion is active.
- After discussion, resume only when the user explicitly chooses to proceed, update the plan, update the implementation, stop, or restart the workflow.
- If the user chooses "Update plan/implementation", route to `mingjie-plan` for plan changes or `mingjie-build` for implementation fixes, whichever is appropriate.
- If a stage ends blocked, do not suggest a build/review/ship skill; suggest the stage that can unblock it, or ask the user for the blocking decision.
- Record the current stage and next suggested skill in Harness state when Harness is active.

## Model Effort Policy

Different stages reward different reasoning budgets. If the current model/effort does not match the recommendation, surface the mismatch before substantive work unless the user already chose to stay.

| Stage | Recommended model + effort |
|---|---|
| Plan, Review | Top-tier: Claude Code -> Opus effort:max; Codex -> highest available reasoning |
| Intake, Frame, Guard | Top-tier preferred for unknown/risky work |
| Build | Standard/high coding model |
| Verify, Accept, Ship | Standard; top-tier for risky releases |
| Harness, Bridge | No strict requirement |

## Harness State

For normal, large, risky, or long-running work, maintain project-scope state:

```text
.mingjie/PROJECT.md
.mingjie/STATE.md
.mingjie/RUNBOOK.md
.mingjie/runs/<timestamp>/
```

Project facts may be written automatically. User-scope, org-scope, or global skill learning requires approval.

If `.mingjie/STATE.md` exists, use it to infer the next step, then verify it against the actual repo before continuing.

## Principles

- Challenge assumptions before coding.
- Prefer project docs, config, and existing patterns over guesses.
- Keep scope minimal and explicit.
- Split work into small, verifiable units or waves.
- Keep context lean; load only relevant rules, docs, and files.
- Prefer TDD for behavior changes and bug fixes.
- Use parallel agents only for planned-independent tasks with disjoint ownership and platform permission.
- Treat Bridge replies as advice until verified locally.
- Do not build a custom agent runtime; use Claude Code, Codex, tmux seats, Bridge messages, and native subagents where available.
- Run Guard before crossing safety, org, dependency, or ship boundaries.
- Review for production readiness and Verify for actual user/system behavior.
- Never claim completion without fresh verification evidence.
- Learn from painful or repeated work, but do not silently change user/org/global behavior.
