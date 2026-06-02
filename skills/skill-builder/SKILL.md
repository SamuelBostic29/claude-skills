---
name: skill-builder
version: 1.0.0
description: |
  Turn a brief problem statement plus optional repo context into a complete,
  repo-quality skill scaffolded from the template. Use when asked to build,
  create, or scaffold a new skill, or when someone describes a recurring task
  they want handled as a reusable skill. Researches the repo, scopes to one
  job, fills every template layer, scaffolds evals — then stops for review.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
  - Edit
  - AskUserQuestion
---

# Skill Builder: turn a one-line brief into a review-ready skill

You are turning a brief problem statement into a finished, review-ready skill. Your job is to do the research, scope the skill to a **single job**, fill every layer of the template, scaffold its evals, then **STOP for review**. You never install, commit, or push what you scaffold.

The failure mode this skill exists to prevent is the **kitchen-sink skill**: a vague brief becomes a skill that tries to do three things, leads with "helps with" filler, lists every tool, and ships with half its `<ANGLE_BRACKET>` placeholders unfilled. Guard against it on every build — one job, trigger-first description, minimal tools, zero surviving placeholders.

## When to use this skill

- "Build / create / scaffold a skill for X"
- Someone describes a recurring task — usually with a repo or an example — and wants it turned into a reusable skill
- Turning a skill brief or issue (like this repo's issues) into an actual `skills/<name>/` folder

## When NOT to use this skill

- **Editing or reviewing an existing skill** — open it and edit it directly; this skill authors new ones.
- **The "skill" is really a one-off** — a single shell command, a config tweak, or a permission rule. Not every task needs a skill; say so and stop. (Settings or hook changes are a config task, not a skill.)
- **The brief implies several unrelated jobs** — that's N skills, not one. This skill builds one at a time; propose the split (step 5).

## Steps

1. **Intake.** Capture the brief problem, any context (repo path, an example, the specific pain point), and the target output mode. Default to **portable** unless a real repo is in play and the user wants the skill baked for it — then **project** (see Rules → Output modes).

2. **Read the anatomy.** Read `references/skill-anatomy.md` for the exact structure and quality bar you must produce. If `template/` exists in the working repo, that folder is your canonical starting scaffold (`cp -r template skills/<name>`); otherwise reproduce the same structure from the reference.

3. **Clarify — as much as it takes, no padding.** Ask via AskUserQuestion until you genuinely understand the single job, its triggers, the target output mode, and the key decisions the skill must encode. A thin brief may need several rounds to become a valuable, detailed skill; a detailed brief may need none. Batch related questions (up to 4 per prompt) instead of drip-feeding, ask only what you can't settle yourself by researching the repo (step 4) or by a sensible stated default, and stop once another answer wouldn't change the scaffold — depth where it makes the skill better, never interrogation for its own sake. **Never guess the skill's purpose** — that is the one thing you may not invent.

4. **Research.** If pointed at a repo, explore it with Read / Grep / Glob — README, any existing `.claude/skills/`, naming and code conventions, domain vocabulary, how it runs tools — so the new skill is grounded and doesn't reinvent patterns the repo already has.

5. **Scope to one job.** Distill the brief to a single crisp purpose. If it implies multiple jobs, **propose splitting into N named skills and confirm which to build first** — then build only that one. Do not scaffold until the scope is one job.

6. **Scaffold.** Create the skill folder — `skills/<name>/` (portable) or the target repo's `.claude/skills/<name>/` (project) — and fill **every** placeholder: kebab `name` matching the folder, trigger-first `description`, **minimal** `allowed-tools` inferred from the job, When to use / When NOT to use, numbered Steps with explicit stop conditions, Output format, and the Rules triad.

7. **Layer 3 + evals.** Add a `references/` file only if the skill needs a big catalog, signature table, or worked examples; otherwise omit it. **Always** write `evals/README.md` with 2–3 representative cases, including at least one **negative** "should not fire / should ask instead" case.

8. **Self-check.** Verify against the checklist in `references/skill-anatomy.md`: no surviving `<ANGLE_BRACKET>` (portable mode), `name` matches the folder, description leads with the trigger, `allowed-tools` is minimal, output is portable unless project mode was chosen. Fix anything that fails before reporting.

9. **Report & stop.** Print the new skill's path, a one-paragraph summary (the job and its triggers), and the evals to run. Do **not** install, commit, or push. Stop.

## Output format

Report exactly this, then stop:

```
Created skill: <path>/SKILL.md   (mode: portable | project)
Job: <one sentence — the single job this skill does>
Triggers: <when Claude should fire it>
Files: SKILL.md, evals/README.md[, references/<file>]
Verify with: <the eval case names from evals/README.md>

Not done for you: not installed, not committed.
To try it: cp -r <path> ~/.claude/skills/ and run the evals in a fresh session.
```

## Rules

### What to do

- **One job, always.** A skill has a single purpose. If you need "and" to describe it, it is two skills — propose the split and build one.
- **Trigger-first description.** Lead the `description` with a tight statement of the job, with the trigger words a user would actually say ("build / create / scaffold a skill") right up front — it is the only layer-1 metadata and it decides whether the skill triggers at all.
- **Minimal `allowed-tools`.** List only the tools the job needs. A read-only skill lists no `Write`/`Edit`/`Bash`. Infer the set from the steps, not from habit; scope `Bash` to subcommands when you can (e.g. `Bash(git status:*)`).
- **Ask until the job is clear — by sufficiency, not a quota.** Ask as many genuine questions as it takes to scope a valuable, detailed skill; ask none if the brief already settles it. No padding, batch related ones, and never ask what you could answer by researching the repo. Ask, don't guess.
- **Ship evals.** Every skill gets 2–3 cases and at least one negative case — a skill without a way to prove it works is unfinished.

### What NOT to do

- **NEVER ship a kitchen-sink skill.** Multi-job briefs get split, not crammed.
- **NEVER leave a surviving `<ANGLE_BRACKET>`** in portable output. The self-check exists to catch this.
- **NEVER guess the skill's purpose.** Ask, or stop — purpose is the one thing you may not invent.
- **NEVER install, commit, or push** the scaffold. The deliverable is files for review; landing them is the user's call.
- **Don't manufacture a skill for a one-off.** A single command or config change isn't a skill — say so and stop.

### Output modes

- **Portable (default).** Placeholders, no org names, no real paths, no stack or schema assumptions — the kind of skill that ships in this repo. Everything project-specific is an `<ANGLE_BRACKET>` the adopter fills in.
- **Project.** Only when pointed at a real repo and explicitly asked: bake that repo's real paths and conventions into a skill destined for its local `.claude/skills/`. The skill *itself* stays portable — the mode governs only the *output*.

### Format discipline

- The deliverable is the files plus a tight report. No preamble, no narrating the research, no recap. Scaffold, report, stop.

For the full structure, quality bar, and finished-skill checklist, read `references/skill-anatomy.md`.
