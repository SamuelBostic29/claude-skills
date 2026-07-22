# Reply mechanics — posting to Copilot and Claude, and watching CI

Read this from step 4 of `ai-post`. All commands run as the user's authed `gh` account —
replies appear under their name.

## Copilot: inline reply to the source comment

Copilot findings are pull-request review comments. Reply in-thread using the comment id
recorded in the item's `Source:` line:

```
gh api repos/{owner}/{repo}/pulls/{pr}/comments/{comment_id}/replies -f body='<draft reply>'
```

One reply per item. Do not open a new top-level comment for a Copilot finding — the
reply must land in the finding's thread.

## Claude: quote-reply to the review's Code Review header

Claude review-bot comments are issue-level comments on the PR. Each starts with a job
header line, then a `### Code Review` section whose **first paragraph states what was
reviewed** — that scope paragraph is the reply's anchor. Real shapes:

```
### Code Review

First review — HEAD `45206ae`, base `main`. Reviewed all 28 changed files (…).
```

```
### Code Review

Incremental review of `5585ecd` ("dash blank header fields, …"), on top of previously-reviewed `04394c7`.
```

The wording varies ("First review of this PR…", "Incremental review — new commit…",
"Incremental review of…") but the structure is constant: heading, then one scope
paragraph. **Quote exactly those two things and nothing else** — never the findings,
severity blocks, or the job header line.

Build the comment body: each quoted line prefixed with `> `, a blank line, then the
draft replies for that review's findings as bullets:

```
> ### Code Review
>
> Incremental review of `5585ecd` ("dash blank header fields, …"), on top of previously-reviewed `04394c7`.

- **<finding 1 short title>:** <draft reply>
- **<finding 2 short title>:** <draft reply>
```

(One finding → a single sentence works too; skip the bold title.) Post it:

```
gh pr comment {pr} --repo {owner}/{repo} --body '<built body>'
```

One quote-reply **per source Claude review comment**, grouping all of that review's
items — never one comment per finding (that re-quotes the same header repeatedly).

## Watching CI and pulling failures

Wait for all checks to settle (background it if the suite is slow):

```
gh pr checks {pr} --repo {owner}/{repo} --watch
```

On a failure, map the check to its run and pull only the failed steps' log:

```
gh pr checks {pr} --repo {owner}/{repo} --json name,state,link   # link carries the run id
gh run view {run_id} --repo {owner}/{repo} --log-failed
```

If `--log-failed` is empty (e.g. the job was cancelled), fall back to
`gh run view {run_id} --log` and search for the first error. Diagnose the root cause from
the log before reporting — the check name alone ("build", "test") is not a diagnosis.
