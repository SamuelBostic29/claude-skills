---
name: ai-next
version: 1.0.0
description: |
  Work the next open item in an AI-review triage list produced by /ai-comments: present
  the finding, implement the proposed fix or record a deliberate defer/decline with its
  rationale, mark the checkpoint in the state file, and stop. One item per invocation.
  Use when the user says "/ai-next", "next AI comment", or "keep working the review list".
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
---

# AI Next: work one triaged AI-review item to its checkpoint

A triaged list of AI reviewer findings already exists in a local state file — /ai-comments
wrote it. Your job is to take exactly one OPEN item to its checkpoint: either the fix is
implemented, or a defer/decline decision is recorded with a rationale worth replying with.
Do not re-triage the list, and do not touch a second item — the whole point of checkpoints
is that each invocation ends at a clean, resumable boundary.

## When to use this skill

- "/ai-next" after /ai-comments has produced the state file
- "Work the next AI comment" / "keep going through the review items"
- Resuming the list in a fresh session (the state file carries all context)

## When NOT to use this skill

- No state file exists yet — run `/ai-comments` first.
- Drafting the reply text — that's `/ai-draft`, after items reach their checkpoints.
- Posting replies or watching CI — that's `/ai-post`.

## Steps

1. **Find the state file.** If a path was passed, use it. Otherwise glob
   `docs/plans/ai-review-pr-*.md`; exactly one → use it; several → ask via
   AskUserQuestion (newest first); none → say to run /ai-comments and stop.

2. **Read the whole file.** It is your only context — assume no prior conversation.

3. **Pick the first item whose Status is OPEN**, in file order. If none, report that
   every item is at its checkpoint, point to `/ai-draft`, and stop.

4. **Present the item** in the format below: category, source, confidence, the finding,
   the Why, and the Proposed solution.

5. **If the item is UNSURE**, settle it first: ask the open question via AskUserQuestion
   and re-categorize (update the item's category and add Why/Proposed solution) before
   going further.

6. **Choose the path.** Default for SHOULD FIX is implementing the proposed solution;
   nitpicks often warrant a quick fix or a decline. Confirm via AskUserQuestion when the
   call isn't obvious: **Fix** / **Defer or decline** (with the user supplying or
   confirming the rationale).

7. **Execute.**
   - **Fix:** read the code first, then implement. If the proposed solution turns out
     wrong once you're in the code, stop and say so — present the problem and the
     alternative, and let the user decide. Do not run the full test suite here;
     `/ai-post` gates on tests and lint before anything is posted.
   - **Defer / decline:** capture the real reason (from discussion or the user), specific
     enough to become a reply — "deferring: this component never renders inside a form
     today; a follow-up story covers it" beats "won't fix".

8. **Record the checkpoint.** In the state file, set the item's Status to `FIXED`,
   `DEFERRED`, or `DECLINED`, and add `- **Resolution:** <1–2 factual sentences of what
   was done or why not>`. Touch nothing else in the file.

9. **Stop.** Report the checkpoint and how many items remain OPEN. Do not start the next
   item, draft replies, commit, or push.

## Output format

Presenting the item (step 4):

```
Item 3 of 7 — [SHOULD FIX] paging guard never fails fast   (Copilot, 93%)
File: src/api/selections.api.ts:41
Finding: <condensed comment>
Why: <grounded reason>
Proposed solution: <the concrete change>
```

Closing report (step 9):

```
Checkpoint: item 3 FIXED — <one-line resolution>. 4 items remain OPEN. Next: /ai-next
```

## Rules

### What to do

- **ONE item per invocation.** Hard cap. Ending at a checkpoint is the feature.
- **Items in file order** — the triage already sorted by priority.
- **Resolutions must be reply-grade.** /ai-draft builds the reply from your Resolution
  line; write it factual and specific.
- **Read code before changing it**, even when the proposed solution looks complete.

### What NOT to do

- **NEVER work past the checkpoint** — no second item, no reply drafting, no posting.
- **NEVER silently deviate from the proposed solution.** If it's wrong, stop and ask —
  the triage verdict was made with the user.
- **NEVER commit or push.** Changes stay in the working tree for /ai-post's gate.
- **Don't re-triage.** Categories and confidences are settled except for the one UNSURE
  item you were asked to resolve.

### Format discipline

- Present the item, do the work, report the checkpoint in one line — no recap of the
  whole list, no plan for the remaining items.
