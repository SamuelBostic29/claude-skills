---
name: review-session
version: 1.0.0
description: |
  Spin up a fresh, INTERACTIVE Claude Code session in a separate terminal to
  review the whole branch's changes vs the base (every commit over the base plus
  uncommitted edits) with zero context from the work that produced them.
  Use when asked to "review my changes in a fresh/separate session", "cold review
  before I open the PR", "spin up another Claude to review this", or "get an
  unbiased second pair of eyes on this branch". Hands the reviewer the exact diff
  automatically; the review happens in the new window, not here.
allowed-tools:
  - Read
  - AskUserQuestion
  - Bash(git rev-parse:*)
  - Bash(git branch:*)
  - Bash(git symbolic-ref:*)
  - Bash(git merge-base:*)
  - Bash(git diff:*)
  - Bash(git ls-files:*)
  - Write
  - Bash(wt.exe:*)
  - Bash(pwsh:*)
  - Bash(osascript:*)
  - Bash(x-terminal-emulator:*)
  - Bash(gnome-terminal:*)
  - Bash(konsole:*)
  - Bash(tmux:*)
---

# Review session: spawn a fresh interactive reviewer pre-loaded with the changeset

You are handing this branch's changes to a **brand-new, interactive Claude Code session running in its own terminal window**, so they get reviewed by someone who has *no idea how or why the code was written*. That context gap is the entire point: a session that did the work defends its own intent; a separate process can only judge the code on its merits.

Your single job is the **handoff and spawn** — detect the changeset, write it into a self-contained review brief, and launch the new interactive session pointed at that brief. You do **not** review the code yourself; reviewing here would reintroduce the exact bias this skill exists to remove. Two invariants govern everything: the reviewer is a **separate process** (no shared conversation), and it is **interactive** (never `-p`/headless — the user needs to converse with it).

## When to use this skill

- "Review my changes in a fresh / separate session"
- "Cold review before I open the PR" / before `draft-pr`
- "Spin up another Claude to review this branch"
- "Get an unbiased second pair of eyes on what I just did"

## When NOT to use this skill

- **You want a one-shot review with no back-and-forth** — use the built-in `/code-review` (or `/code-review ultra` for the deep cloud pass). This skill exists only when you want an *interactive* reviewer to interrogate.
- **Reviewing someone else's open PR** — use a PR-review tool; this reviews local working-tree/branch changes.
- **You want the reviewer to also apply fixes** — this is review-only by default; you drive fixes back in your own session.
- **Not a git repo, or no changes vs the base branch** — there is nothing to hand off; say so and stop.

## Steps

1. **Confirm there is a changeset.** Get the repo root (`git rev-parse --show-toplevel`) and current branch (`git branch --show-current`). If this is not a git repo, stop and say so. If `--show-current` is empty (detached HEAD), label the branch with the short SHA (`git rev-parse --short HEAD`) for the brief/output.

2. **Detect the base — prefer the remote-tracking ref.** Resolve the base to `origin/<name>` (e.g. `origin/main`) so the diff matches what GitHub computes for the PR. Try `git symbolic-ref --short refs/remotes/origin/HEAD` (it returns `origin/<name>`); if unset, probe `origin/main` then `origin/master` (`git rev-parse --verify`). If those `origin/*` probes all fail — no remote-tracking refs exist — resolve the base the same way against local branches (probe local `main` then `master`). If the base is genuinely ambiguous at either layer (both `main` and `master` exist with no `origin/HEAD`, no remote *and* both local candidates exist, or detached HEAD), **ask via AskUserQuestion and stop** — never guess. Note in the report that `origin/<base>` reflects the last fetch, so the user can `git fetch` first if they want the freshest base.

3. **Compute the review surface — the whole branch.** `MB=$(git merge-base <base> HEAD)`. The surface is `git diff $MB` (merge-base → working tree): **every commit since the branch diverged, plus staged and unstaged edits**, in one diff — the same surface the PR will contain. Push state is irrelevant. Three things the naive one-liner gets wrong:
   - **Redact secrets at diff time, not after.** A monolithic `git diff $MB` bakes secret bodies into the patch, and there is no reliable way to strip a hunk back out — so *exclude* the secret patterns from the diff itself with `:(exclude)` pathspecs and list the excluded paths separately as redacted. Secret patterns (the canonical list): `.env*`, `*.pem`, `*.key`, `*.p8`, `*.pfx`, `*.p12`, `*.jks`, `*.ppk`, `*.keystore`, `id_rsa*`, `id_ed25519*`, `id_ecdsa*`, `id_dsa*`, `*.tfvars`, `.npmrc`, `.netrc`, `credentials`, `secrets.*`, `*.local.*`, `appsettings.*.json`. Example: `git diff $MB -- . ':(exclude,glob).env*' ':(exclude,glob)**/*.pem' …`. Honest limit: a filename guard can't catch a secret hard-coded in ordinary source.
   - **Capture new untracked files** — `git diff $MB` omits them. For each path from `git ls-files --others --exclude-standard` that does **not** match a secret pattern, append its contents as a new-file diff: `git diff --no-index -- /dev/null <file> || true`. **`--no-index` exits 1 whenever the files differ — i.e. always; that is success, keep stdout regardless.** `git` interprets `/dev/null` itself, so this works cross-platform inside a git command. Untracked files that *do* match a secret pattern are listed as redacted, never diffed. (`--exclude-standard` skips gitignored files, not a brand-new, not-yet-ignored secret file — exactly the pre-PR state this skill targets.)
   - **Stats for the header:** `git diff --numstat $MB` gives the per-file add/del counts that fill `<N files>, +<adds>/-<dels>`.

   If the (post-exclude) diff is empty *and* there are no untracked files (the branch *is* the base with a clean tree), there is nothing to review — stop and say so.

