---
name: handoff
description: |
  Write a capped between-session brief (goal, where we are, next steps, decisions, gotchas) to
  ~/.claude/handoffs/<repo>.md, or read it back at the start of a fresh session. User-invoked:
  `/handoff` writes, `/handoff resume` reads. A deliberate handoff, not a compaction.
argument-hint: "[resume]"
disable-model-invocation: true
allowed-tools:
  - Read
  - Write
  - Bash(git rev-parse:*)
  - Bash(git branch:*)
  - Bash(git status:*)
metadata:
  version: 0.1.0
---

# Handoff: carry one piece of work from this session to the next

The next session starts with zero context and will trust this file. Write what a colleague needs to
continue in ten minutes: the goal, what is done, what is next, what was decided and why, and what
will bite them. The failure mode is the **transcript dump**: a long narrative of what happened.
Write state, not history, and stay under the cap.

## Steps

1. **Locate.** Run one command: `git rev-parse --show-toplevel && git branch --show-current && git status --short`.
   Repo key = basename of the toplevel; outside a repo, key = `general`, no branch, no status.
   Path = `~/.claude/handoffs/<key>.md`.

2. **Branch on `$ARGUMENTS`.** Empty → step 3 (write). `resume` → step 5 (read). Anything else →
   one line: `handoff: unknown argument "<arg>" — use /handoff or /handoff resume`. Stop.

3. **Write the file** at the path from step 1 in the Output format below, overwriting any previous
   handoff for that key. Every bullet is a current fact, not a step you took. `Working tree` is the
   `git status --short` output verbatim (omit the section when clean or outside a repo). Mark anything
   you did not verify this session `(unverified)`.

4. **Report and stop.** Print `Handoff written: <path> (<N> lines)`. Nothing else.

5. **Resume.** Read the file. If it does not exist: `handoff: none for <key> at <path>`. Stop. If
   the handoff branch differs from the current branch, say so in one line. Then print exactly:

   ```
   Resumed <key> from <date> · <branch>
   Goal: <Goal line>
   Next: <first item under Next>
   ```

   Stop and wait for direction. Do not start the next step unasked.

## Output format

```
# Handoff · <key> · <branch> · <YYYY-MM-DD HH:mm>

## Goal
<one sentence: the task and what "done" looks like>

## Where we are
- <done or in-progress fact, `path:line` where it helps>

## Next
1. <ordered step>

## Decisions
- <decision> — <why>

## Gotchas
- <trap, non-obvious behavior, command that fails and why>

## Working tree
<git status --short, verbatim>

## Refs
- <ticket key, PR URL, plan file, working-file path>
```

## Rules

- **Cap: 60 lines total, max 6 bullets per section.** Cut the least load-bearing item, never widen.
- **State, not history.** "Migration added, not yet applied" — not "then I added a migration".
- **Verbatim identifiers.** Ticket keys, paths, branch names, commands, error text exactly as seen.
- **Empty section = one bullet `- none`.** Keep every heading so the reader knows nothing was dropped.
- **NEVER commit, push, or compact.** The file is the deliverable.
- **NEVER pad resume output.** Three lines plus the optional branch warning; the file itself is the detail.
- No preamble, no recap, no offers.
