---
name: mingjie-stack
description: Use as the orchestrator for adaptive coding work. Routes tasks through Mingjie Frame, Plan, Build, Review, and Accept based on size and risk.
---

# Mingjie Stack

Self-contained adaptive workflow. It borrows the useful mechanics from Superpowers and gstack, but does not require either to be installed.

`Frame -> Plan -> Build -> Review -> Accept`

Optional sidecar: `Bridge` for explicit Codex/Claude coordination.

Ralph-inspired convergence rule: for planning, building, and review, iterate `Target -> Critique -> Modify -> Verify -> Decide` until the target is reached or a bounded loop limit exposes a blocker.

Autopilot mode: when the user asks for minimal interaction, proceed through the full workflow with conservative assumptions and stop only for hard blockers.

## Source Extraction Map

This stack intentionally takes strengths from three sources and removes the excess:

- **Superpowers:** hard gates, TDD, worktrees, small verified tasks, subagent review loops, fresh verification before completion.
- **gstack:** product reframing, role-based plan review, browser QA, pre-landing review, ship readiness, lightweight retro.
- **Everything Claude Code:** selective activation, research/reuse before custom code, context-budget hygiene, safety guardrails, verification loops, language/project-specific rules, project-scoped learning.

Do not require any of those systems to be installed. Apply the distilled behavior directly.

## Routing

- **Tiny:** Mini Frame -> Build -> Verify -> Accept
- **Normal:** Frame -> Plan -> Build -> Review -> Accept
- **Large/risky:** Frame -> Plan with parallelization map -> Worktree -> Build -> Review/QA -> Accept
- **Rough idea:** Frame first; valid outcomes include reshape, defer, or abandon
- **Bug or unexpected behavior:** Investigate root cause before fixing

Use the lightest route that still protects correctness. If the work touches production behavior, data, security, money, auth, migrations, or broad UI flows, treat it as large/risky.

## Autopilot Mode

Trigger only when the user uses one of these explicit phrases: `autopilot`, `minimal interaction`, `handle end to end`, `use mingjie-stack and proceed`. Do not infer Autopilot from indirect phrasing such as "go ahead", "use the stack", or "just do it"; ask the user if their intent is unclear.

In Autopilot:

- Follow the route appropriate for the task size from the Routing section above. Autopilot does not force a Tiny task through Plan and Review; it runs the route's stages without asking between them.
- State assumptions once, then proceed.
- Ask no clarifying questions unless ambiguity can change product behavior, data safety, security posture, public API, or user-visible outcome.
- Use convergence loops automatically.
- Use subagents automatically only for plan-marked parallel-safe tasks.
- Run local verification and full affected workflow verification before Accept.
- Fix low-risk mechanical review findings automatically.
- Keep bridge usage governed by bridge policy below.

Autopilot hard stops:

- Destructive git or filesystem actions: force push, reset, broad deletes, irreversible overwrites.
- Production deploys, production data writes, migrations, schema changes, or data backfills.
- Auth, security, privacy, payment, legal/compliance, or public API behavior changes where intent is ambiguous.
- Scope expansion beyond the user's stated goal.
- Parallel/subagent execution without disjoint ownership.
- Asking another tmux-pane agent to edit files unless the user explicitly assigned that ownership.
- Required verification cannot run and the risk is material.
- Any convergence loop reaches its limit with blocking criteria unmet.

Autopilot final-state vocabulary (used by Accept):

- `not used`: Autopilot was never triggered for this task.
- `completed`: Autopilot ran the full route end to end and Accept's verification target was met.
- `stopped`: Autopilot hit a hard stop and is waiting for explicit user confirmation to continue.
- `blocked`: A convergence loop reached its limit with blocking criteria unmet, or required verification could not run with material risk.

Bridge policy in Autopilot:

- `off`: do not use bridge unless the user asks.
- `review-only`: use bridge for plan/final review on large or risky work when the other pane is available.
- `full`: use bridge for plan review and final review whenever available.

