# plan-to-ta evals

Run each case in a fresh session.

## Case 1 — big plan → full-design TA

**Setup:** A phased implementation plan for a multi-area feature (DB constraint change + new endpoints + merge-logic changes + FE page updates), with context/goals front matter, 5+ phases including review substeps and executor notes. A ticket key is named in the conversation. `TICKET_TOOL` configured.

**Prompt:** "Turn this plan into the TA for TICKET-123."

**Expected:**
- [ ] Full-design shape: `### Technical Analysis`, intent opener, sections ordered by architecture (DB → endpoints → DTOs → …), Non-Obvious Considerations present.
- [ ] Zero execution machinery: no phase names, no ordering language ("first/then/after phase"), no review substeps, no executor notes, no open questions, no test plan, no estimates.
- [ ] At least one explicit no-change statement ("No DTO changes…", "Modified endpoints: none").
- [ ] Identifiers match the plan/code exactly; endpoint table uses method/route/purpose columns.
- [ ] One TA covering backend + frontend (scoped sections), not two TAs.
- [ ] Ends with the status line and the push offer; nothing written to the tracker.

## Case 2 — tiny fix plan → micro TA

**Setup:** A one-phase plan whose whole change is a single mechanism (e.g. wrap a form in a disabled fieldset for read-only mode).

**Prompt:** "/plan-to-ta docs/plans/read-only-fix.md"

**Expected:**
- [ ] Micro shape: `**TA**` + 1–3 sentences. No headers, no tables, no intent paragraph.
- [ ] No inflation — a small plan must not produce a sectioned document.

## Case 3 (negative) — no plan exists

**Setup:** No plan file anywhere; the session has only a ticket description.

**Prompt:** "Write the TA for TICKET-999."

**Expected:**
- [ ] Skill does NOT fabricate a TA from the ticket description.
- [ ] It says a plan is needed or asks for the plan file — then stops.

## Case 4 (negative) — push gate

**Setup:** Case 1 completed; user says "looks good" but not "push"/"set it".

**Prompt:** "Looks good."

**Expected:**
- [ ] Skill offers/asks about the push; it does not write to the tracker on "looks good" alone, and any eventual write shows the exact converted text first.
