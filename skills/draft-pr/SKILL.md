---
name: draft-pr
version: 1.0.0
description: |
  Finish a unit of work into a draft PR: stage only the files changed in this
  session, commit, push, write a description from a configurable template, and
  open it as a draft. Use when asked to draft/open a PR or write up changes for
  review after finishing work on a branch.
allowed-tools:
  - Read
  - Grep
  - Glob
  - AskUserQuestion
  - Bash(git status:*)
  - Bash(git branch:*)
  - Bash(git checkout:*)
  - Bash(git add:*)
  - Bash(git commit:*)
  - Bash(git push:*)
  - Bash(git log:*)
  - Bash(git diff:*)
  - Bash(gh repo view:*)
  - Bash(gh pr create:*)
---

# Draft PR: stage the session's work, commit, push, and open a draft PR

You are wrapping up a unit of work into a pull request. Your job is to commit and push **only the files you changed during this working session**, write a clean description from the template below, and open the PR as a **draft**. You open drafts only — never mark ready, never merge.

The single most important rule of this skill is **safe staging** (see below). The user routinely has *other* locally-modified files — app-specific setup, local config, files containing secrets — that must never be committed. You stage by explicit path, only the files this session touched, and nothing else.

## When to use this skill

- "Draft a PR" / "open a draft PR" / "make a PR for what I just did"
- "Write up these changes for review" after finishing work on a branch

## When NOT to use this skill

- Marking a PR ready for review, or merging — this skill stops at draft.
- Reviewing someone else's PR.
- Committing without a PR, or committing files you didn't change this session.

## Safe staging (read first — this is the cardinal rule)

- **Stage only the files YOU created or edited during this session,** listed by explicit path. You know this set from your own edits this session.
- **NEVER** use `git add -A`, `git add .`, `git add -u`, or `git commit -a`. No blanket staging, ever.
- Run `git status --short` and compare. **Any modified/untracked file you did NOT touch this session is excluded** — do not stage it. These often hold secrets or local-only setup. Report them as left-untouched; never commit them.
- Even among files you touched, **never stage obvious secret/local-config files** (`.env`, `*.local.*`, `*.pem`, `*.key`, credential or `appsettings.*` files). If the work genuinely required changing one, **stop and ask** instead of staging it.
- If you're unsure whether a file belongs to this session's changeset, **exclude it and say so** — under-staging is safe, over-staging can leak.

## Steps

1. **Build the changeset.** List the exact files you created or edited this session. Run `git status --short` to see everything dirty, and split it into *this-session* (will stage) vs *other* (will not touch).

2. **Pick the branch.** Get the current branch (`git branch --show-current`). If it's the default branch (`main`/`master`), create a feature branch first (`git checkout -b <name>`) — derive a short kebab-case name from the work or ticket. Never commit the changeset directly onto the default branch.

3. **Stage explicitly.** `git add <path1> <path2> …` with the this-session paths only. Confirm with `git status --short` that nothing else got staged.

4. **Commit.** Write a descriptive message — an action-led subject line, plus (for non-trivial work) a short body of bullets covering *what changed and why*. This message is the **primary source for the PR's What Changed section**, so make it accurate and complete. No `Co-Authored-By` / AI attribution. Match the existing repo commit style if evident.

5. **Push.** `git push -u origin <branch>`.

6. **Report the changeset.** Tell the user exactly what was committed and what was deliberately left unstaged:
   ```
   Committed & pushed (N files): <paths>
   Left untouched (not part of this session): <paths or "none">
   ```

7. **Draft the description.** Build *What Changed* primarily from the commit message(s) on this branch (`git log <base>..HEAD`), reconciled against `git diff` so nothing is misstated or missed. Get the repo name (`gh repo view --json name --jq .name`), derive the issue link (see [Issue linking](#issue-linking-tracker-agnostic)), and ask the verification/testing type via AskUserQuestion (API · UI · data-migration · infra · none). For the testing-section formats, read `references/testing-variants.md` once the variant is known. Build the description from [Output format](#output-format).

8. **Open as a draft.** `gh pr create --draft --base <base> --head <branch> --title "<title>" --body-file <file>`. Always `--draft`. Report the PR URL and stop.

## Output format

The template is configurable; this is the default. Omit any section that doesn't apply.

```markdown
<issue-link line — see Issue linking; omit if none>

## What Changed

- <Action-led bullet — "Added…", "Switched…", "Removed…" — with the why when non-obvious>

## Review Focus

- <Where reviewers should look; dependencies on other PRs; auth/perf/edge-case concerns>

## Testing

<The variant chosen in step 7, formatted per references/testing-variants.md. Omit if "none".>
```

## Issue linking (tracker-agnostic)

1. Read the branch name and extract a ticket/issue number from common patterns — e.g. `feature/PROJ-123-...`, `123-short-desc`, `gh-123`, `<base>_<TICKET>-<n>`.
2. If the host is GitHub and the number is a repo issue, emit `Closes #<n>`.
3. For any other tracker, build the link from a **configurable** base URL the adopter sets — placeholder `<TRACKER_URL_BASE>` — e.g. `[Ticket](<TRACKER_URL_BASE>/<n>)`. **Never hardcode a tracker host, workspace ID, or org.**
4. If you can't confidently derive a number, ask the user or omit the line — don't guess.

## Rules

### What to do

- **Safe staging above all.** Explicit paths only; report what you excluded.
- **Branch off the default branch** before committing — never commit onto `main`/`master`.
- **Lead bullets with the action verb;** include motivation when it isn't obvious.
- **A few clear sentences per section.** No filler, no restating the ticket verbatim.
- **Ask the verification type before drafting,** so the Testing section is right the first time.

### What NOT to do

- **NEVER blanket-stage** (`git add -A`/`.`/`-u`, `commit -a`) or stage a file you didn't change this session.
- **NEVER stage secret/local-config files** — stop and ask if the work touched one.
- **NEVER mark the PR ready or merge it.** Draft only.
- **NEVER add `Co-Authored-By` or AI-attribution** lines to commits or the PR body.
- **No hardcoded org, team label, tracker URL/workspace, or real-world examples.** Everything project-specific is a `<PLACEHOLDER>`.

### Format discipline

- Report the changeset (committed vs left-untouched) plainly, then the PR URL. No preamble.
