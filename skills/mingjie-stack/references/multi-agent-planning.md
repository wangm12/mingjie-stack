# Multi-Agent Planning

Use this workflow when the user explicitly asks for multiple agents, plan debate, different planning personalities, or when large/risky/unknown work needs stronger planning pressure. This is a workflow layer over Claude Code and Codex, not a custom agent runtime.

```text
Intake -> Frame -> Multi-Agent Plan Drafts -> Synthesis -> Judge Final Plan -> Guard -> Build
```

## Runtime Model

- Use tmux panes as visible agent seats: Claude Code, Codex, and optionally shell.
- Let Claude Code and Codex use their native subagents when available.
- Treat all draft agents as advisory/read-only by default.
- Do not ask draft agents to edit files unless the judged final plan grants explicit disjoint ownership.
- Bridge replies are advice until the orchestrator verifies the relevant facts locally.

## Orchestrator Brief

Before dispatching drafts, the orchestrator prepares one shared brief:

```text
Goal:
Context:
Role:
Constraints:
Files:
Requested action:
Expected output:
```

The brief must include repo facts, relevant files, verification expectations, hard stops, out-of-scope items, and ship path. If Intake identifies an Uber repo, state that generic GitHub push/PR/review is prohibited and official `uber-dev:*` / `uber-reviewer:*` skills are required for diff, PR, review, verify, and ship.

## Draft Roles

- **Conservative Planner:** minimize risk, preserve reversibility, prefer small steps and proven patterns.
- **Aggressive Planner:** look for higher-leverage automation, challenge under-scoping, and expose bolder architecture options.
- **Pragmatic Planner:** choose the fastest reliable path, implementation order, dependencies, and cheapest useful verification.
- **Skeptic-Guard:** find hard stops, org/security/git/workflow risks, unsafe parallelism, and missing verification.

Each draft must output:

- Recommended approach
- Task breakdown
- Risks and hard stops
- Verification plan
- What another plan may miss
- Confidence level

## Synthesis And Judge

Synthesis merges agreements, names conflicts, adopts the strongest ideas, and rejects unsafe or over-scoped ideas with reasons.

The main orchestrator is the judge. It produces one final `mingjie-plan` before Build starts. The final plan must mark each task as sequential, parallel-safe, bridge-review-only, or native-subagent-allowed, and it must define exact ownership before any parallel implementation.

## Harness Artifacts

When Harness is active, write planning evidence under:

```text
docs/mingjie-stack/runs/<run-id>/multi-agent/
  BRIEF.md
  draft-conservative.md
  draft-aggressive.md
  draft-pragmatic.md
  draft-skeptic-guard.md
  synthesis.md
  final-plan.md
```

Project-scope facts and run evidence may be recorded automatically. User-scope, org-scope, or global skill learning still requires explicit approval.
