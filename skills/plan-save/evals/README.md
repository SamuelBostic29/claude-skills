# Evals for `plan-save`

## What this skill is supposed to fix

Without this skill, a plan produced in conversation dies with the session — or gets dumped
to a file as loose prose a later session can't execute: no context for a cold start, no
phase boundaries, technical detail summarized away. With it, the plan lands in a persistent
file with a Context section rich enough for a fresh session and discrete, trackable phases
that `plan-next` can execute one at a time.

## How to run

1. Install the skill: `cp -r skills/plan-save ~/.claude/skills/`
2. Run each case in a session where the noted setup holds.
3. Compare the result to **Expected**. A case passes only if every checkbox holds.

## Cases

### Case 1 — save a plan produced in plan mode

- **Setup / fixture:** a session where plan mode (or a long planning discussion) just produced a multi-step plan with file paths and code snippets.
- **Prompt:** "Save this plan."
- **Expected:**
  - [ ] Asks where to save via AskUserQuestion, suggesting a descriptive filename in the project — does NOT silently pick `~/.claude/`.
  - [ ] The file has a Context section a fresh session could work from, and `###` phases under `## Implementation phases`.
  - [ ] File paths, snippets, and design rationale from the discussion survive — not summarized away.
  - [ ] No phases invented beyond what the plan discussed.

### Case 2 — plan already has numbered steps

- **Setup / fixture:** the conversation's plan already contains numbered sections/steps.
- **Prompt:** "Persist this as a plan file."
- **Expected:**
  - [ ] Phases mirror the plan's own numbering and structure rather than a re-invented split.
  - [ ] Each phase reads as a self-contained unit of work executable in one session.

### Case 3 — negative: nothing to save

The "should not fire / should ask instead" case.

- **Setup:** a fresh session; no plan has been discussed.
- **Prompt:** "Save the plan."
- **Expected:**
  - [ ] Recognizes there is no plan in the conversation — asks which plan is meant, or says there is nothing to save.
  - [ ] Does NOT fabricate a plan or write a file.
