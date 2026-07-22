# Evals for `ai-comments`

## What this skill is supposed to fix

Without this skill, every session starts with re-dictating the same drill: "pull the AI
comments from Copilot and Claude, understand the code, categorize should-fix vs nitpick,
rate confidence, ask about the uncertain ones." Claude also tends to categorize from the
comment text alone (shallow triage) and to mix human comments in. With it, one invocation
produces a code-grounded, confidence-rated item list in a local state file.

## How to run

1. Install the skill: `cp -r skills/ai-comments ~/.claude/skills/`
2. In a fresh session inside a repo whose branch has an open PR with AI review comments,
   run each case below.
3. Compare the result to **Expected**. A case passes only if every checkbox holds.

## Cases

### Case 1 — full triage of a live PR

- **Setup / fixture:** a checked-out branch with an open PR carrying ≥1 Copilot inline
  comment and ≥1 Claude review comment with multiple findings, plus at least one human
  reviewer comment.
- **Prompt:** "/ai-comments"
- **Expected:**
  - [ ] Resolves the PR from the current branch without being given a number
  - [ ] Reads the code each comment points at before categorizing (visible Read/Grep of
        the referenced files, not just the comment bodies)
  - [ ] The multi-finding Claude review is split into one item per finding
  - [ ] Every SHOULD FIX item has Source, Confidence, Why, and a concrete Proposed solution
  - [ ] Human reviewer comments do NOT appear as items
  - [ ] State file written to `docs/plans/ai-review-pr-<n>.md`, items ordered
        SHOULD FIX → UNSURE → NITPICK, all Status OPEN
  - [ ] No fix is implemented; ends with the summary table and a pointer to /ai-next

### Case 2 — low confidence routes to a question, not a guess

- **Setup / fixture:** a PR where at least one AI comment's validity depends on intent
  Claude can't verify from code (e.g. "is this endpoint supposed to be paginated?").
- **Prompt:** "/ai-comments <PR url>"
- **Expected:**
  - [ ] The ambiguous finding is rated under 85% and lands in UNSURE
  - [ ] A targeted AskUserQuestion is asked to settle it (not silently forced into
        SHOULD FIX or NITPICK)
  - [ ] If answered, the item is re-categorized using the answer; if not settled, it
        stays UNSURE with an `Open question:` line

### Case 3 (negative) — re-run merges instead of clobbering

- **Setup:** a state file from a prior run exists with one item already marked FIXED with
  a Resolution line; the PR has since gained one new Copilot comment.
- **Prompt:** "/ai-comments"
- **Expected:**
  - [ ] Only the new comment is appended as a new item
  - [ ] The FIXED item's status and Resolution are untouched
  - [ ] No duplicate items for comments already in the file
