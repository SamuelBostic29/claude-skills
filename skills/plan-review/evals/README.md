# Evals for `plan-review`

## What this skill is supposed to fix

Fresh-eyes plan reviews reliably produce a 6–8 item nit-list regardless of plan maturity —
re-raising deliberate scope cuts, dressing "I don't understand" up as findings, and never
converging. With this skill a review is verdict-first, hard-capped (max 2 blockers, max 2
questions), reads prior review entries so repeated rounds converge, and records itself in
the plan file.

## How to run

1. Install the skill: `cp -r skills/plan-review ~/.claude/skills/`
2. Use plan files in the plan-save format with the noted properties.
3. Compare the result to **Expected**. A case passes only if every checkbox holds.

## Cases

### Case 1 — first review of a plan with a real defect

- **Setup / fixture:** a plan with no `## Reviews` section and one genuine internal contradiction (phase 2 assumes something phase 4 reverses).
- **Prompt:** "Review the plan."
- **Expected:**
  - [ ] Output is exactly verdict / blockers / questions — no preamble, no plan recap, no polish list.
  - [ ] The contradiction is a blocker citing both phases; verdict is "don't execute".
  - [ ] At most 2 blockers and 2 questions, even if more candidates exist.
  - [ ] Appends a dated `### Review 1` record to the plan file.

### Case 2 — a later round converges instead of re-litigating

- **Setup / fixture:** a plan whose `## Reviews` section shows 2+ prior entries, including a concern that was answered by scoping it out.
- **Prompt:** "Give this plan another review."
- **Expected:**
  - [ ] Does not re-raise anything a prior entry shows was already raised or scoped out.
  - [ ] Gap-style concerns ("X isn't addressed") surface as questions, not blockers — or not at all.
  - [ ] The review record is appended with the next sequential number.

### Case 3 — negative: no manufactured findings on a mature plan

- **Setup / fixture:** a clean plan with 5+ prior reviews and nothing new wrong in the text.
- **Prompt:** "One more review before I execute."
- **Expected:**
  - [ ] Verdict "execute" with blockers "none" and questions "none" — it does not invent items to justify the round.
  - [ ] Still appends the (short) review record.
