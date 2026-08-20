# Evals for `ai-next`

## What this skill is supposed to fix

Without this skill, working through a triaged AI-review list sprawls: Claude fixes three
items in one pass, drafts replies mid-fix, or loses the list across /clear. With it, each
invocation takes exactly one item to a clean checkpoint (implemented, or deferred with a
reply-grade rationale) recorded in the state file, so the list survives sessions.

## How to run

1. Install the skill: `cp -r skills/ai-next ~/.claude/skills/`
2. Create a fixture state file at `{AI_STATE_DIR}/<repo>-pr-999.md` for a scratch repo,
   following the format in `skills/ai-comments/SKILL.md`, with 3 items: one SHOULD FIX
   (OPEN), one UNSURE (OPEN), one NITPICK (OPEN). (For case 4, also a
   `{HUM_STATE_DIR}/<repo>-pr-999.md` with one OPEN QUESTION item.)
3. In a fresh session, run each case. A case passes only if every checkbox holds.

## Cases

### Case 1 — fix path, one item only

- **Setup / fixture:** the 3-item state file; item 1 is a SHOULD FIX whose proposed
  solution is a small, real code change in the fixture repo.
- **Prompt:** "/ai-next"
- **Expected:**
  - [ ] Finds the state file without being given a path
  - [ ] Presents item 1 (category, source, confidence, why, proposed solution) before acting
  - [ ] Implements the fix after reading the affected code
  - [ ] Sets item 1 Status to FIXED and adds a 1–2 sentence factual Resolution line
  - [ ] Items 2 and 3 are untouched; no reply drafted; nothing committed or pushed
  - [ ] Stops after reporting the checkpoint and the remaining-OPEN count

### Case 2 — UNSURE item routes to a question first

- **Setup / fixture:** state file where the first OPEN item is UNSURE with an
  `Open question:` line.
- **Prompt:** "/ai-next"
- **Expected:**
  - [ ] Asks the item's open question via AskUserQuestion before any implementation
  - [ ] Re-categorizes the item from the answer (adds Why/Proposed solution)
  - [ ] Then proceeds to fix or defer per the user's direction — still only this item

### Case 3 (negative) — all items at checkpoint

- **Setup:** state file where every item is FIXED/ANSWERED/DEFERRED/DECLINED.
- **Prompt:** "/ai-next"
- **Expected:**
  - [ ] Reports that all items are at their checkpoints and points to /ai-draft
  - [ ] Does NOT invent new work, re-open items, or start drafting replies itself

### Case 4 — both queues open → asks; QUESTION answered, no code touched

- **Setup:** both the AI and the human fixture files have OPEN items.
- **Prompt:** "/ai-next"
- **Expected:**
  - [ ] Asks which queue to work (AI vs human) instead of picking silently
  - [ ] If the human queue is chosen: the QUESTION item's answer is confirmed with the
        user and recorded as Status ANSWERED with the answer in the Resolution line
  - [ ] No code is changed for the QUESTION item; still one item per invocation
