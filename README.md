# claude-skills

[![validate-skills](https://github.com/SamuelBostic29/claude-skills/actions/workflows/validate.yml/badge.svg)](https://github.com/SamuelBostic29/claude-skills/actions/workflows/validate.yml)

A curated collection of portable, high-quality [Claude Code](https://docs.claude.com/en/docs/claude-code) skills — the sharable subset distilled from a larger personal toolkit.

Every skill here is built to the same bar: **self-contained, opinionated, and convergent.** They do one thing well, give the model crisp decision rules instead of vague guidance, and carry no company- or machine-specific assumptions — so they drop into any repo and just work. Skills that target a specific stack (currently .NET) are labeled as such.

## Skills

### Planning

| Skill | What it does |
|---|---|
| [`plan-save`](skills/plan-save) | Restructure a plan into a persistent, phase-tracked markdown file you can execute across sessions. |
| [`plan-next`](skills/plan-next) | Execute the next incomplete phase of a saved plan — implement it, update the file, then stop. |
| [`plan-review`](skills/plan-review) | A convergence-oriented review of a saved plan: verdict first, blockers capped, "I don't understand" routed to questions instead of nitpicks. |
| [`plan-from-issue`](skills/plan-from-issue) | Turn a GitHub issue (plus an optional story ticket) into a saved, phase-structured implementation plan — fetch the issue, synthesize the ask, ground it in code via `call-trace`, persist via `plan-save`. |

### Code understanding & review

| Skill | What it does |
|---|---|
| [`call-trace`](skills/call-trace) | Trace the full call chain in both directions — callers and callees — around a target, reading whole method bodies to build deep context before changing shared or foundational code. |
| [`review-session`](skills/review-session) | Spin up a fresh, interactive Claude Code session in a separate terminal to cold-review the whole branch — every commit over the base plus uncommitted edits — with zero context from the work that produced it. |

### Delivery workflow

| Skill | What it does |
|---|---|
| [`draft-pr`](skills/draft-pr) | Finish a unit of work into a draft PR: stage **only the files changed this session** (never secret-bearing local config), commit, push, write a templated description, and open it as a draft. |
| [`pr-stats`](skills/pr-stats) | Summarize a GitHub user's pull-request activity over a time window into one markdown report — per-PR metadata, lines/files/commits, human-review-comment counts (bots filtered), and a summary of each linked issue. |
| [`pr-comments`](skills/pr-comments) | Triage a PR's review feedback — including AI-reviewer comments — into a judged task list: every item checked against repo facts and verdicted ACT / DISMISS / HUMAN with cited evidence. Never posts, never fixes. |
| [`jira-dc`](skills/jira-dc) | Operate on a single Jira **Data Center** ticket over the DC REST API — read, comment, assign, transition, create — with a per-user PAT in a gitignored token file, stdin-fed auth that never hits argv, and every write drafted + confirmed before sending. |

### Code generation (.NET)

| Skill | What it does |
|---|---|
| [`dto-mapping`](skills/dto-mapping) | Generate a family of DTOs and hand-written mappers for a .NET entity — detail/list/reference reads, create/update inputs, and `ToDto()`-style mapping — recommending only the variants that fit and matching the codebase's existing conventions. |
| [`validator-generator`](skills/validator-generator) | Generate a FluentValidation validator for a .NET DTO or command (create / update / delete / shared-save / import), with rules grounded in the DTO's real properties and uniqueness checks routed through an abstraction you own. |

### Meta

| Skill | What it does |
|---|---|
| [`skill-builder`](skills/skill-builder) | Turn a brief problem statement into a complete, repo-quality skill built from the template — scoped to one job, every layer filled, evals stubbed — then stop for review. |

## Installing a skill

Skills live under `~/.claude/skills/` (available everywhere) or `<project>/.claude/skills/` (scoped to one repo). To install one:

```bash
# user-level (available in every project)
cp -r skills/plan-save ~/.claude/skills/
```

Claude Code picks it up automatically. Invoke it by name, or let it trigger from its `description`.

## Creating a new skill

Start from the template — it's pre-structured for the quality bar below, so a new skill begins correct-by-construction:

```bash
cp -r template skills/<your-skill-name>
```

The template ([`template/`](template)) lays out the three layers of **progressive disclosure** — annotated frontmatter and instructions in `SKILL.md`, an optional `references/` file for large content that loads only on demand, and an `evals/` slot so every skill ships a way to prove it works. Fill in the `<ANGLE_BRACKET>` placeholders, delete what you don't need, and you've got a skill that matches the rest of the repo.

Prefer to automate it? The [`skill-builder`](skills/skill-builder) skill does all of this from a one-line problem statement — researching the repo, scoping to one job, filling every layer, and stubbing evals — then stops for review.

## Design principles

What every skill in this repo aims for:

- **One job, done well.** A single, clear purpose — no kitchen-sink skills.
- **Decision rules, not vibes.** Hard caps, explicit "what to flag / what not to flag," verdict-first output.
- **Convergent, not noisy.** Built to reduce churn and make-work, not generate it.
- **Portable.** No hardcoded paths, org names, or machine specifics — and stack-specific skills say so up front.

## License

[MIT](LICENSE) © Samuel Bostic
