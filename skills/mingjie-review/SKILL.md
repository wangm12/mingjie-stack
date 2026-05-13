---
name: mingjie-review
description: Use after implementation and before acceptance to self-review, check plan compliance, inspect diff scope, run QA where relevant, and apply the senior-staff production-confidence gate.
---

# Mingjie Review

Purpose: decide whether the work is production-worthy.

**Before reviewing**: This stage requires the top-tier model + max effort (see Model Effort Policy in `mingjie-stack`). If the current model is not Claude Opus 4.7 effort:max (Claude Code) or gpt-5.5 effort:extra-high (Codex), stop and ask the user to switch via `/model` before continuing.

## Must Check

- Goal satisfied
- Plan/spec compliance
- Intake and Guard compliance
- Diff has no unrelated changes
- Tests/verification are meaningful
- Verification covers both focused checks and the full affected workflow when applicable
- Risks are handled or disclosed
- Bridge responses, if used, were read, verified locally, and not treated as proof by themselves
- Uber workflow skills were used when Intake marked the repo as Uber
- UI work has browser QA when relevant
- Context stayed focused: no broad unrelated rule loading, no unnecessary files, no accidental skill/plugin sprawl

## Pre-Landing Review Categories

- Data safety: SQL interpolation, unsafe DB writes, migrations, schema mismatches
- Concurrency: read-check-write races, non-atomic status transitions
- Security: shell injection, XSS, SSRF, auth/authz gaps, secret exposure
- LLM boundaries: validate LLM output before DB writes, network fetches, emails, tools, or vector storage
- Completeness: new enum/status/type handled by every consumer
- Performance: N+1 queries, blocking sync calls in async paths, avoidable O(n*m) view logic
- Frontend: console errors, broken flows, accessibility, responsive layout, visual regressions
- Distribution: CI, release artifacts, version/changelog/docs when relevant
- Ship path: local/GitHub/internal/Uber backend is correct and authorized
- Tests: happy path, negative path, regression coverage, meaningful assertions
- Workflow: complete user/system path still works, including integration boundaries between changed units

## Fix-First Heuristic

Auto-fix mechanical low-risk issues:

- Unused code introduced by the change
- Missing eager loading
- Stale docs/comments that contradict the change
- Path/version mismatches
- Named constants for repeated magic values

Ask before fixes that affect:

- Security posture
- User-visible behavior
- Data model
- Product/design decisions
- Large rewrites
- Removal of functionality

## Autopilot Review

When Autopilot is active:

- Run the review convergence loop automatically.
- Fix low-risk mechanical blocking issues automatically.
- Re-run relevant verification after each fix.
- Stop and report blocked for product, security, data, public API, or large rewrite issues that exceed the stated scope.
- Use bridge review according to the active bridge policy, and verify accepted findings locally.
- Stop if an Uber repo used generic GitHub/PR/review/verify flow instead of required Uber skills.

## Production Confidence Gate

Ask:

> As a responsible senior staff software engineer, am I confident enough to ship this to production with minimal to no bugs?

If not an unqualified yes:

- Identify what is missing, fragile, or uncertain.
- Fix it or mark it blocked.
- Re-run verification.
- Ask the question again.

## Review Convergence Loop

Loop: `Target -> Critique -> Modify -> Verify -> Decide`.

Target:

- No blocking review findings remain.
- Required checks pass fresh.
- Complete workflow verification passes when the change affects an end-to-end path.
- Bridge/subagent findings, if used, are resolved or explicitly deferred with rationale.
- Remaining risks are non-blocking and disclosed.
- The production confidence gate is an unqualified yes, or the work is reported blocked.

Process:

1. Critique the implementation using the categories above.
2. Classify findings as blocking or non-blocking.
3. Auto-fix low-risk mechanical blocking issues.
4. For non-mechanical blocking issues, fix only when the task scope allows it; otherwise report blocked.
5. Re-run the relevant verification.
6. Repeat until target is reached or the loop limit is hit.

Loop limits:

- Normal work: up to 3 review loops.
- Large/risky work: up to 5 review loops.
- After the limit, stop and report blocked status with remaining blocking findings.

## QA Tiers

For UI/web work:

- **Quick:** critical/high functional bugs, console errors, broken primary flow
- **Standard:** quick + medium UX/accessibility/responsive issues
- **Exhaustive:** standard + cosmetic polish, performance, edge paths

QA must include real interaction when a browser/app is available: navigate, click/type through the critical flow, inspect console/network where practical, and capture before/after evidence for fixed UI bugs.

## Verification Loop

Choose the project-appropriate checks and run them fresh before acceptance:

- Build
- Type check
- Lint/format check
- Unit/integration tests
- Complete workflow test for the affected path: browser E2E, API flow, CLI end-to-end, worker/job flow, migration dry run, or manual smoke test with exact steps
- E2E/browser checks for critical UI flows
- Security/secret scan when relevant
- Diff review and changed-file review
- Bridge inbox/thread cleanup when cross-agent coordination was used
- Harness state/evidence updated when Harness is active

If any required check fails, stop and fix or report blocked status.

End with a stage transition prompt. Usually suggest `mingjie-verify`; if blocking issues remain, suggest `mingjie-build` or `mingjie-plan` with the exact reason.
