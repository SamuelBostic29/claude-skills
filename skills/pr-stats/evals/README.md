# Evals for `pr-stats`

## What this skill is supposed to fix

Without this skill, summarizing a user's PR activity is ad-hoc and easy to get wrong — running as the wrong authed account, missing paginated comments, or counting bot comments as human review. With it, the user is resolved up front (auto when one account, by prompt when several), the window/scope/output are configurable with sensible defaults, and the result is one complete, fresh markdown report gathered read-only.

## How to run

1. Install the skill: `cp -r skills/pr-stats ~/.claude/skills/`
2. In a fresh session with `gh` authed, run each case below.
3. Compare the result to **Expected**. A case passes only if every checkbox holds.

## Cases

### Case 1 — Default bulk run, single authed account

- **Setup / fixture:** exactly one `gh` account authed; that user has a few PRs in the last two weeks.
- **Prompt:** "Give me my PR stats."
- **Expected:**
  - [ ] Does NOT prompt for an account (only one is authed) and does NOT switch accounts.
  - [ ] Uses the authed login as `--author`; window defaults to the last 14 days.
  - [ ] Writes exactly one file under the configured output dir (default `~/pr-stats/`) and prints its absolute path.
  - [ ] Report has the aggregate Summary plus a per-PR section with commits, files, human-comment tally, and linked-issue summaries.
  - [ ] Read-only — no comments/pushes/PRs created.

### Case 2 — Scoped + custom window + extra automation account

- **Setup / fixture:** a user with PRs across multiple orgs; one org uses a non-bot automation login (e.g. a scanner that posts as a normal user).
- **Prompt:** "PR report for `<owner>` from 2026-01-01 to 2026-03-31, and ignore comments from `<that-automation-login>`."
- **Expected:**
  - [ ] Filters PRs to `<owner>/…` only; honors the explicit date window.
  - [ ] Excludes `<that-automation-login>` from the human-reviewer tally (in addition to the generic bot list).
  - [ ] Still one fresh file; still read-only.

### Case 3 — Multiple authed accounts, none specified (negative: ask, don't guess)

The "should ask instead of guessing" case — directly exercises Step 1.

- **Setup:** two or more `gh` accounts authed; the request names no user.
- **Prompt:** "Summarize my GitHub work this month."
- **Expected:**
  - [ ] Recognizes 2+ accounts and **asks via AskUserQuestion** which to run as — does NOT silently use the active account.
  - [ ] Switches to the chosen account **once**, then runs everything under it — no further `gh auth switch` anywhere in the run.
  - [ ] If the window has 0 PRs, writes a minimal zeros report and stops — fabricating no PRs or tickets.

### Case 4 — External-tracker ticket linking (configured, structural, link-only)

Exercises Step 7 Track B: the key is derived structurally and the tracker is never fetched.

- **Setup / fixture:** `TRACKER_URL_BASE` configured (e.g. `https://tracker.example/browse`); one PR on branch `main_PROJ-17385` whose title also leads with `PROJ-17385`; a second PR with neither a keyed branch nor a keyed title.
- **Prompt:** "Give me my PR stats."
- **Expected:**
  - [ ] Derives `PROJ-17385` from the branch (or title) via `TICKET_KEY_PATTERN` and renders a **Ticket** link line pointing at `<TRACKER_URL_BASE>/PROJ-17385`.
  - [ ] Makes **no** HTTP/API call to the tracker — the link is built from Configuration, not fetched.
  - [ ] The second PR (no derivable key) shows **no** ticket line — nothing fabricated.
  - [ ] With `TRACKER_URL_BASE` unset, no ticket lines appear anywhere (Track B off).
