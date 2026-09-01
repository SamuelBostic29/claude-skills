---
name: plan-to-ta
description: |
  Convert a saved implementation plan into a Technical Analysis (TA) for a
  ticket — the high-level "XYZ needs done, so we're doing ABC" design write-up
  that goes in a ticket description, not the phased execution plan. Use when
  asked to "write the TA", "turn this plan into a technical analysis", "draft
  the TA for <ticket>", or "/plan-to-ta".
allowed-tools:
  - Read
  - Grep
  - Glob
  - AskUserQuestion
argument-hint: "[plan-file]"
metadata:
  version: 0.1.0
---

# Plan to TA: distill an implementation plan into a ticket's Technical Analysis

You are converting a detailed implementation plan into the short Technical Analysis that belongs on a ticket. The cardinal failure mode is **dumping the plan into the ticket**: phases, sequencing, review substeps, executor notes, open-question ledgers, and session sizing are execution machinery — a TA is the *design*, ordered by architecture, not the *schedule*, ordered by execution. Strip all of it, keep the mechanisms.

## Configuration (set per adopter — the only project-specific section)

| Key | Value | Used for |
| --- | --- | --- |
| `PLAN_LOCATION` | `<where plan files live, e.g. docs/plans/>` | Locating the plan when no path is given |
| `TICKET_TOOL` | `<the skill or CLI that writes to your tracker — blank = chat-only, no push offer>` | The optional push in step 6 |
| `TICKET_MARKUP` | `<markdown \| jira-wiki \| other>` | Converting the draft on push |

## When to use this skill

- "Write the TA" / "turn this plan into a technical analysis" / "draft the TA for <ticket>"
- A phased implementation plan exists and its ticket needs a description-level design write-up
- "/plan-to-ta [plan-file]"

## When NOT to use this skill

- **No plan exists yet** — a TA invented straight from a ticket title isn't grounded. Say so and stop.
- **Writing or revising the plan itself** — use your planning workflow.
- **Any other ticket edit** (comments, transitions, fields) — use the tracker tool directly.

## Steps

1. **Locate and read the plan.** Use the `$ARGUMENTS` path if given; otherwise the plan already in this session's context; otherwise look in `PLAN_LOCATION` and ask which file. Read the whole plan: its context/goals front matter supplies the intent; its phases supply the mechanisms.

2. **Identify the ticket.** Take the key from the plan or the conversation; if absent, ask. (Needed only for the push offer — don't block drafting on it.)

3. **Pick the TA shape from the plan's scope** — read `references/ta-shapes.md` for the four shapes with examples:
   - **Micro** — a bug fix / one-mechanism change: `**TA**` + 1–3 sentences.
   - **Layer-walk** — a small feature in one service: a short block per architectural layer (Endpoints → Business logic → Data access → DTOs, or per-file bullets).
   - **Contract** — field/import/API-contract work: field tables with types + validation, payload examples, an edge-case list.
   - **Full-design** — a large feature: Current Architecture → per-area changes → Non-Obvious Considerations.

4. **Write the TA in the house conventions.** One TA per plan, even when it spans backend + frontend — scope sections per side instead of splitting.
   - Header: `### Technical Analysis` (micro shape uses `**TA**` alone).
   - Above micro, open with 1–2 sentences of intent: *what* needs to happen and *why this approach* — before any mechanics.
   - **Real identifiers only** — file paths, classes, methods, routes, tables, env vars — taken from the plan and, when the repo is on disk, spot-verified with Grep/Read. Never invent or "normalize" a name; if the plan and code disagree, the code wins.
   - **State the negative space**: what explicitly does *not* change ("No DTO changes", "Modified endpoints: none"). It's a first-class part of the format.
   - Tables for enumerable facts (fields, file → change, endpoint method/route/purpose).
   - Strip everything execution-flavored: phases, ordering, review substeps, executor/model notes, open questions, test plans, estimates, story points, acceptance-criteria tags. Mechanisms, not snapshot numbers (no test/file/line counts).

5. **Present the draft in chat** and stop for review. The draft is the deliverable — no meta-commentary inside it.

6. **Offer the push** only if `TICKET_TOOL` is set: after the user approves the text, convert per `TICKET_MARKUP` (Jira table in `references/ta-shapes.md`), show the exact write, and wait for an explicit go-ahead. Never write to the tracker without it.

7. **Stop.** Done = the TA draft delivered, and pushed only if the user said push.

## Output format

The chat draft leads with the TA itself, then one line naming shape and target:

```
### Technical Analysis

<1–2 sentence intent: what needs to happen, and the approach>

<sections per the chosen shape — see references/ta-shapes.md>

---
Shape: <micro | layer-walk | contract | full-design> · Target: <ticket> · Push? (per TICKET_TOOL, confirm-gated)
```

## Rules

### What to do

- **Design over schedule.** Order sections by architecture (DB → endpoints → business logic → DTOs → UI), never by execution order.
- **Intent first.** Everything above micro opens with the "XYZ needs done, so ABC" framing before mechanics.
- **Verify identifiers when the repo is local.** A TA with a wrong class name is worse than a vaguer one.
- **Scale the shape to the plan.** A trivial fix gets three sentences, not headers.
- **Say what doesn't change.** Explicit no-change statements per area the reader would otherwise wonder about.

### What NOT to do

- **NEVER carry execution machinery into the TA** — phases, sequencing, review substeps, executor notes, open questions, session sizing, test plans, estimates.
- **NEVER invent an identifier** or write a TA with no plan behind it.
- **NEVER push to the tracker without the user's explicit go-ahead.**
- **No acceptance-criteria tags, no hard counts** (tests/files/lines), no restating the ticket description verbatim.

### Format discipline

- The draft is pure TA text — no preamble, no narration of what you stripped. One status line after the `---`, then stop.
