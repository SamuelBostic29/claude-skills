<!--
============================================================================
SKILL TEMPLATE  —  delete this comment block once you've filled things in.

Copy this whole folder to start a new skill:
    cp -r template skills/<your-skill-name>

This template encodes the repo's quality bar so a new skill starts
correct-by-construction. Three things make a skill good here:

  1. ONE JOB.        A single, clear purpose. If you need "and", split it.
  2. DECISION RULES. Hard caps and explicit "do X / never do Y" — not vibes.
  3. CONVERGENCE.    The skill should reduce churn, not manufacture make-work.

Structure follows PROGRESSIVE DISCLOSURE — load context only as needed:
  - Layer 1: the frontmatter below (name + description). ALWAYS preloaded.
  - Layer 2: this SKILL.md body. Loaded when the skill triggers. Keep it lean.
  - Layer 3: references/*.md. Loaded only when the body tells Claude to read them.

Anything <IN_ANGLE_BRACKETS> is a placeholder for you to fill in. Search the
file for "<" before you ship — no angle brackets should survive.
============================================================================
-->
---
name: <skill-name>
# ^ lowercase-kebab-case, matches the folder name. This is part of layer-1
#   metadata and helps Claude decide when to trigger the skill.

version: 0.1.0

description: |
  <One or two sentences: WHAT this skill does AND WHEN Claude should use it.>
  <The description is the ONLY thing preloaded for every installed skill, and
   it is what Claude reads to decide whether to trigger this skill. Lead with
   the trigger condition. Be concrete. Avoid "helps with" / "assists" filler.>

allowed-tools:
  # Minimal set ONLY — list the exact tools this skill needs, nothing more.
  # A read-only skill should never list Write/Edit/Bash. Delete this comment
  # and the unused entries below.
  - Read
  - Grep
  - Glob
  # - Write
  # - Edit
  # - Bash
  # - AskUserQuestion
  # - Task
---

# <Skill Name>: <one-line statement of the single job>

<!--
Opening frame: orient Claude in 2-4 sentences. State the situation it's in
when this skill fires, the single job, and — if there's a classic failure mode
for this kind of task — name it up front (the plan-review skill opens by naming
the context-gap that causes bad reviews). Delete this comment.
-->
<You are about to .... Your job is to ....  Do X, then STOP — do not Y.>

## When to use this skill

<!-- Crisp triggers. Mirror the description but in list form. -->
- <Trigger 1>
- <Trigger 2>

## When NOT to use this skill

<!-- Just as important. Prevents misfires and scope creep. -->
- <Anti-trigger 1 — "use <other-skill> instead">
- <Anti-trigger 2>

## Steps

<!--
Numbered, imperative, in order. Each step is one action. Include EXPLICIT
stop conditions ("if X, ask the user and stop"). Never let the model guess
when it's blocked — route to AskUserQuestion. End with an explicit "Stop."
-->

1. **<First action.>** <Detail. What to read first, what to look for.>

2. **<Next action.>** <Detail.>

3. **<...>**

N. **Stop.** <State exactly what "done" is and that the skill does not continue past it.>

## Output format

<!--
If the skill produces structured output, show the EXACT shape in a fenced
block — verdict/result first. If it edits files instead, replace this section
with the file-format spec. If it produces no fixed output, delete this section.
-->

```
<Show the literal output structure here. Put the most important line first.>
```

## Rules

<!--
This is where "decision rules over vibes" lives. Use bold lead-ins. Prefer
hard caps and "NEVER / Do NOT" over soft advice. If the skill makes judgment
calls, give it a "what to flag / what NOT to flag" pair so the boundary is
explicit. Keep universal opinions framed as configurable, not law.
-->

### What to do

- **<Rule.>** <Why, briefly.>
- **<Hard cap, if any.>** <e.g. "Max 2 X. Hard cap — pick the two most important.">

### What NOT to do

- **<Anti-rule.>** <The tempting-but-wrong behavior, and what to do instead.>
- **NEVER <the cardinal sin for this skill>.**

### Format discipline

- <No preamble / no recap / verdict-first / stop when done — whatever keeps the output tight.>

<!--
LAYER 3 — PROGRESSIVE DISCLOSURE
If this skill needs a big catalog, signature reference, or worked examples,
DO NOT inline them here. Put them in references/ and point to them so they
load only when needed, e.g.:

    For the full <thing> catalog, read `references/<thing>-catalog.md`.

Delete references/ entirely if the skill doesn't need it. Likewise keep evals/
and fill it in — every skill in this repo ships a way to prove it works.
-->
