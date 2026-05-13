---
name: mingjie-verify
description: Use after review and before acceptance to verify the user-visible or system-visible workflow, run UAT-style checks, and produce a fix plan for any gap.
---

# Mingjie Verify

Purpose: prove the requested outcome works, not just that code looks good.

Review asks "is this production-worthy?" Verify asks "does the user's goal actually work end to end?"

## Verification Tiers

- **Quick:** targeted tests and one smoke path.
- **Standard:** targeted tests, broader affected test suite, and the main workflow.
- **Strict:** standard plus edge cases, rollback checks, browser/API/CLI/manual UAT as applicable.

Use Intake and Plan to choose the tier. Large/risky work defaults to Standard or Strict.

## Required Output

- Goal being verified
- Commands or manual steps run
- Expected result
- Actual result
- Pass/fail
- If failed: smallest fix plan and whether it returns to Build or Plan

## Workflow Examples

- CLI: run the command from a clean cwd and inspect output/exit code.
- API: exercise request validation, persistence, and response shape.
- Web: open the app, interact with the primary flow, check console errors.
- Worker/job: enqueue or simulate the job and verify side effects.
- Migration: dry run or local rollback path; never production data.

## Rules

- Do not accept unit tests as workflow verification when the change affects a user/system path.
- Do not claim workflow success without fresh evidence.
- If workflow verification is unavailable, disclose the exact gap and risk.
- If verification fails, create a concrete fix plan; do not hand-wave.
- For Uber repos, route verification through `uber-dev:verify` when available; otherwise stop under Guard.
- End with a stage transition prompt. Usually suggest `mingjie-accept`; if verification fails, suggest `mingjie-build` with the fix plan.
