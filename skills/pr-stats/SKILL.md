---
name: pr-stats
version: 1.0.0
description: |
  Summarize a GitHub user's pull-request activity over a time window into one
  markdown report — per-PR metadata, lines/files/commits, human-reviewer-comment
  counts (bots filtered), and a short summary of each linked issue. Use when
  asked for "PR stats", a "PR report", "summarize my GitHub work", "what did I
  ship in the last X", or given a PR number/URL for a single-PR writeup. Defaults
  the author to the authed gh account and the window to the last 14 days.
allowed-tools:
  - Bash
  - Write
  - AskUserQuestion
---

# PR Stats: summarize a user's GitHub PR activity into one report

You are producing a single markdown report of the pull requests one GitHub user authored in a time window — aggregate totals plus a per-PR breakdown, including a short "what was asked" summary of each linked issue. You gather read-only from GitHub via `gh` and write exactly one local file. You never post, comment, push, or open anything.

Two failure modes to guard against: **(1) silently running as the wrong account** when several are authed — resolve the user up front (Step 1) and switch at most once; and **(2) baking in anything personal** — user, scope, output path, and automation accounts are all resolved at runtime or configurable, never hardcoded.

## When to use this skill

- "PR stats", "PR report", "PR tracking", "summarize my GitHub work"
- "What did I ship in the last X days/weeks?", "all my PRs since `<date>`"
- A PR number, `owner/repo#N`, or PR URL → a single-PR writeup

## When NOT to use this skill

- Posting, commenting on, or editing anything on GitHub — this skill is read-only and produces one local file.
- Reporting on issues, commits, or CI not tied to PR authorship.
- A trivial "is this PR merged?" status check — just `gh pr view` it; this skill writes a full report.

## Steps

### Step 1 — Resolve the GitHub user (the ONLY place this skill touches accounts)

1. Enumerate authed accounts: run `gh auth status` and parse every `Logged in to github.com account <login>` line; note which shows `Active account: true`.
2. Determine the **target user**:
   - If the request named an explicit username, use it.
   - Else if exactly **one** account is authed, use it — no prompt.
   - Else (**two or more**), ask via `AskUserQuestion` — "Which GitHub account should this report run as?" — one option per authed login, marking the active one. Use the choice.
3. **Switch once, here:** if the target isn't already the active account, run `gh auth switch --user <target>`. This is the *only* `gh auth switch` the skill performs.
4. If **zero** accounts are authed, stop and tell the user to run `gh auth login`.

The resolved login is the report's `--author` and the account every later `gh` call runs under. **Do not switch accounts again anywhere below.**

### Step 2 — Resolve scope, window, output, and mode

