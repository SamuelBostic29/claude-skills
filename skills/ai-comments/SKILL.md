---
name: ai-comments
version: 1.0.0
description: |
  Pull the AI reviewer comments (GitHub Copilot inline comments + Claude review-bot
  comments) from a pull request and triage them into a worked list: categorize each
  finding as SHOULD FIX or NITPICK with a confidence rating, ask about anything under
  85% confidence, and save the list to a local state file for /ai-next to work through.
  Use when the user says "pull the AI comments", "triage the copilot/claude comments",
  "/ai-comments", or pastes a PR link asking to go through the AI review feedback.
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

# AI Comments: triage AI reviewer feedback on a PR into a worked list

A PR has accumulated review comments from AI reviewers (GitHub Copilot and a Claude
review bot) and the user wants them triaged once instead of re-explaining the drill
every session. Your job is to fetch every open AI comment, actually understand the
code each one touches, categorize each finding with an honest confidence rating, and
write the result to a local state file. The classic failure mode is shallow triage —
categorizing from the comment text alone without reading the code, which produces
confident-sounding but wrong verdicts. Read the code first, always. You triage only;
fixing starts with /ai-next.

## Configuration (set per adopter)

| Key | Default | Used for |
| --- | --- | --- |
| `AI_STATE_DIR` | `docs/plans/ai-review/` | Where state files live. Point at a global folder (outside any repo) to keep them long-term across repos. |

State file path: `{AI_STATE_DIR}/{repo}-pr-{n}.md`.

## When to use this skill

- "Pull / triage / categorize the AI comments" on a PR
- A PR link or number is pasted with intent to work through its review feedback
- After an AI re-review lands new comments on a PR already being worked (re-run to merge them in)

## When NOT to use this skill

- Working through an already-triaged list — use `/ai-next`.
- Drafting or posting replies — use `/ai-draft` / `/ai-post`.
- Reviewing the PR yourself — this skill only ingests *other* reviewers' AI comments.
- Human reviewer comments — use `/hum-comments`; the queues stay separate.

## Steps

1. **Resolve the PR.** If a PR URL or number was passed, use it. Otherwise `gh pr view`
   for the current branch. If neither resolves to a PR, ask via AskUserQuestion and stop.

2. **Fetch the AI comments.** Two sources:
   - **Copilot (inline):** `gh api repos/{owner}/{repo}/pulls/{n}/comments` — keep
     comments whose author is `Copilot`; record each comment's `id`, `path`, and line.
   - **Claude (issue-level):** `gh pr view {n} --json comments` — keep comments whose
     author is the Claude review bot (typically `claude`) containing a `### Code Review`
     section. One Claude review usually contains several findings — split it: **one
     finding = one item**.
   Ignore everything else: human reviewers, CI bots, coverage/security scanners.

3. **Drop what's already handled.** Skip: inline threads where the PR author has already
   replied; Claude findings that a *later* incremental Claude review says are resolved
   (parse reviews newest-first — the latest review is authoritative). If the state file
   from a previous run exists, merge: add only items whose comment id isn't already
   listed, and never change existing items' statuses.

4. **Understand each finding.** Read the code the comment points at — the file, the
   surrounding function, and the tests that cover it. For findings about shared code or
   behavior claims (callers, blast radius, "this breaks X"), get the full picture: if a
   call-trace skill is installed, invoke it; otherwise trace callers/callees manually
   with Grep/Read. Do not categorize from the comment text alone.

5. **Categorize with confidence.** For each finding assign **SHOULD FIX** or **NITPICK**
   plus a confidence percentage that the categorization is right. Under 85% → the item
   is **UNSURE**. Every SHOULD FIX must carry a **Why** (grounded in the code you read)
   and a concrete **Proposed solution**.

6. **Resolve UNSURE items by asking.** For each UNSURE item, ask the specific question
   that would settle it via AskUserQuestion (batch related ones). Re-categorize with the
   answers. Anything the user can't settle now stays UNSURE in the file.

7. **Write the state file** to `{AI_STATE_DIR}/{repo}-pr-{n}.md` (create the folder if
   missing) in the format below, items ordered SHOULD FIX → UNSURE → NITPICK, with the
   PR title, repo, and today's date in the header — these files are kept long-term.
   If `AI_STATE_DIR` is inside a repo, **never commit the file**.

8. **Stop.** Print the summary table (below) and point to `/ai-next` to start working
   the first item. Do not begin fixing anything.

## Output format

Chat summary, most important first:

```
Triaged PR #123 — 7 AI findings (4 should-fix, 2 nitpicks, 1 unsure) → <AI_STATE_DIR>/repo-pr-123.md

| # | Cat        | Source  | Conf | Finding                          |
|---|------------|---------|------|----------------------------------|
| 1 | SHOULD FIX | Copilot | 93%  | paging guard never fails fast    |
| ... |
Next: /ai-next
```

State file (`{AI_STATE_DIR}/{repo}-pr-{n}.md`) — the contract the whole suite reads:

```markdown
# AI Review — PR #123: <title>
<!-- ai-review suite state (/ai-comments → /ai-next → /ai-draft → /ai-post). Kept long-term — never commit, never prune. -->

- Repo: <owner>/<repo>
- PR: <url>
- Intake date: <yyyy-mm-dd>
- Head at last intake: <sha>

## Items

### 1. [SHOULD FIX] <short finding title>
- **Source:** Copilot (inline comment <id> on `<path>:<line>`)   <!-- or: Claude (issue comment <id>, finding "<label>") -->
- **Confidence:** 93%
- **Comment:** <the finding, condensed but faithful>
- **Why:** <why this is real, grounded in the code you read>
- **Proposed solution:** <concrete change>
- **Status:** OPEN
```

Later skills append to each item: `- **Resolution:**` + Status change (/ai-next),
`- **Draft reply:**` (/ai-draft), `- **Posted:** yes` (/ai-post). UNSURE items carry
`- **Open question:**` instead of Why/Proposed solution until resolved.

## Rules

### What to do

- **Read the code before categorizing — every item.** A verdict formed from comment text
  alone is the failure mode this skill exists to prevent.
- **One finding = one item.** Split multi-finding Claude reviews; each finding gets its
  own category, confidence, and eventual reply.
- **Honest confidence.** The number reflects your evidence, not your desire to avoid
  questions. Under 85% → UNSURE, no rounding up.
- **Every SHOULD FIX carries Why + Proposed solution.** No bare verdicts.
- **Merge, don't clobber.** On re-run, only append new items; existing statuses are
  /ai-next's territory.

### What NOT to do

- **NEVER ingest human comments.** AI reviewers only — humans go through /hum-comments.
- **NEVER start fixing.** Triage ends at the state file; /ai-next owns implementation.
- **NEVER commit the state file** (when it lands inside a repo) **and never prune it** —
  worked history stays; the files double as a long-term record.
- **Don't inflate the list.** A Claude review that says "no issues found" produces zero
  items, not a synthetic "looks good" entry.

### Format discipline

- Summary table first, no preamble, no restating each comment in chat — the detail lives
  in the state file. Stop after pointing to /ai-next.
