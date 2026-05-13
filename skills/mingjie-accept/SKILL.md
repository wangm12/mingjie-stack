---
name: mingjie-accept
description: Use at the end of a task to report what changed, fresh verification evidence, remaining risk, and final state without claiming completion unless evidence supports it.
---

# Mingjie Accept

Purpose: make the final result state explicit.

## Required Report

- What changed
- What was verified
- Full workflow verification result, or why it was not applicable/available
- Intake/Guard summary when relevant
- Harness state/evidence path when used
- Bridge coordination summary, if used
- Convergence state: converged / blocked / deferred
- Autopilot state: not used / completed / stopped / blocked
- Ship state: not requested / local-only / pushed / PR-created / blocked
- Remaining risks or unverified areas
- Final state: done / PR-ready / blocked / abandoned / deferred
- Ship readiness for large/risky work

## Rules

- No completion claim without fresh verification evidence.
- No completion claim if a convergence loop ended with unresolved blocking criteria.
- If tests fail, report the failure and do not call the work complete.
- If the affected workflow was not verified end-to-end, disclose that as remaining risk unless it is genuinely not applicable.
- If verification was impossible, state exactly what was not verified and why.
- In Autopilot, explicitly state whether execution completed without interruption or stopped on a hard blocker.
- If an Uber repo was detected, state which `uber-dev:*` / `uber-reviewer:*` skills were used, or report blocked.
- For PR-ready work, include summary and test plan.
- For abandoned/deferred ideas, state the reason and the condition that would change the decision.

## Ship Readiness Checklist

For large/risky work:

- Base branch considered or updated when relevant.
- Tests/build/lint run fresh.
- Complete affected workflow verified, not only unit tests, or the unverified workflow risk is explicit.
- Plan completion checked.
- Plan/build/review convergence loops either reached target or reported blockers.
- Scope drift checked.
- Bridge threads marked done or remaining open messages reported when bridge coordination was used.
- Harness `.mingjie/STATE.md` and latest run evidence considered when Harness was active.
- Docs/changelog/release notes considered.
- PR/merge/deploy state is explicit.
- Context/tooling stayed lean; no unnecessary plugin/rule/skill installation was introduced.

## Lightweight Learning

Run only after large, painful, surprising, or repeated work.

Capture:

- What assumption was wrong?
- What review or test caught the issue?
- What should be added to future Frame, Plan, Build, Review, or Accept behavior?
- Should this skill collection be updated?
- Is the lesson project-specific or global?
- What evidence supports keeping this lesson?

Do not promote project lessons to user scope, org scope, or skill text without explicit approval.
