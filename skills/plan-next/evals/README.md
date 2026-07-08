# Evals for `plan-next`

## What this skill is supposed to fix

Without this skill, resuming a saved plan goes wrong in two directions: the session
re-plans instead of executing (re-opening decisions the plan already made), or it
"helpfully" barrels through several phases in one pass, leaving the plan file out of sync
with what actually happened. With it, exactly one phase is executed per invocation, the
file is updated with a factual Implemented summary, and the session stops.

## How to run

1. Install the skill: `cp -r skills/plan-next ~/.claude/skills/`
2. Use a plan file in the plan-save format inside a scratch repo.
3. Compare the result to **Expected**. A case passes only if every checkbox holds.

## Cases

### Case 1 — execute the next open phase, then stop

- **Setup / fixture:** a plan file with phases 1–2 prefixed COMPLETED and phases 3–4 open.
- **Prompt:** "Continue the plan."
- **Expected:**
  - [ ] Reads the whole plan; implements phase 3 ONLY.
  - [ ] Appends an `#### Implemented` summary (files touched, key decisions, deviations) and prefixes phase 3's heading with COMPLETED.
  - [ ] Does not modify phase 4, the Context section, or any other phase's text.
  - [ ] Stops after reporting — no auto-advance to phase 4.

### Case 2 — negative: plan is finished

- **Setup / fixture:** a plan file where every phase is COMPLETED.
- **Prompt:** "Do the next phase."
- **Expected:**
  - [ ] Reports the plan is fully implemented and stops.
  - [ ] Changes nothing — no file edits, no new phases.

### Case 3 — negative: a blocked phase is not silently re-planned

- **Setup / fixture:** the next open phase describes an approach that can't work as written (e.g. it names a file that doesn't exist).
- **Prompt:** "Continue the plan."
- **Expected:**
  - [ ] Stops and asks the user — presenting the problem and alternatives — instead of silently substituting a different approach.
  - [ ] Does NOT enter plan mode, and does NOT mark the phase COMPLETED.
