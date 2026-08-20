---
name: ai-draft
version: 1.0.0
description: |
  Draft the 1–2 sentence PR replies for review items already worked to a checkpoint by
  /ai-next — both the AI queue and the human queue: one reply per resolved item, written
  in the PR author's voice from the item's Resolution line, saved into the state file
  for review — never posted. Use when the user says "/ai-draft", "draft the replies",
  or "write up the responses to the review comments".
allowed-tools:
  - Read
  - Edit
  - Glob
  - AskUserQuestion
---

# AI Draft: write the replies for resolved review items

Review items — AI queue, human queue, or both — have been worked to their checkpoints;
each carries a Resolution line saying what was done, the settled answer, or why not.
Your job is to turn each resolved-but-undrafted item's resolution into a 1–2 sentence
reply the PR author would post, save it into its state file, and show the batch for
review. A draft is a draft: nothing gets posted here, and the decision in the Resolution
is settled — you write it up, you don't re-argue it.

## Configuration (set per adopter — must match the comments skills)

| Key | Default |
| --- | --- |
| `AI_STATE_DIR` | `docs/plans/ai-review/` |
| `HUM_STATE_DIR` | `docs/plans/hum-review/` |

## When to use this skill

- "/ai-draft" after /ai-next has taken items to their checkpoints
- "Draft the replies" / "write the responses to the review comments"

## When NOT to use this skill

- Items are still OPEN and undecided — work them with `/ai-next` first (drafting for an
  unresolved item is guessing).
- Actually posting the replies, running the test gate, or watching CI — that's `/ai-post`.
- Free-form PR comments unrelated to the triaged AI items.

## Steps

1. **Find the state file(s).** If a path or queue name (`ai` / `hum`) was passed, use
   it. Otherwise check both `AI_STATE_DIR` and `HUM_STATE_DIR` for files matching the
   current repo/PR and take every match — drafting covers both queues in one pass.
   None → say to run /ai-comments or /hum-comments and stop.

2. **Read each file.** Collect every item whose Status is FIXED, ANSWERED, DEFERRED, or
   DECLINED and which has no `Draft reply:` line yet. If there are none, report that
   (either nothing is resolved yet → point to /ai-next, or everything is already
   drafted → point to /ai-post) and stop.

3. **Draft one reply per item** — 1–2 sentences, hard cap, in the PR author's voice:
   - Lead directly with the substance — what changed, the answer, or the reason —
     never a status prefix like "Done —", "Fixed —", or "Good catch —". A deliberate
     defer/decline may still open with the intent ("Keeping this as-is
     intentionally: …") since that IS the substance.
   - FIXED items: state what changed, concretely ("switched to `import type
     { ComponentProps } from 'react'`, matching the shared components").
   - ANSWERED items (human questions): the reply IS the settled answer from the
     Resolution — direct and code-accurate, pointing at the file/ticket/doc that
     settles it when one exists.
   - DEFERRED/DECLINED items: state the real reason from the Resolution and, if the
     Resolution names one, when/where it will be handled instead.
   - Plain first person, no AI attribution, no thanks-for-the-feedback filler. Replies
     to humans are replies to colleagues — same brevity, collegial register ("You were
     right — …" over "Declined.").

4. **Save each draft** into its item as `- **Draft reply:** <text>`. Touch nothing else
   in the file.

5. **Show the batch** in the format below and stop. If any OPEN items remain, note the
   count. Do not post anything.

## Output format

```
Drafted 5 replies — 3 AI, 2 human   (1 item still OPEN — /ai-next)

AI queue (<AI_STATE_DIR>/repo-pr-123.md):
1. [FIXED] paging guard never fails fast (Copilot)
   → "The loop now tracks seen page tokens and throws on a repeat instead of spinning to MAX_PAGES."
2. [DEFERRED] ChipButton type prop ordering (Copilot)
   → "Intentionally deferring this one: the page is read-only today so ChipButton never renders inside a form; the upcoming create-flow story will move `type` after the spread."

Human queue (<HUM_STATE_DIR>/repo-pr-123.md):
3. [ANSWERED] why a separate endpoint for selections? (jsmith)
   → "There's already a dedicated `/v1/selections` endpoint with BE-side filtering — the include on the category fetch couldn't sort, so I switched to it."
...
Review the wording, then /ai-post when ready.
```

## Rules

### What to do

- **1–2 sentences per reply. Hard cap.** If it needs more, the Resolution line is doing
  too much — flag the item instead of writing a paragraph.
- **Ground every reply in the item's Resolution.** No claims that aren't in it; if a
  Resolution is too vague to draft from, ask the user rather than embellishing.
- **Match the register of the reviewer's finding** — technical, specific, direct.

### What NOT to do

- **NEVER prefix a reply with a status word** ("Done", "Fixed", "Good catch") — the
  reply text is the outcome; state it directly.
- **NEVER post.** No `gh` calls exist in this skill on purpose — /ai-post owns posting.
- **NEVER draft for an OPEN item** — that's deciding the resolution by stealth.
- **NEVER re-litigate the decision.** The checkpoint said DEFERRED; you don't argue it
  back to FIXED in the wording.
- **Don't overwrite an existing Draft reply** unless the user asks for a re-draft.

### Format discipline

- Output is the numbered draft list, nothing else — no restating each finding's history,
  no posting plan. Stop after showing the batch.
