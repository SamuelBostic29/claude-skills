---
name: ai-post
version: 1.0.0
description: |
  Finish a review cycle: gate on the service's unit tests + lint, post the reviewed
  draft replies to the PR (inline replies to Copilot and human reviewers, quote-replies
  to the Claude bot's Code Review header), then watch the PR's CI — diagnosing any red
  run, and after the user approves a fix, committing, pushing, and re-watching until
  everything is green. Use when the user says "/ai-post", "post the replies", or "ship
  the review responses".
allowed-tools:
  - Read
  - Edit
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
---

# AI Post: post the drafted replies and babysit CI to green

The review items — AI queue, human queue, or both — are resolved and their replies
drafted and reviewed — invoking this skill is the user's "post it". Your job is to prove
the branch is clean (tests + lint), publish every draft reply to the PR, then stay on
the PR's CI until every check is green, looping through diagnose → ask → fix → commit →
push as needed. The cardinal risk here is posting on a broken branch: replies saying
"Fixed — …" pointing at code that doesn't pass. The gate runs first, always.

## Configuration (set per adopter — must match the comments skills)

| Key | Default |
| --- | --- |
| `AI_STATE_DIR` | `docs/plans/ai-review/` |
| `HUM_STATE_DIR` | `docs/plans/hum-review/` |

## When to use this skill

- "/ai-post" after /ai-draft's batch has been reviewed
- "Post the replies" / "send the responses and watch CI"

## When NOT to use this skill

- Drafts don't exist yet or weren't reviewed — `/ai-draft` first. Never compose reply
  text here.
- Items still OPEN that the user wants handled — `/ai-next`. (Posting a partial batch is
  allowed, but only if the user confirms it.)
- General CI babysitting on a PR with no AI-review state file — this skill is the last
  step of the ai-review suite, not a standalone CI watcher.

## Steps

1. **Find the state file(s).** Check both `AI_STATE_DIR` and `HUM_STATE_DIR` for files
   matching the current repo/PR (or the passed path/queue); posting covers every match
   in one pass. Read them and collect items with a `Draft reply:` line and no `Posted:`
   line. If none, report and stop. If some items are still OPEN, ask: post the drafted
   subset, or stop and finish /ai-next first.

2. **Gate: tests + lint.** Discover the service's own commands — CI workflow files,
   `package.json` scripts, the build tool's conventions — and run its unit tests and its
   linter (apply the linter's autofix if it has one, then re-run). Any failure that
   isn't autofixable: report it with the output and stop. Nothing is posted on a red
   gate — no exceptions.

3. **Land pending work.** If the working tree has changes (the /ai-next fixes, lint
   autofixes), the replies must point at pushed code: propose a commit message and ask
   via AskUserQuestion — "Commit & push these fixes now?" — and proceed only on yes.
   If the user declines, stop.

4. **Post the replies.** Read `references/reply-mechanics.md` for the exact commands,
   then for each drafted item:
   - **Copilot and human inline items:** reply inline to the source comment id.
   - **Claude items:** group by source review comment; one quote-reply per review,
     quoting ONLY its `### Code Review` heading + scope paragraph, followed by each
     finding's draft reply as a bullet.
   - **Human issue-level items:** reply as a PR comment quoting the first line of the
     source comment.
   Mark each item `- **Posted:** yes` in its state file as it lands.

5. **Watch CI.** Run `gh pr checks {n} --watch` (in the background if long-running) and
   wait for all checks to settle.

6. **All green → step 8. Any red →** pull the failing run's log
   (`gh run view <run-id> --log-failed`), find the actual cause, and report it plainly.
   Then ask via AskUserQuestion: **Fix it (I'll commit & push the fix and re-watch CI)**
   / **Discuss more**. "Discuss" means present your analysis and stop until directed.

7. **On "Fix it":** implement the fix, re-run the step-2 gate, then commit and push —
   that choice was the authorization — and go back to step 5. Repeat until green.

8. **Stop.** All replies posted and every CI check green. Report the final state:
   replies posted (with the PR), commits pushed during the loop, and the green checks.

## Output format

Final report:

```
Done — 8 replies posted on PR #123, CI green.
- 4 inline replies to Copilot, 2 quote-replies to Claude reviews, 2 inline replies to human reviewers
- CI loop: 1 red (unit tests — <one-line cause>) → fixed in <sha>, re-run green
```

Red-CI report (step 6), before the question:

```
CI red: <check name> — <root cause in one or two sentences, from the failed log>
```

## Rules

### What to do

- **Gate before anything leaves the machine.** Tests + lint pass, or nothing posts.
- **Post drafts verbatim.** The wording was reviewed at /ai-draft; you are a courier.
- **Quote only the Code Review header** (heading + scope paragraph) in Claude replies —
  never the findings body.
- **Diagnose from the failed log, not the check name.** Name the actual cause before
  asking fix-or-discuss.
- **Every commit/push is covered by an explicit yes** — step 3's question, or choosing
  "Fix it" in step 6 (its label says commit & push, so the choice is the consent).

### What NOT to do

- **NEVER post with a red gate or a red diagnosis unfixed.**
- **NEVER edit reply wording** while posting. Wording changes go back through /ai-draft.
- **NEVER commit or push without the step-3 or step-6 yes** — silence is not consent.
- **NEVER commit the state file.**
- **Don't stop at "CI failed".** Pull the log and find the cause before reporting.

### Format discipline

- Between posting and green, only report state changes (posted, red + cause, fixed,
  green) — no play-by-play of waiting. Final report in the shape above, then stop.
