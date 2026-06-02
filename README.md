# claude-skills

A growing collection of portable, high-quality [Claude Code](https://docs.claude.com/en/docs/claude-code) skills.

Every skill here is built to the same bar: **self-contained, opinionated, and convergent.** They do one thing well, give the model crisp decision rules instead of vague guidance, and carry no project-, company-, or machine-specific assumptions — so they drop into any repo and just work.

## Skills

| Skill | What it does |
|---|---|
| [`plan-save`](skills/plan-save) | Restructure a plan into a persistent, phase-tracked markdown file you can execute across sessions. |
| [`plan-next`](skills/plan-next) | Execute the next incomplete phase of a saved plan — implement it, update the file, then stop. |
| [`plan-review`](skills/plan-review) | A convergence-oriented review of a saved plan: verdict first, blockers capped, "I don't understand" routed to questions instead of nitpicks. |
| [`draft-pr`](skills/draft-pr) | Finish a unit of work into a draft PR: stage **only the files changed this session** (never secret-bearing local config), commit, push, write a templated description, and open it as a draft. |

More skills are in progress — see [the issues](../../issues) for the roadmap.

## Installing a skill

Skills live under `~/.claude/skills/` (available everywhere) or `<project>/.claude/skills/` (scoped to one repo). To install one:

```bash
# user-level (available in every project)
cp -r skills/plan-save ~/.claude/skills/
```

Claude Code picks it up automatically. Invoke it by name, or let it trigger from its `description`.

## Design principles

What every skill in this repo aims for:

- **One job, done well.** A single, clear purpose — no kitchen-sink skills.
- **Decision rules, not vibes.** Hard caps, explicit "what to flag / what not to flag," verdict-first output.
- **Convergent, not noisy.** Built to reduce churn and make-work, not generate it.
- **Portable.** No hardcoded paths, org names, or stack assumptions.

## License

[MIT](LICENSE) © Samuel Bostic
