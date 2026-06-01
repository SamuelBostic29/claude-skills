---
name: plan-next
version: 1.0.0
description: |
  Continue executing the next phase of a saved plan. Reads the plan file,
  finds the next incomplete phase, implements it, updates the file, and stops.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
  - Task
---

# Plan Next: Execute the next phase of a saved plan

You are resuming work on a structured plan saved to a local file. The plan is ALREADY WRITTEN — do NOT create a new plan or enter plan mode. Your job is to find the next incomplete phase, implement it directly, update the plan file, and stop.

## Steps

1. **Find the plan file.** If an argument was provided, use that as the file path. Otherwise, search the current project directory for plan files (matching `*plan*.md`, `*PLAN*.md`, or any markdown file containing `## Implementation phases`). If exactly one is found, confirm it with the user. If multiple are found, ask the user which one to use via AskUserQuestion — list them sorted by last-modified (most recent first) and default to the most recently modified file.

2. **Read the entire plan file.**

3. **Understand the context.** Read the Context section carefully. This is your only source of background information — there is no prior conversation history.

4. **Find the next open phase.** In the "Implementation phases" section, find the first `###` heading that is NOT prefixed with `COMPLETED`. This is your current task.

5. **If all phases are COMPLETED**, inform the user that the plan is fully implemented and stop.

6. **Implement the phase.** Do the work described. Read existing code first before making changes. Use all available tools. If anything is unclear or blocked, ask the user rather than guessing.

7. **Update the plan file** when the phase is done:
   - Add an `#### Implemented` subsection at the end of the phase content with a brief, factual summary: files created/modified, key decisions made, any deviations from the plan.
   - Prefix the phase heading with `COMPLETED` (e.g., change `### 3. Create API endpoints` to `### COMPLETED 3. Create API endpoints`).

8. **Stop.** Do NOT proceed to the next phase. Report what was accomplished and stop.

## Rules

- **NEVER enter plan mode.** Do NOT use EnterPlanMode or ExitPlanMode. The plan already exists — your job is to EXECUTE it, not re-plan it. Go straight to implementation.
- Only work on **ONE phase** per invocation.
- Execute phases **in order** — do not skip phases.
- If a phase is unclear or blocked, **ask the user** rather than guessing or improvising.
- The `#### Implemented` summary should be **factual and concise** — what files were touched, what changed, any deviations from the plan.
- Do **NOT** modify the Context section or other phases.
- Do **NOT** move on to the next phase after completing one — mark it completed and stop.
- **NO PLAN DEVIATIONS WITHOUT ASKING.** If the planned approach seems difficult, infeasible, or suboptimal, you MUST stop and ask the user before changing the approach. Present the problem, explain why the plan seems hard, and propose alternatives — then let the user decide. NEVER unilaterally replace the planned approach with a different one, even if your alternative passes tests. The plan's approach was chosen for a reason (often architectural, not just functional), and silently deviating can undermine the entire purpose of the phase.
