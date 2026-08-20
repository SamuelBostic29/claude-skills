# Evals for `hum-comments`

## What this skill is supposed to fix

Without this skill, human reviewer feedback gets handled ad hoc while AI feedback flows
through the triage pipeline — and Claude, asked casually, mixes the two queues, answers
questions from the comment text without reading the code, or treats the state file as
disposable. With it, human comments get the same code-grounded triage into their own
long-lived archive file, with questions recognized as QUESTIONs rather than forced into
fix/nitpick shapes.

## How to run

1. Install the skill: `cp -r skills/hum-comments ~/.claude/skills/` (set `HUM_STATE_DIR`
   for your machine).
2. In a fresh session on a branch whose PR has human review comments (including at least
   one question) plus AI reviewer comments, run each case.
3. Compare to **Expected**. A case passes only if every checkbox holds.

## Cases

### Case 1 — full triage with a question

- **Setup / fixture:** a PR with inline human comments from ≥1 reviewer — at least one
  actionable suggestion and one pure question — plus Copilot/Claude comments.
- **Prompt:** "/hum-comments"
- **Expected:**
  - [ ] Only human comments become items; Copilot/Claude/bot comments are excluded
  - [ ] The question is categorized QUESTION with "What they're asking" and, where the
        code settles it, a code-grounded answer draft (visible Reads of the referenced code)
  - [ ] Items ordered SHOULD FIX → QUESTION → UNSURE → NITPICK, reviewer named per item
  - [ ] File written to `{HUM_STATE_DIR}/{repo}-pr-{n}.md` with PR title, repo,
        reviewers, and date in the header
  - [ ] Nothing fixed, nothing answered on the PR; ends with the table + /ai-next pointer

### Case 2 — re-run appends, archive untouched

- **Setup / fixture:** an existing state file with worked history (FIXED/ANSWERED items
  with Resolutions); the PR has one new human comment.
- **Prompt:** "/hum-comments"
- **Expected:**
  - [ ] Exactly one new item appended
  - [ ] Every existing item — statuses, resolutions, drafts — byte-identical
  - [ ] Nothing deleted or reorganized

### Case 3 (negative) — AI comments must not enter this queue

- **Setup:** a PR whose only unhandled comments are from Copilot and a Claude bot.
- **Prompt:** "/hum-comments"
- **Expected:**
  - [ ] Zero items created (no state file, or an unchanged one); reports there is no
        human feedback to triage and points to /ai-comments for the AI queue
  - [ ] Does NOT triage the AI comments "while it's here"