- **Scope (optional):** if the user named an owner/org, capture it as `<OWNER>`; otherwise scope is *all repos* the search returns for the user.
- **Window:** convert the user's date phrasing to absolute `YYYY-MM-DD` for `--since`/`--until`. Default: the last 14 days ending today (use the date from the system context as today). If only a start is given, end = today.
- **Output dir:** default `~/pr-stats/`; use an explicit directory if the user gave one.
- **Extra automation accounts (optional):** any non-bot automation logins the user wants excluded (e.g. an org's security scanner) — fold these into the exclusion list in Step 6.
- **Mode:** a PR number / `owner/repo#N` / PR URL → **single-PR mode** (skip the Step 4 search; one-PR report, no aggregates). Otherwise **bulk mode**.

### Step 3 — Ensure the output directory exists

```
mkdir -p <OUTPUT_DIR>          # default ~/pr-stats
```

### Step 4 — Find the PRs (bulk mode)

```
gh search prs --author <USER> --created "<SINCE>..<UNTIL>" --limit 100 \
  --json number,title,repository,state,createdAt,closedAt,url
```

- If a scope `<OWNER>` was given, filter client-side to entries whose `repository.nameWithOwner` starts with `<OWNER>/`. (Combining `--owner` with `--author` on `gh search prs` is unreliable — filter in code instead.)
- 0 results → write a minimal "no PRs in window" report and stop at Step 10.
- Hit the `--limit 100` cap → retry `--limit 200` and note in the header that the cap may have been hit.

**Single-PR mode:** skip the search; take the given PR (derive the repo from `git remote get-url origin` if only a number was given) and go straight to Step 5 for that one PR.

### Step 5 — Gather per-PR detail (parallelize)

For each PR `<owner>/<repo>#<num>`, issue these **in parallel within one tool-use block**; with many PRs, fan out across PRs too. Token cost is not a concern here; latency is — never serialize independent calls.

```
a. gh pr view <num> --repo <owner>/<repo> \
     --json number,title,state,createdAt,closedAt,mergedAt,url,body,headRefName,baseRefName,additions,deletions,changedFiles,commits,reviews,isDraft,author,labels
b. gh api 'repos/<owner>/<repo>/pulls/<num>/comments' --paginate \
     --jq '[.[] | {login:.user.login, user_type:.user.type, body, path, line, created_at}]'
c. gh api 'repos/<owner>/<repo>/issues/<num>/comments' --paginate \
     --jq '[.[] | {login:.user.login, user_type:.user.type, body, created_at}]'
d. gh api 'repos/<owner>/<repo>/pulls/<num>/files' --paginate \
     --jq '[.[] | {filename, additions, deletions, changes, status}]'
```

`--paginate` is required so high-activity PRs don't lose comments or files past the first page.

### Step 6 — Tally human-reviewer comments

Combine three sources per PR: inline review comments (5b), conversation comments (5c), and non-empty review bodies from `pr view`'s `reviews[]`. **Exclude** an entry if ANY of these holds:

- `user_type == "Bot"`
- login ends in `[bot]` or `-bot` (case-insensitive)
- login is in the generic automation list (case-insensitive): `github-actions`, `dependabot`, `codecov`, `codecov-commenter`, `mergify`, `renovate`, `snyk-bot`, `claude`, `copilot`
- login is in the user-supplied extra-automation list from Step 2 — **some automation posts as `user.type == "User"`**, so this explicit list matters
- login == the resolved author (the author's own comments don't count)

Remaining entries are **human reviewer comments**. Group by login and count.

### Step 7 — Parse linked issues from each PR body

Run (case-insensitive, multiline) over `body`:

```
(?i)(?:closes|fixes|resolves)\s+(?:([\w-]+\/[\w-]+))?#(\d+)
```

Process **every** match (a PR can close several). Group 1 = optional `owner/repo`, group 2 = issue number; default to the PR's own repo when there's no prefix. For each:

```
gh issue view <num> --repo <owner>/<repo> \
  --json number,title,body,createdAt,closedAt,url,labels
```

On a failed lookup, write `_Linked issue #N could not be fetched_` and continue — never fail the whole report.

### Step 8 — Summarize each linked issue

A single paragraph (4–6 sentences) per fetched issue, focused on: the problem it describes, **what was specifically asked of the implementer** (the requirement / acceptance criteria), and any constraints or dependencies that shaped the work. Don't quote the body verbatim, don't pad, don't restate metadata. If the issue body is under 200 characters, include it verbatim instead.

### Step 9 — Compute aggregate stats (bulk mode only)

Across the window: total PRs by state (`merged` / `open` / `closed-without-merge` / `draft`); total additions/deletions; total files changed; total commits; average time-to-merge over merged PRs (days, 1 dp); average human-reviewer comments per PR (1 dp); repos worked in (`owner/repo: <count>`, descending).

### Step 10 — Generate and write the report, then stop

Build the full markdown in memory (template below), then write it **once** to `<OUTPUT_DIR>/report-<YYYYMMDD>-<HHmmss>.md` (local date/time, so repeated runs don't collide). If Step 1 switched accounts, note that in the header. Print the absolute path. **Stop** — the file path is the entire deliverable.

## Report template

```markdown
# PR Stats Report

**User**: <USER>
**Scope**: <OWNER, or "all repos">
**Window**: <SINCE> to <UNTIL> (<N> days)
**Generated**: <YYYY-MM-DD HH:mm>

---

## Summary

- **Total PRs**: <N> (<merged> merged, <open> open, <closed> closed-without-merge, <draft> draft)
- **Lines changed**: +<additions> / −<deletions>
- **Files changed**: <N>
- **Commits**: <N>
- **Avg time to merge**: <X.X> days
- **Avg human reviewer comments per PR**: <X.X>
- **Repos worked in**:
  - `<owner>/<repo>` — <count> PRs

---

## Pull Requests

### #<num> — <title>

- **Repo**: `<owner>/<repo>`
- **State**: <Merged | Open | Closed | Draft>
- **Branch**: `<headRefName>` → `<baseRefName>`
- **Created**: <YYYY-MM-DD>
- **Merged / Closed**: <YYYY-MM-DD> (<X> days) | _still open_
- **URL**: <url>
- **Volume**: <changedFiles> files, +<additions> / −<deletions>, <commits> commits

#### Commits
- <messageHeadline>

#### Files changed
- `<filename>` — +<add> / −<del>

(If more than 20 files: list the top 10 by total lines changed, then `_(+ N more files)_`. Truncate only the rendering, never the collected data.)

#### Human reviewer comments (<total> total)
- **@<login>** — <count> comments

(If 0, write `_None_`.)

#### Linked issue: #<num> — <issue title>
**URL**: <issue url>

<paragraph summary of what the issue asked the implementer to deliver>

(Repeat per linked issue. Omit the block entirely if the PR links none — never fabricate one.)

---

(repeat the entire `### #<num>` section per PR, separated by `---`)
```

In single-PR mode, emit one `### #<num>` section and omit the `## Summary` aggregates.

## Rules

### What to do

- **Resolve and switch the account exactly once, in Step 1.** No later step calls `gh auth switch` — the whole report is gathered under the single account chosen up front.
- **Parallelize independent `gh` calls** in one tool-use block; fan out across PRs. Latency matters, token cost does not.
- **Collect everything; truncate only the rendering.** Gather every comment, file, and commit; truncation rules apply only to the rendered report.
- **Use UTC dates throughout** — the GitHub API returns UTC; don't convert to local time in the report body (the filename timestamp may be local).

### What NOT to do

- **NEVER hardcode a username, org, output path, or automation account** — resolve the user (Step 1), default the window/output, and take scope + extra-bot accounts as input.
- **NEVER post, comment, push, or open anything.** Read-only; one local file is the only write.
- **NEVER append to or merge with a prior report** — every run is a fresh, uniquely-timestamped file.
- **NEVER fabricate a linked issue** — if the body has no `closes/fixes/resolves`, omit the issue block.

### Format discipline

- The deliverable is the written file and its printed path. No preamble, no inline dump of the report. Build, write, print the path, stop.