4. **Write the review brief.** Write a single self-contained markdown file to the OS temp dir, built from [Brief format](#brief-format) — framing, then changeset metadata, then the diff. **Sanitize the filename:** real branches are `type/name`, so replace `/` (and any other non-`[A-Za-z0-9._-]` character, including spaces) in `<branch>` with `-` before building `claude-review-brief-<branch>-<timestamp>.md`. An unsanitized `/` makes `Write` target a non-existent temp subdirectory and fail — and spaces would break the step-5 launch quoting. The secret redaction already happened in step 3 (excluded at diff time, listed as redacted); the brief just carries the safe diff plus the redacted-paths list.

5. **Spawn the interactive reviewer.** Read `references/launch-recipes.md`, pick the recipe for the current OS, and launch a **detached** new terminal window — in the repo root, so the reviewer can open whole files for context — running `claude` interactively with a short initial prompt that points at the brief:
   > `Read the review brief at <path> and carry out the cold code review it describes. You are seeing this code for the first time — review it on its own merits.`
   **Pass that whole prompt as one quoted argument** — if it splits on spaces, `claude` receives only the first word (`Read`) and the review never starts. The launch must return immediately and **not block this session** (a one-time permission approval for the launcher may appear — that is not "blocking"). If no GUI terminal is available, fall back to printing the exact command for the user to run, and report it with the **fallback** output shape below — not the spawn one.

6. **Report and stop.** State that the review is happening in the new window, give the brief path, base, branch, and file/line counts, per [Output format](#output-format). Then **stop** — do not review the diff here.

## Brief format

```markdown
# Cold code review

You are reviewing this changeset with **no knowledge of why it was written**.
Do not assume the author's intent was correct. Review it on its own merits for:
correctness bugs, logic errors, unhandled edge cases, error/null handling,
security, breaking changes, and requirements the diff appears to miss. This is
an interactive review — surface findings most-severe first, cite `file:line`,
and let the user drive any fixes. Open whole files in the repo for context as
needed; do not stop at the hunk.

## Under review
- Branch: <current branch, or short SHA if detached> vs base <base> — entire branch (all commits over base) + uncommitted edits
- Range: <merge-base>..working tree
- Files: <N changed>, +<adds>/-<dels>
- New untracked files: <list or "none">
- Redacted (secret-pattern files, body withheld): <list or "none">

## Diff
<Wrap the diff in a fence LONGER than any backtick/tilde run inside it — markdown-heavy repos
 produce diffs containing ``` that would close a plain ```diff fence early; use ~~~~ or a 5+ backtick fence.>
<git diff $MB with the secret patterns :(exclude)-d, then a `git diff --no-index` new-file diff
 for each non-secret untracked file. Redacted files appear only in the list above, never here.>
```

## Output format

On a successful spawn:

```
Spawned interactive reviewer in a new window.
  Branch:  <current>  vs base: <base>
  Surface: whole branch — <N files>, +<adds>/-<dels> (all commits over base + working tree)
  Brief:   <temp path>
Review it in that window; come back here to apply any fixes. (Not reviewed in this session — by design.)
```

If no GUI terminal is available (headless / SSH / CI) — no window was opened:

```
No GUI terminal to spawn into. Run this yourself to start the review:
  cd <repo> && claude "Read the review brief at <temp path> and carry out the cold code review it describes. You are seeing this code for the first time — review it on its own merits."
  Surface: whole branch — <N files>, +<adds>/-<dels>
  Brief:   <temp path>
```

## Rules

### What to do

- **Separate process, always.** The reviewer is a new `claude` session in its own terminal — that isolation is the whole value. State it; don't shortcut it.
- **Interactive only.** Launch plain `claude "<prompt>"` (interactive by default). Never `-p`/`--print`.
- **Hand off by file.** Put the diff in the brief file, not on the command line — diffs are large and shell-escaping them is brittle.
- **Detect the base (prefer `origin/<base>`); ask if ambiguous.** Use the remote-tracking ref so the surface matches the PR diff; never assume `main` over `master` or guess across candidates.
- **Launch in the repo root** so the reviewer can read whole files, and **detached** so this session is never blocked.
- **Detect headless deterministically** — don't guess whether a GUI terminal exists; use the env tests in `references/launch-recipes.md`.

### What NOT to do

- **NEVER review the changes in this session.** That reintroduces the bias the skill removes — the cardinal rule. Spawn, report, stop.
- **NEVER use `-p`/headless** — the user must be able to converse with the reviewer.
- **Never paste secret-config bodies.** Redact (path + `redacted` note, no diff body) any file matching the step-4 pattern list — `.env*`, `*.pem`, `*.key`, `id_rsa*`, `appsettings.*.json`, `*.local.*`, … Caveat: this is a filename guard, so a secret hard-coded in ordinary source still passes — it can't promise zero secrets.
- **NEVER hardcode the base branch or a single platform** — detect both at runtime.
- **NEVER block this session** waiting on the review.

### Format discipline

- Report the spawn, brief path, and changeset stats, then stop. No preamble, and no review commentary of your own.
