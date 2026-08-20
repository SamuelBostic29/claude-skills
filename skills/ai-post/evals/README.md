# Evals for `ai-post`

## What this skill is supposed to fix

Without this skill, the endgame is manual and error-prone: replies posted on a branch
that doesn't lint, Claude reviews answered by re-quoting the entire findings body,
"CI failed" reported with no cause, and fixes committed without consent. With it: tests
and lint gate first, Copilot gets in-thread replies, Claude gets one quote-reply per
review anchored on just the Code Review header, and CI is watched to green with every
commit/push covered by an explicit yes.

## How to run

1. Install the skill: `cp -r skills/ai-post ~/.claude/skills/`
2. Fixtures need a real (test) PR: a branch with an open PR carrying ≥1 Copilot inline
   comment and ≥1 Claude-bot review comment, plus a state file at
   `{AI_STATE_DIR}/<repo>-pr-<n>.md` whose items are resolved and carry `Draft reply:`
   lines referencing those comments. Optionally add a human inline comment and a
   matching `{HUM_STATE_DIR}/<repo>-pr-<n>.md` with a drafted ANSWERED item to verify
   both queues post in one pass (in-thread, same as Copilot). Mark the PR as a test PR.
3. In a fresh session, run each case. A case passes only if every checkbox holds.

## Cases

### Case 1 — happy path: gate, post, green

- **Setup / fixture:** the fixture PR above; working tree has the (already-correct)
  fixes uncommitted; CI will pass once pushed.
- **Prompt:** "/ai-post"
- **Expected:**
  - [ ] Discovers and runs the service's unit tests and lint BEFORE any posting
  - [ ] Asks before committing/pushing the pending fixes, and proceeds only on yes
  - [ ] Copilot item replied in-thread via the `/replies` endpoint (not a new top-level comment)
  - [ ] Claude reply quotes ONLY the `### Code Review` heading + scope paragraph, one
        comment per source review, drafts posted verbatim
  - [ ] Items marked `Posted: yes` in the state file; state file itself not committed
  - [ ] Watches `gh pr checks --watch` and ends with the final report only when all green

### Case 2 — red CI: diagnose, ask, fix on consent

- **Setup / fixture:** same, but the pushed branch fails one CI check (e.g. a failing
  unit test introduced in the fixture).
- **Prompt:** "/ai-post" (answer "Fix it" when asked)
- **Expected:**
  - [ ] Pulls the failing run's log (`--log-failed`) and reports the actual root cause,
        not just the check name
  - [ ] Asks Fix it / Discuss more before touching anything
  - [ ] After "Fix it": implements, re-runs the tests+lint gate, commits, pushes, and
        re-watches CI until green — no second permission prompt needed for that push

### Case 3 (negative) — red gate blocks everything

- **Setup:** fixture where the service's unit tests fail locally.
- **Prompt:** "/ai-post"
- **Expected:**
  - [ ] Reports the failure with the test output and stops
  - [ ] Posts NO replies, commits nothing, pushes nothing
