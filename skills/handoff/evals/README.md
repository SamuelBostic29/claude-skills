# Evals for `handoff`

## What this skill is supposed to fix

Without it, a session ends with either a lossy compaction or an ad-hoc paragraph pasted into the
next prompt. With it, `/handoff` writes a fixed-shape, capped brief to `~/.claude/handoffs/<repo>.md`
and `/handoff resume` restores it in three lines.

## How to run

1. Skill is installed at `~/.claude/skills/handoff`.
2. Run each case in a fresh session, inside the named fixture.
3. A case passes only if every checkbox holds.

## Cases

### Case 1 — write inside a repo with a dirty tree

- **Setup:** a repo on a feature branch, one modified file, a session that made a couple of decisions.
- **Prompt:** `/handoff`
- **Expected:**
  - [ ] File written to `~/.claude/handoffs/<repo-basename>.md`, previous content overwritten
  - [ ] Header has key, branch, and timestamp; all seven sections present, empties as `- none`
  - [ ] `Working tree` matches `git status --short` verbatim
  - [ ] ≤ 60 lines, ≤ 6 bullets per section, bullets are state not narrative
  - [ ] Only output is `Handoff written: <path> (<N> lines)`; no commit, no compaction

### Case 2 — resume with a branch mismatch

- **Setup:** handoff exists for the repo naming branch `feature/x`; current branch is `main`.
- **Prompt:** `/handoff resume`
- **Expected:**
  - [ ] One-line branch mismatch warning
  - [ ] Exactly the three-line `Resumed …` block after it
  - [ ] Does not begin executing the `Next` step

### Case 3 — negative: resume with no handoff, and an unknown argument

- **Setup:** fresh repo with no `~/.claude/handoffs/<repo>.md`.
- **Prompt:** `/handoff resume`, then `/handoff foo`
- **Expected:**
  - [ ] First prints `handoff: none for <key> at <path>` and stops; no file created
  - [ ] Second prints the unknown-argument line and stops; no file written
