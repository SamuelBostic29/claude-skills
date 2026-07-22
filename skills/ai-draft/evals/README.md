# Evals for `ai-draft`

## What this skill is supposed to fix

Without this skill, reply-writing sprawls: paragraphs where the reviewer needs a sentence,
wording that re-argues settled decisions, replies invented for items nobody resolved, or
replies posted straight to the PR without review. With it, each resolved item gets a
1–2 sentence, resolution-grounded draft saved to the state file and shown for review.

## How to run

1. Install the skill: `cp -r skills/ai-draft ~/.claude/skills/`
2. Create a fixture state file at `docs/plans/ai-review-pr-999.md` (format in
   `skills/ai-comments/SKILL.md`) with: one FIXED item with a specific Resolution, one
   DEFERRED item with a rationale Resolution, one OPEN item, and one FIXED item that
   already has a `Draft reply:` line.
3. In a fresh session, run each case. A case passes only if every checkbox holds.

## Cases

### Case 1 — batch draft for resolved, undrafted items

- **Setup / fixture:** the 4-item state file above.
- **Prompt:** "/ai-draft"
- **Expected:**
  - [ ] Drafts exactly 2 replies (the FIXED and DEFERRED items without drafts)
  - [ ] Each reply is 1–2 sentences, leads with the outcome, first person, no AI attribution
  - [ ] Each reply's claims come only from that item's Resolution line
  - [ ] Drafts saved as `- **Draft reply:**` lines; nothing else in the file changed
  - [ ] The existing draft is not overwritten; the OPEN item gets no draft
  - [ ] Nothing is posted (no `gh` calls); ends by showing the batch and pointing to /ai-post

### Case 2 — vague Resolution routes to a question

- **Setup / fixture:** a state file whose only undrafted resolved item has
  `Resolution: handled it`.
- **Prompt:** "/ai-draft"
- **Expected:**
  - [ ] Does not embellish a reply from the vague line
  - [ ] Asks the user what was actually done (AskUserQuestion) before drafting

### Case 3 (negative) — nothing resolved yet

- **Setup:** state file where every item is OPEN.
- **Prompt:** "/ai-draft"
- **Expected:**
  - [ ] Drafts nothing and does not resolve items itself
  - [ ] Reports that no items are at a checkpoint and points to /ai-next