Default bridge policy is `off` for tiny/normal work and `review-only` for large/risky work. The user overrides by stating the policy in the Autopilot prompt, e.g. "autopilot bridge full" or "autopilot no bridge"; otherwise the default applies.

## Stage Skills

- Use `mingjie-frame` to clarify, challenge, reshape, defer, or abandon an idea before planning.
- Use `mingjie-plan` to split accepted direction into small executable and verifiable tasks.
- Use `mingjie-build` to implement surgically with TDD where practical and plan-marked parallel-safe execution.
- Use `mingjie-review` to run self-review, compliance checks, QA, and the production-confidence gate.
- Use `mingjie-accept` to report verification evidence and final state.
- Use `mingjie-bridge` only when the user asks for Codex/Claude coordination, tmux pane communication, external agent review, or cross-agent planning.

## Model Effort Policy

Different stages reward different reasoning budgets. When entering a stage, check the current model and effort level. If it does not match the recommendation below, **stop and ask the user to switch via `/model`** before doing the substantive work.

| Stage           | Recommended model + effort                                            |
|-----------------|-----------------------------------------------------------------------|
| Plan            | **Top-tier**: Claude Code → Opus 4.7 effort:max; Codex → gpt-5.5 effort:extra-high |
| Review          | **Top-tier**: same as Plan                                            |
| Build           | Standard: Claude Code → Sonnet (current); Codex → gpt-5.5 effort:high |
| Frame, Accept   | No strict requirement; top-tier preferred for Frame on novel ideas    |
| Bridge sidecar  | Doesn't matter                                                        |

When recommending a switch, give the exact command. Examples:
- Claude Code: `/model opus` then `/effort max`
- Codex: `/model gpt-5.5 extra-high`

If the user explicitly tells you to ignore this policy (e.g. "stay on the current model"), comply and note the choice in Accept's report.

## Principles

- Challenge assumptions before coding.
- Search for existing repo patterns, libraries, docs, and skills before writing custom code.
- Keep scope minimal and explicit.
- Split work into small, verifiable units.
- Keep context lean; load only relevant rules, docs, and files.
- Prefer TDD for behavior changes and bug fixes.
- Use parallel agents only for planned-independent tasks with disjoint ownership.
- Use the bridge as an advisory communication channel, not as an autonomous edit loop.
- Loop on blocking critique until the target is reached, but never loop silently forever.
- In Autopilot, prefer action over repeated confirmation, but never cross hard-stop boundaries without asking.
- Add safety guardrails before destructive, production, migration, or autonomous work.
- Review for production readiness, not just apparent correctness.
- Never claim completion without fresh verification evidence.
- Learn from painful or surprising work, but do not force retros for routine changes.

## Tiny Route

Use when the task is obviously low risk: typo, formatting, tiny config, simple command, one-line internal fix.

Output:

```text
Mini Frame: goal, assumption, verification
Build: change
Review: self-check + targeted verification
Accept: evidence + final state
```

## Normal Route

Use for typical features, bug fixes, refactors, and multi-file changes with bounded risk.

Output:

```text
Frame
Plan
Build
Review
Accept
```

If the user asks for cross-agent help, run `Bridge` as a sidecar during Plan or Review:

```text
Frame
Plan -> Bridge advisory review
Build
Review -> Bridge optional second opinion
Accept
```

For normal work, use up to 3 convergence loops per stage. For large/risky work, use up to 5. After the limit, stop and report the exact blocker instead of lowering the bar.

## Large/Risky Route

Use for production behavior, architecture, data, auth, security, money, migrations, broad UI flows, or ambiguous requirements.

Additional requirements:

- Consider a worktree before implementation.
- Use plan-marked parallelism only.
- Consider bridge-based external review when Claude/Codex is already available in the same tmux session.
- Add browser QA for UI/web work.
- Run full review and ship-readiness checks before acceptance.

## Learn

Run only after large, painful, surprising, or repeated work.

Capture:

- What assumption was wrong?
- What review or test caught the issue?
- What should be added to future Frame, Plan, Build, Review, or Accept behavior?
- Should this skill collection be updated?
