# Evals for `skill-builder`

## What this skill is supposed to fix

Without this skill, going from "I have a recurring problem" to "I have a skill" is all manual: the user writes the prompts, explains the problem in full, and drives the research and template-filling by hand every time. With it, a one- or two-sentence brief (plus optional repo context) becomes a complete, review-ready skill — scoped to one job, every template layer filled, evals scaffolded — with no kitchen-sink sprawl and no surviving placeholders.

## How to run

1. Install the skill: `cp -r skills/skill-builder ~/.claude/skills/`
2. In a fresh session, run each case below (the prompt is inline; fixtures noted where needed).
3. Compare the result to **Expected**. A case passes only if every checkbox holds.

## Cases

### Case 1 — Reconstruct an existing skill from a one-line brief

The headline eval: given only a brief, the skill should produce something comparable to a skill that already exists in this repo (`plan-review`).

- **Setup / fixture:** none — just the prompt. (Optionally move `skills/plan-review/` out of view first so it can't simply be copied.)
- **Prompt:** "Build me a skill that reviews a saved plan with fresh eyes but keeps the review convergent — verdict first, a hard cap on blockers, and 'I don't understand' turned into questions instead of a fresh nit-list every round."
- **Expected:**
  - [ ] Asks only genuine clarifying questions — no padding (this brief is detailed, so likely few or none).
  - [ ] Produces `skills/<name>/SKILL.md` scoped to the single job "review a saved plan convergently".
  - [ ] `description` leads with the trigger; `name` matches the folder; `allowed-tools` is minimal.
  - [ ] Output format puts the verdict first and caps blockers (mirrors plan-review's decision rules).
  - [ ] `evals/README.md` exists with 2–3 cases including a negative case.
  - [ ] No surviving `<ANGLE_BRACKET>` placeholders.
  - [ ] Stops at scaffold — does NOT install, commit, or push.

### Case 2 — Project mode against a real repo

Exercises repo research + the project output mode.

- **Setup / fixture:** point it at any small real repo path on disk.
- **Prompt:** "In project mode, build a skill for <that repo> that <a single repo-specific task>. Bake in the repo's real paths and conventions."
- **Expected:**
  - [ ] Reads the repo (README, existing `.claude/skills/`, conventions) before scaffolding.
  - [ ] Confirms project mode (real paths allowed) rather than silently defaulting to portable.
  - [ ] Writes the skill to the target repo's `.claude/skills/<name>/`, not into this repo.
  - [ ] Bakes in the repo's real paths/conventions, yet still one job, minimal tools, with evals.
  - [ ] Stops at scaffold.

### Case 3 — Multi-job brief (negative: split, don't cram)

The "should not fire as-is / should ask" case — the gold one.

- **Setup:** none — just the prompt.
- **Prompt:** "Build a skill that formats my code, runs the test suite, and opens a PR."
- **Expected:**
  - [ ] Does NOT scaffold a single kitchen-sink skill doing all three.
  - [ ] Recognizes three jobs and proposes splitting into N named skills (and flags any job an existing skill already covers, rather than duplicating it).
  - [ ] Confirms which single skill to build first before scaffolding anything.
  - [ ] If the user instead clarifies it is really one job, scaffolds only that one.

## Optional: the bootstrap eval (meta)

A future case, not required for a first cut (issue #11 open question): give `skill-builder` a one-line brief describing *itself* and check that it reconstructs a comparable `skill-builder`. Delightfully meta; defer until the three cases above pass.
