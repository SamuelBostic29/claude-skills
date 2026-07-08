# CLAUDE.md — claude-skills

A curated, **public** collection of portable Claude Code skills — the sharable
subset of a larger personal toolkit. Everything here is portfolio-grade and
org/machine-agnostic. Treat every change as public-facing.

## Quality bar (every skill, no exceptions)

- **One job.** A single, clear purpose — if the description needs "and", split it.
- **Decision rules, not vibes.** Hard caps, explicit "do X / NEVER Y", stop conditions.
- **Convergent.** Skills reduce churn; output is review-ready, never make-work.
- **Portable.** No org names, hosts, real paths, or machine specifics. Anything
  project-specific is a `<PLACEHOLDER>` or a Configuration-table entry the
  adopter fills in. Stack-specific skills (e.g. .NET) are labeled in the README.
- **Evals mandatory.** Every skill ships `evals/README.md` — 2–3 representative
  cases, at least one negative ("should not fire / should ask instead").
- **Frontmatter:** `name` equals the folder name; `description` leads with the
  trigger; `allowed-tools` is the minimal set (scope Bash to subcommands where
  possible).

## Workflow for adding or changing a skill

1. Brief it as a GitHub issue — this repo's issues are skill briefs.
2. Branch `skill/<name>` off `main`. Start from the template
   (`cp -r template skills/<name>`) or run the `skill-builder` skill.
3. Add or update the skill's row in the README catalog, in the right group.
4. Run `python scripts/validate-skills.py` — it must exit 0 (CI runs it on
   every PR).
5. Open a draft PR (`Closes #<issue>`); merge only after review.

## Never

- Never commit `docs/plans/` (local planning docs), tokens, or local config.
- Never introduce org/employer specifics — this repo is public.
- Never ship a skill without evals, or with surviving `<ANGLE_BRACKET>`
  placeholders (`template/` is the one intentional exception).
