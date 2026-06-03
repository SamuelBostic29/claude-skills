# claude-skills

A growing collection of portable, high-quality [Claude Code](https://docs.claude.com/en/docs/claude-code) skills.

Every skill here is built to the same bar: **self-contained, opinionated, and convergent.** They do one thing well, give the model crisp decision rules instead of vague guidance, and carry no project-, company-, or machine-specific assumptions — so they drop into any repo and just work.

## Skills

| Skill | What it does |
|---|---|
| [`plan-save`](skills/plan-save) | Restructure a plan into a persistent, phase-tracked markdown file you can execute across sessions. |
| [`plan-next`](skills/plan-next) | Execute the next incomplete phase of a saved plan — implement it, update the file, then stop. |
| [`plan-review`](skills/plan-review) | A convergence-oriented review of a saved plan: verdict first, blockers capped, "I don't understand" routed to questions instead of nitpicks. |
| [`call-trace`](skills/call-trace) | Trace the full call chain in both directions — callers and callees — around a target, reading whole method bodies to build deep context before changing shared or foundational code. |
| [`dbcontext-query`](skills/dbcontext-query) | Generate EF Core data-access methods (get / list / add / update / remove / paginate) for an entity as a single `DbContext` partial class — follows your repo's conventions, with namespaces and base types left as placeholders to adapt. |
| [`dto-mapping`](skills/dto-mapping) | Generate a family of DTOs and hand-written mappers for a .NET entity — detail/list/reference reads, create/update inputs, and `ToDto()`-style mapping — recommending only the variants that fit and matching the codebase's existing conventions. |
| [`validator-generator`](skills/validator-generator) | Generate a FluentValidation validator for a .NET DTO or command (create / update / delete / shared-save / import), with rules grounded in the DTO's real properties and uniqueness checks routed through an abstraction you own. |
| [`add-data-access`](skills/add-data-access) | Scaffold the data-access layer for a resource — a typed model + repository/DAO, or one new method on an existing DAO — by mirroring the repo's nearest existing DAO. |
| [`add-service`](skills/add-service) | Scaffold the business-logic/service layer — a service that orchestrates repositories and applies rules — by mirroring the repo's nearest existing service. |
| [`add-controller`](skills/add-controller) | Scaffold the HTTP route/handler — request validation → service/DAO call → standardized response, with the repo's auth, error codes, and concurrency headers — by mirroring the nearest existing handler. |
| [`add-tests`](skills/add-tests) | Scaffold unit tests for a model, DAO, service, or handler by mirroring the repo's existing test style (framework, layout, mocking, fixtures) — never editing production code to pass. |
| [`draft-pr`](skills/draft-pr) | Finish a unit of work into a draft PR: stage **only the files changed this session** (never secret-bearing local config), commit, push, write a templated description, and open it as a draft. |
| [`pr-stats`](skills/pr-stats) | Summarize a GitHub user's pull-request activity over a time window into one markdown report — per-PR metadata, lines/files/commits, human-review-comment counts (bots filtered), and a summary of each linked issue. |
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
- **Portable.** No hardcoded paths, org names, or stack assumptions.

## License

[MIT](LICENSE) © Samuel Bostic
