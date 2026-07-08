# Evals for `pr-comments`

## What this skill is supposed to fix

Without this skill, PR review feedback — AI-reviewer feedback especially — gets treated as
either gospel (every comment "fixed", including the wrong ones) or noise (all of it skimmed
and ignored). With it, every unresolved comment gets a grounded verdict backed by repo
evidence: ACT with a concrete fix, DISMISS with the fact that refutes it, or HUMAN with the
question a person needs to decide — and nothing is posted or changed.

## How to run

1. Install the skill: `cp -r skills/pr-comments ~/.claude/skills/`
2. In a fresh session inside a repo clone with `gh` authed, run each case.
3. Compare the result to **Expected**. A case passes only if every checkbox holds.

## Cases

### Case 1 — triage a reviewed PR with mixed-quality feedback

- **Setup / fixture:** an open PR with review feedback (AI or human) containing at least one comment that is correct and one that is refutable from the code.
- **Prompt:** "Pull the comments from my PR and work through them."
- **Expected:**
  - [ ] Resolves the PR from the current branch without asking.
  - [ ] Collects review bodies, inline comments, conversation comments, AND the GraphQL thread-resolution map — resolved threads are dropped, not guessed.
  - [ ] The valid item is ACT with a concrete one-line fix; the refutable item is DISMISS citing the refuting `file:line`.
  - [ ] Output matches the triage format with counts and a suggested order.
  - [ ] Nothing posted to GitHub, no files edited.

### Case 2 — judgment needs intent context

- **Setup / fixture:** a PR where one comment questions whether the change matches the feature's intent (not a mechanical code issue).
- **Prompt:** "Go through the review feedback on PR #<n>."
- **Expected:**
  - [ ] Reads the PR description and any linked issue before verdicting that item.
  - [ ] If intent is still genuinely ambiguous, the verdict is HUMAN with a crisp question — not a guessed ACT/DISMISS.

### Case 3 — negative: asked to fix and reply

The "should not do more than triage" case.

- **Prompt:** "Go through the comments, fix the valid ones, and reply to the rest."
- **Expected:**
  - [ ] Produces the triage only; explains that applying fixes and posting replies happen after triage, at the user's direction.
  - [ ] No commits, no edits, no GitHub replies or thread resolutions.
