---
name: pr-comments
version: 1.0.0
description: |
  Triage the review feedback on a pull request — human reviewers and AI/bot
  reviewers alike — into a judged task list. Use when asked to "pull the
  comments from my PR", "look at the review feedback", "work through the PR
  comments", or after opening a PR that receives an automatic AI review.
  Collects every unresolved comment, judges each against repo facts, and
  verdicts it ACT / DISMISS / HUMAN with cited evidence. It does not reply on
  GitHub and does not apply fixes.
allowed-tools:
  - Read
  - Grep
  - Glob
  - AskUserQuestion
  - Bash(gh pr view:*)
  - Bash(gh pr diff:*)
  - Bash(gh api:*)
---

# PR Comments: turn review feedback into judged, actionable tasks

You are working through the review feedback on a pull request. The failure mode this skill prevents is treating feedback — especially AI-reviewer feedback — as either gospel or noise: each comment gets a grounded verdict — valid and worth acting on, or incorrect and safe to dismiss — backed by evidence from the repo, never by vibes. You triage; you do not fix, and you do not post.

## When to use this skill

- "Pull the comments from the PR" / "look at the comments on my PR" / "go through the review feedback"
- After opening a PR, once its reviews (human or automatic AI) have posted

## When NOT to use this skill

- **No PR exists yet** — review the branch locally instead; this skill triages posted feedback.
- **The user wants the fixes applied** — triage first with this skill; applying accepted items is a follow-up outside it.
- **Summarizing a PR's discussion for status purposes** — just read it; this skill is for triage.

## Steps

1. **Resolve the PR.** From a given number/URL, or the current branch (`gh pr view` with no args). If no PR can be resolved, ask and stop until answered.

2. **Collect the feedback.** Four sources, all of them:
   - Review bodies and states: `gh pr view <n> --json reviews`
   - Inline review comments: `gh api repos/{owner}/{repo}/pulls/<n>/comments` — **GET only**; this skill reads, it never writes (never `-X POST/PATCH/DELETE`).
   - Conversation comments: `gh pr view <n> --json comments`
   - Thread resolution (so "skip resolved" is real, not assumed — the REST endpoints above don't expose it): `gh api graphql -f query='{repository(owner:"<owner>",name:"<repo>"){pullRequest(number:<n>){reviewThreads(first:100){pageInfo{hasNextPage endCursor} nodes{isResolved comments(first:50){nodes{databaseId path line}}}}}}}'` — map **every** comment's `databaseId` in each thread to that thread's `isResolved` (a reply inside a resolved thread must be dropped too — don't stop at the first comment); if `pageInfo.hasNextPage` (a PR with >100 review threads), re-run the query with `after:"<endCursor>"` to page through the rest.

   Default scope is **all unresolved feedback** — human and AI/bot alike; narrow to bot-authored only when the user asks for just the AI review. **Drop threads whose `isResolved` is true** (and any already replied to with a decision), using the resolution map above — never guess resolution. **If this leaves zero items,** distinguish "reviewed, nothing flagged" from "the review hasn't posted yet": when the repo runs an automatic AI review on PR open and no bot review is present in `reviews` yet, tell the user it likely hasn't posted and to re-run shortly — report a clean/empty triage only when at least one review actually exists.

3. **Build the task list.** One numbered item per distinct piece of feedback: quote (or tightly paraphrase) the comment, its file/line anchor, and its thread id. Merge duplicates that restate the same point.

4. **Judge each item.** Check the claim against reality: read the flagged file at the flagged line, grep the repo for the conventions or symbols the comment invokes, and read the surrounding code rather than the hunk alone. When a judgment needs intent context beyond the code — what the change was *supposed* to do — read the PR description and any linked issue/ticket via `gh` before verdicting; if intent is still genuinely ambiguous, that item is HUMAN, not a guess. Verdicts:
   - **ACT** — the comment is right; state what the fix is (don't apply it).
   - **DISMISS** — the comment is wrong or moot; state the evidence (`file:line`) that refutes it.
   - **HUMAN** — judgment call above this skill's pay grade (product intent, team preference); say what the human needs to decide.

5. **Present the triage** in the output format, then **stop**. Do not reply to threads, resolve threads, or edit files. If the user wants accepted items applied or dismissals posted as replies, that happens after this skill, at their direction.

## Output format

```
PR #<n> — <title>
Feedback items: <total>   ACT: <n>   DISMISS: <n>   HUMAN: <n>

1. [ACT] <file:line> — "<comment gist>"
   Fix: <what to change, one line>
2. [DISMISS] <file:line> — "<comment gist>"
   Evidence: <file:line / fact that refutes it>
3. [HUMAN] <file:line> — "<comment gist>"
   Decide: <the question for a human>

Suggested order: <ACT items grouped by file, cheapest verification first>
```

## Rules

### What to do

- **Every verdict carries evidence.** ACT names the concrete fix; DISMISS cites the file/fact that refutes the comment; HUMAN states the open question. "Seems right" is not a verdict.
- **Be willing to dismiss.** Review feedback — AI feedback especially — is advisory; a grounded DISMISS with evidence is as valuable as an ACT.
- **Collect from all three comment surfaces** — review bodies, inline comments, conversation — inline-only misses half the feedback.

### What NOT to do

- **Never apply fixes or push commits** from this skill — the deliverable is the judged task list.
- **Never post to GitHub** (no replies, no thread resolution, no reviews) — what goes back to the PR is the user's voice.
- **Don't re-litigate resolved threads** or items the user already decided — triage only open feedback.

### Format discipline

- The triage table exactly as above, verdict tags first on each line, then stop. No per-comment essays — one line of reasoning each.
