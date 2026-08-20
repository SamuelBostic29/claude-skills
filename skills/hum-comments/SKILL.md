---
name: hum-comments
version: 1.0.0
description: |
  Pull the HUMAN reviewer comments from a pull request and triage them into a worked
  list: categorize each as SHOULD FIX, NITPICK, or QUESTION with a confidence rating,
  ask about anything under 85% confidence, and save the list to the human-review state
  file for /ai-next to work through. Use when the user says "pull the human comments",
  "triage the reviewer feedback", "/hum-comments", or pastes a PR link asking to work
  through what human reviewers said.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
  - Edit
  - Bash(gh:*)
  - AskUserQuestion
  - Skill
---

# Hum Comments: triage human reviewer feedback on a PR into a worked list

A PR has review comments from human colleagues and the user wants them triaged into the
same checkpoint pipeline the AI comments go through (/ai-next → /ai-draft → /ai-post),
but kept in their own long-lived file. Your job is to fetch every open human comment,
actually understand the code each one touches, categorize it with an honest confidence
rating, and write the result to the human-review state file. Two things are different
from AI triage: humans ask real **questions** that deserve answers rather than fixes,
and these files are a **permanent archive** the user keeps for one-on-ones — you append
history, you never prune it. As with AI triage, the classic failure mode is categorizing
from the comment text alone — read the code first, always. You triage only; working the
items starts with /ai-next.

## Configuration (set per adopter)

| Key | Default | Used for |
| --- | --- | --- |
| `HUM_STATE_DIR` | `docs/plans/hum-review/` | Where state files live. Point at a global folder (outside any repo) to keep them long-term across repos. |

State file path: `{HUM_STATE_DIR}/{repo}-pr-{n}.md`.

## When to use this skill

- "Pull / triage the human reviewer comments" on a PR
- A PR link or number is pasted with intent to work through colleagues' feedback
- After new human comments land on a PR already triaged (re-run to merge them in)

## When NOT to use this skill

- AI reviewer comments (Copilot, Claude bots) — use `/ai-comments`; never mix the queues.
- Working through an already-triaged list — `/ai-next`; drafting/posting — `/ai-draft` / `/ai-post`.
- Reviewing the PR yourself — this skill only ingests reviewers' comments.

## Steps

1. **Resolve the PR.** If a PR URL or number was passed, use it. Otherwise `gh pr view`
   for the current branch. If neither resolves to a PR, ask via AskUserQuestion and stop.

2. **Fetch the human comments.** Three sources, keeping only comments by humans — not
   the PR author, not AI reviewers (Copilot / Claude bots), not CI or scanner bots:
   - **Inline:** `gh api repos/{owner}/{repo}/pulls/{n}/comments` — record each
     comment's `id`, `path`, and line.
   - **Review summaries:** `gh api repos/{owner}/{repo}/pulls/{n}/reviews` — reviews
     with substantive body text (skip empty approvals).
   - **Issue-level:** `gh pr view {n} --json comments`.

3. **Drop what's already handled.** Skip inline threads where the PR author has already
   replied. If the state file exists, merge: add only items whose comment id isn't
   already listed, and never change existing items' statuses or history.

4. **Understand each comment.** Read the code it points at — file, surrounding function,
   covering tests. For comments about shared code or behavior claims, get the full
   picture: invoke a call-trace skill if installed, otherwise trace manually with
   Grep/Read. A question ("why not use the existing endpoint?") needs the same grounding
   as a defect claim — the eventual answer must be code-accurate.

5. **Categorize with confidence.** Each comment gets **SHOULD FIX**, **NITPICK**, or
   **QUESTION** plus a confidence percentage that the categorization is right; under
   85% → **UNSURE**. SHOULD FIX carries a **Why** and a concrete **Proposed solution**;
   QUESTION carries **What they're asking** and, when the code answers it, a
   **Grounded answer draft** for the user to confirm at /ai-next.

6. **Resolve UNSURE items by asking** targeted questions via AskUserQuestion (batched).
   Re-categorize with the answers; what the user can't settle stays UNSURE.

7. **Write the state file** to `{HUM_STATE_DIR}/{repo}-pr-{n}.md` (create the folder if
   missing), same format as the AI queue (see /ai-comments) plus a `[QUESTION]` item
   shape, items ordered SHOULD FIX → QUESTION → UNSURE → NITPICK. Include the PR title,
   repo, reviewers, and today's date in the header — the file outlives the PR.

8. **Stop.** Print the summary table and point to `/ai-next`. Do not begin fixing or
   answering anything.

## Output format

Chat summary:

```
Triaged PR #12 — 5 human findings from 2 reviewers (2 should-fix, 2 questions, 1 nitpick) → <HUM_STATE_DIR>/repo-pr-12.md
| # | Cat        | Reviewer | Conf | Finding                    |
|---|------------|----------|------|----------------------------|
| 1 | SHOULD FIX | jsmith   | 90%  | list should be virtualized |
...
Next: /ai-next
```

Item shapes (full format spec lives in /ai-comments; QUESTION adds):

```markdown
### 3. [QUESTION] why a separate endpoint for selections?
- **Source:** jsmith (inline comment <id> on `<path>:<line>`)
- **Confidence:** 88%
- **Comment:** <the question, condensed but faithful>
- **What they're asking:** <the actual information sought>
- **Grounded answer draft:** <code-accurate answer, if the code settles it>
- **Status:** OPEN
```

## Rules

### What to do

- **Read the code before categorizing — every item**, questions included.
- **One comment = one item**, each with its reviewer named — the archive is also a
  record of who raised what.
- **Honest confidence.** Under 85% → UNSURE, no rounding up.
- **Merge, don't clobber.** These files are permanent — append new items, touch nothing
  historical.

### What NOT to do

- **NEVER ingest AI or bot comments** — that queue belongs to /ai-comments.
- **NEVER delete, prune, or rewrite existing file content.** The archive is the point.
- **NEVER start fixing or post an answer.** Triage ends at the state file.
- **Don't editorialize about reviewers.** Items record what was said and where it
  stands — no commentary on comment quality.

### Format discipline

- Summary table first, detail in the state file, stop after pointing to /ai-next.
