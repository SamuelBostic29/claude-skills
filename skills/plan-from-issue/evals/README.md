# Evals for `plan-from-issue`

## What this skill is supposed to fix

Without this skill, given an issue and asked to "get a plan going", Claude drafts a
plan straight from the ticket prose — plausible phases naming files it never read —
and often starts implementing on top of it. With the skill, Claude fetches the real
issue under the right gh account, synthesizes an explicit ask, grounds the plan in
call-traced code, saves it via plan-save, and stops.

## How to run

1. Install the skill **and its dependencies** (`call-trace`, `plan-save`):
   `cp -r skills/plan-from-issue skills/call-trace skills/plan-save ~/.claude/skills/`
2. In a fresh session inside a real repo with an open GitHub issue, run each case.
3. Compare the result to **Expected**. A case passes only if every checkbox holds.

## Cases

### Case 1 — full pipeline from an issue URL + story ticket file

- **Setup / fixture:** a repo with a non-trivial open issue; a local text file
  containing the story ticket description.
- **Prompt:** "Gather context and start a plan for <issue URL> — the story ticket is
  in <path/to/story-ticket.txt>."
- **Expected:**
  - [ ] Ran `gh auth status` before any fetch; switched account (and said so) only if
        the active account didn't match the repo owner
  - [ ] Fetched the issue with comments and read the story ticket file
  - [ ] Stated a synthesized understanding + plain-prose acceptance criteria (no
        ticket-tracking tags) before planning
  - [ ] Invoked the call-trace skill on ≤ 3 targets before drafting any plan phase
  - [ ] Invoked plan-save; the saved plan's phases name files that were actually read
  - [ ] Stopped after the report — no code edits, no phase-1 execution

### Case 2 — bare issue number, thin body, no story ticket

- **Setup / fixture:** a repo whose `origin` remote resolves the issue; the issue
  body is one vague sentence.
- **Prompt:** "Start a plan for issue 17."
- **Expected:**
  - [ ] Derived the repo from `git remote get-url origin` instead of asking for it
  - [ ] Recognized the body was too thin and asked for the story ticket / more detail
        via AskUserQuestion instead of padding the gap with assumptions
  - [ ] Did not invent acceptance criteria or draft a plan before getting an answer

### Case 3 — negative: a saved plan already exists

- **Setup:** the repo already contains a saved plan file for this issue's work
  (plan-save format, some phases incomplete).
- **Prompt:** "Let's keep going on issue 17."
- **Expected:**
  - [ ] Skill recognizes it doesn't apply — does not generate a competing plan
  - [ ] Defers to `plan-next` (execute) or `plan-review` (critique) instead
