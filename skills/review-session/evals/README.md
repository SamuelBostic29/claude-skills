# Evals for `review-session`

## What this skill is supposed to fix

Asking the session that wrote the code to review it yields biased reviews — it
defends its own intent. The manual workaround is to open a second Claude Code
session whose only job is to review the diff cold. This skill automates that:
detect the changeset, write it into a self-contained brief, and **spawn a new
interactive reviewer in its own window** pointed at the brief. The headline
invariants: the reviewer is a **separate process** (no shared context) and
**interactive** (never `-p`), and the calling session **does not review the code
itself**.

## How to run

1. Install: `cp -r skills/review-session ~/.claude/skills/`
2. In a throwaway git repo, set up each case's branch/working state.
3. Run the prompt and check against **Expected**. A case passes only if every box holds.

> **Remote-base fixtures:** Cases 1, 3, and 4 expect an `origin/<base>`. Give the throwaway repo an `origin` (a local bare clone) and `git fetch` so the remote-tracking ref exists. Without a remote the skill *correctly* falls back to the local base, and the `origin/main` checkbox doesn't apply.

## Cases

### Case 1 — spawns a separate interactive session, doesn't review here (the critical one)

- **Setup:** branch `feature/x` off `main` with a couple of committed changes plus an uncommitted edit to `src/widget.ts`.
- **Prompt:** "Spin up a fresh session to review my changes."
- **Expected:**
  - [ ] Resolves the base to the remote-tracking ref `origin/main`, computes the merge-base, and builds a whole-branch diff covering **all commits over the base + uncommitted** tracked changes (not just the uncommitted edit)
  - [ ] Writes a self-contained brief file (framing + metadata + diff)
  - [ ] Launches a **new interactive** `claude` window (no `-p`/`--print`), detached, in the repo root
  - [ ] **Does NOT review the diff in the calling session** — reports the spawn + brief path and stops
  - [ ] Reports brief path, base, branch, and file/line counts

### Case 2 — ambiguous base → ask, don't guess

- **Setup:** repo has both `origin/main` and `origin/master`, and `origin/HEAD` is not set.
- **Prompt:** "Cold review this branch."
- **Expected:**
  - [ ] Recognizes the base is ambiguous and **asks via AskUserQuestion** rather than assuming `main`
  - [ ] Does not spawn until the base is settled

### Case 3 — safe handoff: secrets stay out of the brief

- **Setup:** the diff includes a change to `.env` alongside real source edits.
- **Prompt:** "Review my changes in a separate session."
- **Expected:**
  - [ ] The brief carries the source diff, but for `.env` records **only the path + a `redacted` note — never its diff body** (the added/removed lines are the secret)
  - [ ] Still spawns the reviewer

### Case 4 — brand-new untracked files reach the reviewer with their contents

- **Setup:** branch has one committed change plus a **new, never-`git add`-ed** file `src/new.ts` with real code in it.
- **Prompt:** "Spin up a session to review this."
- **Expected:**
  - [ ] The brief includes the **full contents** of `src/new.ts` (e.g. via `git diff --no-index`), not just its filename — a plain `git diff $MB` would omit it entirely
  - [ ] Committed change is included too

### Case 5 (negative) — one-shot request should NOT fire this skill

- **Setup:** any branch with changes.
- **Prompt:** "Just give me a quick code review of my changes."
- **Expected:**
  - [ ] Does **not** spawn a separate session; recognizes this is a one-shot need
  - [ ] Points the user at the built-in `/code-review` instead (this skill is only for an *interactive* spun-up reviewer)
