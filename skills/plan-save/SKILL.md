---
name: plan-save
version: 1.0.0
description: |
  Save and structure a plan for iterative execution across sessions.
  Use after plan mode generates a plan to save it as a persistent
  markdown file with trackable phases.
allowed-tools:
  - Read
  - Write
  - Edit
  - AskUserQuestion
---

# Plan Save: Structure and persist a plan for iterative execution

You have just helped create a plan (either through plan mode or conversation). Your job is to restructure it into a persistent, trackable format and save it to a file.

## Steps

1. **Identify the plan** in the current conversation. Look for the plan that was just discussed or created in plan mode.

2. **Ask the user** for the save location using AskUserQuestion. Suggest a descriptive filename in the current project directory (e.g., `./dev-mode-plan.md`, `./auth-refactor-plan.md`). Do NOT save to `~/.claude/`.

3. **Restructure the plan** into the format described below.

4. **Write the file** to the location the user specified.

## Output format

```markdown
# [Plan Title]

## Context

[Extract the background, goals, constraints, architecture decisions, and any other
relevant context from the plan. This section should give a future session enough
information to understand WHY this plan exists and WHAT is being built. Include
file paths, architecture diagrams, design principles — anything a fresh session
needs to pick up the work without re-exploring the codebase.]

## Implementation phases

Phases are executed one at a time across conversation sessions. When a phase is finished,
add an `#### Implemented` subsection summarizing what was done, then prefix the phase title
with **COMPLETED** (e.g., `### COMPLETED 1. Setup database schema`).
On a new session, read this file first — skip any COMPLETED phases and pick up the next open one.
Do not automatically move to the next phase when done — mark the phase completed and stop.

### 1. [Phase title]

[What needs to be done — files to create/modify, specific implementation details,
code snippets, acceptance criteria. Be detailed enough that a fresh session can
execute this without guessing.]

### 2. [Phase title]

[...]

### N. [Phase title]

[...]
```

## Rules

- **Preserve ALL technical detail** from the original plan — do not summarize away specifics like file paths, code snippets, architecture notes, or design rationale.
- The **Context section** should be comprehensive enough for a completely fresh session (no prior conversation history) to understand the project and make good decisions.
- Each **phase** should be a coherent, self-contained unit of work that can be completed in one session.
- If the original plan already has numbered sections, steps, or phases, use those as the phases. Preserve the original numbering/naming style where it makes sense.
- If the original plan doesn't have clear steps, organize it into logical phases yourself based on dependency order.
- Keep phase descriptions **detailed** — include file paths, code snippets, architecture notes, expected behavior.
- Do **NOT** add phases that weren't in the original plan.
- Do **NOT** remove or reword technical content to make it "cleaner" — accuracy matters more than aesthetics.
