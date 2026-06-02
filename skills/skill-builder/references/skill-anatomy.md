# Skill anatomy — the structure and bar a new skill must meet

## When to read this

Step 2 of `skill-builder` sends you here: read it before scaffolding so the skill you emit is correct-by-construction. The canonical scaffold is `template/` in the claude-skills repo — if it's present, copy it. This file is the portable equivalent: it captures the same structure and the quality bar so the skill works even when `template/` isn't alongside you. If both exist and disagree, the live `template/` wins.

## The bar — three pillars

Every good skill clears all three:

1. **One job.** A single, clear purpose. If the description needs "and", split it into separate skills.
2. **Decision rules, not vibes.** Hard caps ("max 2 X"), explicit "do X / NEVER do Y", and stop conditions — not soft advice the model can rationalize around.
3. **Convergence.** The skill should *reduce* churn, not manufacture make-work. Output is review-ready, not a starting mess.

## Progressive disclosure — three layers

Load context only as needed:

- **Layer 1 — frontmatter (`name` + `description`).** Always preloaded for every installed skill. The `description` is the *only* thing Claude reads to decide whether to trigger. Lead with the trigger.
- **Layer 2 — the SKILL.md body.** Loaded when the skill fires. Keep it lean: the process, the rules, the output shape.
- **Layer 3 — `references/*.md`.** Loaded only when the body explicitly tells Claude to read them. This is where big catalogs, signature tables, and worked examples go — they cost zero context until needed.

## Frontmatter contract

```yaml
---
name: <kebab-case, identical to the folder name>
version: 1.0.0
description: |
  <Trigger first: WHEN Claude should fire this skill. Then WHAT it does.>
  <Concrete. No "helps with" / "assists" filler.>
allowed-tools:
  - <only the tools the job actually needs — minimal>
---
```

- **`name`** — lowercase-kebab, matches the folder exactly.
- **`description`** — trigger-first; this is the trigger signal, not a summary.
- **`allowed-tools`** — minimal. A read-only skill lists no `Write`/`Edit`/`Bash`. Scope `Bash` to subcommands when you can (e.g. `Bash(git status:*)` rather than a blanket `Bash`).

## Body contract — sections in order

1. **Title + opening frame.** A one-line title stating the single job, then 2–4 sentences that orient Claude: the situation when the skill fires, the single job, and — if there's a classic failure mode for this kind of task — **name it up front** (e.g. a review skill opens by naming the context-gap that yields nit-picky reviews; a commit skill opens with its safe-staging rule as the cardinal one), so Claude guards against it from the start.
2. **When to use this skill.** Crisp triggers, mirroring the description in list form.
3. **When NOT to use this skill.** Anti-triggers — just as important. Point to the other skill to use instead where relevant. Prevents misfires and scope creep.
4. **Steps.** Numbered, imperative, one action each, in order. Include explicit stop/ask conditions ("if X is ambiguous, ask via AskUserQuestion and stop"). End with an explicit **Stop** step stating what "done" is.
5. **Output format.** If the skill emits structured output, show the exact shape in a fenced block, most-important line first. If it edits files instead, spec the file format. If there's no fixed output, omit the section.
6. **Rules.** Where "decision rules over vibes" lives. Three sub-blocks with bold lead-ins:
   - **What to do** — rules and hard caps.
   - **What NOT to do** — the tempting-but-wrong behavior and the cardinal `NEVER`.
   - **Format discipline** — verdict-first / no preamble / stop when done.

## Evals contract

Every skill ships a way to prove it works (`evals/README.md`):

- 2–3 representative cases tied to the skill's rules / acceptance criteria.
- At least one **negative** case — "should NOT fire", or "asks instead of guessing". These are gold; they prove the skill knows its own boundaries.
- Each case: setup/fixture, the prompt, and an **Expected** checklist of observable properties of a correct run.

## Finished-skill checklist (the self-check)

Before reporting, confirm:

- [ ] **Zero surviving `<ANGLE_BRACKET>`** placeholders (portable mode).
- [ ] `name` is kebab-case and matches the folder name.
- [ ] `description` leads with the **trigger**, not a summary, and has no "helps with" filler.
- [ ] `allowed-tools` is **minimal** — every listed tool is used by a step; nothing extra.
- [ ] The skill does exactly **one job** (no "and").
- [ ] Steps are imperative, ordered, and end with an explicit **Stop**.
- [ ] `evals/README.md` has 2–3 cases including **≥1 negative** case.
- [ ] `references/` exists only if the skill genuinely needs a layer-3 catalog; otherwise omitted.
- [ ] **Portable** unless project mode was explicitly chosen — no org names, real paths, stack or schema assumptions.
