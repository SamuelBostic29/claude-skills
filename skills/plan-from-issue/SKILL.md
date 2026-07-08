---
name: plan-from-issue
version: 1.0.0
description: |
  Turn a GitHub issue (plus an optional story ticket) into a saved, phase-structured
  implementation plan: fetch the issue, synthesize the ask, ground it in the codebase
  via the call-trace skill, then persist the plan via plan-save. Use when given an
  issue URL or repo + issue number and asked to "gather context for this issue",
  "start/build a plan for this ticket", "get this story ready to implement", or
  "/plan-from-issue". Stops once the plan is saved — execution belongs to plan-next.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(gh auth status:*)
  - Bash(gh auth switch:*)
  - Bash(gh issue view:*)
  - Bash(git remote get-url:*)
  - Skill
  - AskUserQuestion
---

# Plan From Issue: turn a GitHub issue into a saved implementation plan

You have been handed a GitHub issue — and possibly a separate story ticket — and your
job is to produce a saved, executable implementation plan for it by chaining this
repo's context and planning skills. The failure mode this skill exists to prevent is
**planning from prose**: drafting a plan straight from ticket text without grounding
it in the actual code, which produces plausible-sounding phases that name files that
don't exist and miss the side effects that do. Every plan this skill saves must be
grounded in code that was actually read.

This is an orchestrator: it depends on the **call-trace** and **plan-save** skills
being installed, and it ends where they end — with a saved plan, not changed code.

## When to use this skill

- Given a GitHub issue URL, or a repo + issue number, with a request to gather
  context, build understanding, or start a plan for it.
- "Get this story/ticket ready to implement" — a story ticket description is
  supplied alongside (or inside) the issue.
- Kicking off work on an issue when no saved plan exists yet.

## When NOT to use this skill

- **A saved plan for this work already exists** — use `plan-next` to execute it or
  `plan-review` to critique it; don't generate a competing plan.
- **The user wants the change made now**, not planned — small, well-understood fixes
  don't need a plan pipeline; just do the work.
- **You only need the issue's contents** — a quick `gh issue view` answers that; this
  skill is for producing a plan, not summarizing a ticket.
- **No issue exists** — if there's only a verbal idea, plan it directly (plan mode +
  `plan-save`); this skill's job starts from a real issue.

## Steps

1. **Resolve the issue reference.** Accept a full issue URL or a repo + number. If
   given only a number, derive the repo from `git remote get-url origin` in the
   current directory. If the issue's repo and the working directory's remote point at
   different repos, or no repo can be derived, ask via AskUserQuestion and stop.

2. **Verify the gh account.** Run `gh auth status`. If multiple accounts are authed
   and the active one is not the account used for this repo's owner, switch with
   `gh auth switch --user <account>` and **say that you switched**. Never fetch under
   the wrong account, and never switch silently.

3. **Fetch the issue.** `gh issue view <n> --repo <owner/repo> --comments` — read the
   full body and comments, not just the title.

4. **Gather the story ticket.** It may live in the issue body itself, in a second
   issue the user pointed at (fetch it the same way), or in a local file the user
   named (Read it). If the issue body is thin and no story ticket was provided, ask
   for one via AskUserQuestion rather than padding the gap with assumptions.

5. **Synthesize the ask.** Distill issue + story ticket into an explicit statement of
   what is being requested and a plain-prose list of acceptance criteria. Strip
   ticket-tracking tags and IDs — plain language only. If the ask is materially
   ambiguous or self-contradictory, ask via AskUserQuestion before proceeding; never
   plan around a guess.

6. **Locate the target code.** Map the ask onto the codebase with Grep/Glob/Read to
   find the methods, classes, or routes the work centers on. Select at most **3**
   targets — the most load-bearing ones.

7. **Trace each target.** Invoke the **call-trace** skill on each selected target to
   build deep bidirectional context. Do not skip this even when the ticket "seems
   clear" — this step is what separates a grounded plan from prose.

8. **Draft the plan.** Write the implementation plan from the synthesized ask plus
   the trace findings: ordered phases, the real file paths involved, and how each
   acceptance criterion is met. Every phase must reference code that was actually
   read in steps 6–7.

9. **Save the plan.** Invoke the **plan-save** skill to persist it (it will ask the
   user where to save).

10. **Stop.** Report using the Output format below — the synthesized understanding,
    what was traced, and where the plan lives. Suggest `plan-review` to critique it
    and `plan-next` to start executing. Do **not** begin implementing.

## Output format

```
Plan saved: <path> (<N> phases)

Understanding: <one short paragraph — what the issue + story ticket are asking for>
Acceptance criteria: <plain-prose list>
Traced: <the call-trace targets and the one-line takeaway from each>

Next: plan-review to critique, plan-next to execute phase 1.
```

## Rules

### What to do

- **Verify the account before any gh call.** Fetching under the wrong account is an
  unrecoverable first step on machines with multiple identities.
- **Read the whole issue, comments included.** Decisions and scope changes live in
  comment threads at least as often as in bodies.
- **Hard cap: 3 call-trace targets.** Pick the most load-bearing; more traces add
  noise, not understanding.
- **Ground every phase.** Each plan phase must name files/methods that were actually
  read during the trace — if a phase can't, trace more or cut the phase.

### What NOT to do

- **NEVER plan from prose alone.** Skipping the codebase trace because the ticket
  "explains it well" is the cardinal sin — that is exactly when invented file paths
  slip in.
- **Don't start implementing.** The deliverable is the saved plan; execution belongs
  to `plan-next` in a later session.
- **Don't paste raw ticket text into the plan.** Synthesize; the plan's Context
  section is for a future session, not an archive of the issue.
- **Don't invent acceptance criteria.** If the ticket doesn't state one you think is
  implied, list it as an open question for the user — not as a requirement.

### Format discipline

- Don't narrate each fetch and grep; speak up at the checkpoints — the synthesized
  understanding (step 5) and the final report.
- Output-format block exactly as specified, plan location first. Then stop.
