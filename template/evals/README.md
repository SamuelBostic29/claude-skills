# Evals for `<skill-name>`

<!--
============================================================================
Every skill in this repo ships a way to PROVE it works. Evals are to skills
what unit tests are to code: a small set of representative tasks plus a clear
description of what a correct run looks like.

You don't need a framework. A markdown checklist + a tiny fixture is enough.
Fill in the sections below, then delete this comment block.

Workflow (evaluation-driven authoring):
  1. Name the gap the skill closes (what does Claude get wrong without it?).
  2. Write 2-3 representative tasks that expose that gap.
  3. Build the skill.
  4. Run each task WITH the skill installed and check it against "Expected".
  5. Iterate on SKILL.md until every case passes.
============================================================================
-->

## What this skill is supposed to fix

<One or two sentences: the capability gap. "Without this skill, Claude does X
(wrong). With it, Claude should do Y.">

## How to run

1. Install the skill: `cp -r skills/<skill-name> ~/.claude/skills/`
2. In a fresh session, run each case below against the matching fixture (if any
   — put fixtures under `evals/fixtures/`).
3. Compare the result to **Expected**. A case passes only if every checkbox holds.

## Cases

### Case 1 — <short name>

- **Setup / fixture:** <link to fixture, or the prompt to paste>
- **Prompt:** "<what you ask>"
- **Expected:**
  - [ ] <observable property of a correct run>
  - [ ] <another — tie these to the SKILL.md Rules / acceptance criteria>
  - [ ] <e.g. "did NOT do <the failure mode>">

### Case 2 — <short name>

- **Setup / fixture:** <...>
- **Prompt:** "<...>"
- **Expected:**
  - [ ] <...>

### Case 3 — <edge case / negative case>

<!-- A "should NOT fire" or "should ask instead of guessing" case is gold here. -->

- **Setup:** <...>
- **Expected:**
  - [ ] <e.g. "skill recognizes it doesn't apply and defers" / "asks the user rather than guessing">
