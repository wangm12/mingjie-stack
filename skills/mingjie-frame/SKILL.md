---
name: mingjie-frame
description: Use before planning or coding to clarify a rough idea, challenge assumptions from multiple perspectives, strengthen or shrink the idea, and decide whether to proceed, defer, or abandon.
---

# Mingjie Frame

Purpose: sharpen or reject the idea before planning.

## Required Output

- Goal
- Current idea quality: clear / rough / risky / probably wrong
- Assumptions
- Challenge from relevant perspectives
- Stronger version of the idea
- Reasons to abandon or defer
- Options
- Recommendation
- Success criteria
- Open questions

## Perspective Pool

Pick only relevant perspectives:

- User/customer
- Product/business
- Engineering
- Design/UX
- Security/privacy
- Operations
- Future maintainer
- Cost/time

## Rough-Idea Shaping

When the user has only a rough idea:

- Name the real pain or opportunity behind the feature request.
- Separate the user's wording from the actual job-to-be-done.
- Identify the narrowest useful wedge.
- Ask whether the idea should be strengthened, shrunk, deferred, or abandoned.
- If there is no clear user value or success test, stop before planning.

## Research And Reuse Check

Before recommending custom implementation for non-trivial work:

- Check whether the repo already has the pattern.
- Identify likely existing libraries, tools, MCPs, or skills that solve most of the problem.
- Prefer adopting, wrapping, or porting a proven approach over inventing one.
- If online or vendor docs are needed for current behavior, use primary sources.

## Rules

- Do not blindly agree.
- If the idea is weak, say so.
- If a simpler path exists, recommend it.
- If the best answer is abandon or defer, say that clearly.
- Ask only questions that materially affect the direction.
- Do not implement from Frame.

## Autopilot Framing

When Autopilot is active:

- State assumptions explicitly and proceed without asking confirmation.
- Ask only when the answer can change product behavior, data safety, security posture, public API, or user-visible outcome.
- Convert non-material open questions into documented assumptions with a one-line rationale; carry them into the plan as accepted risk.
- If the idea has no clear user value or success test, stop as blocked instead of inventing one.
- If Frame concludes abandon or defer, stop and report that final state; do not auto-continue to Plan.
