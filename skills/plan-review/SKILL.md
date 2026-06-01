---
name: plan-review
version: 1.0.0
description: |
  Review a saved plan with convergence-oriented discipline — verdict first,
  blockers capped, "I don't understand" converted to questions instead of
  findings. Designed to avoid the fresh-eyes nit-list pattern where every
  review produces 6-8 items regardless of plan maturity.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
---

# Plan Review: Convergence-oriented fresh-eyes review

You are reviewing a plan that was written in a prior session. You do NOT have the session context the author had while writing it. That context-gap is the single biggest source of bad reviews — you flag "X isn't addressed" when X was deliberately scoped out two rounds ago, the user explains, and the round produces no improvement.

Your job is to produce a sharp, cheap, convergent review that the user can act on in one pass — and to append a short record of this review to the plan itself, so future reviewers can see what's already been said.

## Steps

1. **Find the plan file.** If an argument was provided, use that path. Otherwise, search the current project directory for plan files (matching `*plan*.md`, `*PLAN*.md`, or markdown in `plans/`). If exactly one is found and it's obviously the active plan, use it. If multiple, ask the user via AskUserQuestion, sorted by last-modified.

2. **Read the entire plan file,** including any `## Reviews` section at the bottom.

3. **Check prior reviews.** If a `## Reviews` section exists, read every entry. Two purposes:
   - **Avoid repeating yourself.** If a prior review already raised a concern and it was resolved (or explicitly scoped out), do not raise it again.
   - **Calibrate strictness.** Count the entries. Apply the scaling in Rules → Round-N discipline.

4. **Produce the review** in the output format below. Nothing else — no preamble, no recap of the plan, no "here's what I read."

5. **Append a record of this review** to the plan file (see Appending to the Reviews section).

6. **Stop.** Do not offer to make edits to the plan body. Do not continue into execution. The review and its record are the deliverables.

## Output format

Exactly this structure, in this order:

```
**Verdict:** execute | don't execute

**Blockers:** [max 2, or "none"]
- [sharp, specific, cites plan section]

**Questions:** [max 2, or "none"]
- [genuine "I don't understand" items, phrased as questions]
```

That is the entire output to the user. No additional sections. No polish list. No "minor suggestions." If you have nothing for a section, write "none" and move on.

## Appending to the Reviews section

After producing the review output above, append a short paragraph to the plan file under a `## Reviews` heading at the bottom. If the section doesn't exist, create it.

**Format per entry:**

```markdown
### Review N — YYYY-MM-DD

[One short paragraph, 2-4 sentences. State the verdict. If blockers or
questions were raised, summarize them in one clause each. If none, say so.]
```

- Use today's date from the conversation context (check the system reminder for `currentDate`).
- Number entries sequentially — if there are already 3 reviews, this is Review 4.
- Keep each entry short on purpose. The Reviews section length is itself a signal — if it grows long, the user should question whether further review is still productive. Fat paragraphs defeat that signal.
- Do not copy the full verdict/blockers/questions block into the Reviews section. Summarize.

## Rules

### What to flag

Only flag things visible from the plan text itself:

- **Internal contradictions** — phase 3 says X, phase 5 assumes NOT-X.
- **Load-bearing ambiguity** — "TBD" / "implementation detail" on a gating decision that downstream phases depend on.
- **Undefined load-bearing terms** — a term used as if defined that has no definition in the plan or in cited references.
- **Phase-gate mismatch** — a phase's gate condition can't actually be checked given the phase's scope.

### What NOT to flag

- **"X isn't addressed."** If X isn't in the plan, it was almost certainly scoped out deliberately. Convert this to a Question ("Is X deliberately out of scope?") instead — or, if the Reviews section shows this has been discussed before, don't raise it at all.
- **Polish, wording, "consider adding," section-reordering.** These are never blockers and don't belong in the output.
- **Hypothetical edge cases not in the current execution path.**
- **"You might want to verify..."** — if it's important enough to verify, it's either a blocker or a question. If it's neither, cut it.
- **Anything the Reviews section shows was already raised.** If prior review #2 asked about X and the plan wasn't changed, the user decided X is fine. Don't re-raise.

### Blocker vs. Question

Your default tempted-to-flag item is probably a Question, not a Blocker. Test:

- **Blocker**: "Executing this plan as written will produce a wrong / broken / incomplete result because ______." You can complete that sentence confidently from the plan text alone.
- **Question**: "I think there might be a problem with X, but it might also be deliberate and I don't have the context." → Question.

If you can't confidently complete the Blocker sentence, it's a Question. If the Question appears in a prior review, it's nothing — drop it.

### Round-N discipline

First, separate your concern into one of two classes:

- **Text-visible concern.** Something wrong *in the plan text itself*: an internal contradiction (phase 3 says X, phase 7 assumes NOT-X), a load-bearing TBD, an undefined load-bearing term, a phase gate that can't actually check what it claims. These are caught by reading, not by guessing at coverage.
- **Gap concern.** "X isn't addressed" / "I'd expect to see Y" / "what about Z?" You're inferring that something *should* be in the plan and isn't. This class is where review variance lives — different fresh-eyes reads produce different imagined gaps.

**Round-N discipline applies only to gap concerns. Text-visible concerns stay full-weight at every round** — a real contradiction on review 10 is still a real contradiction.

Count entries in the `## Reviews` section and apply to gap concerns:

- **Reviews 0–1:** normal weight. Gap concerns are fair game; fresh-eyes is most valuable here.
- **Reviews 2–4:** prefer converting gap concerns to Questions rather than Blockers. The author has had more context than you on each prior round; if a gap survived previous reviews, it's probably deliberate.
- **Reviews 5+:** default to not raising gap concerns at all. If your only material is gap concerns on review 6+, the honest verdict is "execute / none / none." Text-visible concerns are still raisable — but be sure it's actually text-visible, not a gap dressed up as one.

### When in doubt, it's a Question

The hardest call in this skill is "is this a real issue or am I navel-gazing?" You won't always classify correctly. That's fine — the output format has a built-in safety valve:

- **Questions are cheap.** One sentence to answer, no execution halt, no re-plan.
- **Blockers are expensive.** They stop execution and demand fixes.

So when you can't tell whether something is real: **route it to Questions, not Blockers.** Cost-asymmetrically, you'd rather ask a dumb question than halt execution on a non-issue. If the user answers the Question and it turns out to be nothing, no harm — the Reviews section records that it was asked, so future reviewers won't re-ask.

### Cap discipline

**Max 2 blockers. Max 2 questions.** Hard cap. If you have more candidates, pick the two most important of each and drop the rest. The cap forces prioritization — three is always findable, two requires actual judgment.

### Verdict discipline

The verdict is committal. If you'd execute the plan as-is, say "execute" and mean it. Don't say "execute" and then list 4 blockers — pick one or the other.

- **execute** = you would start Phase 0/1 right now as written, no further edits needed.
- **don't execute** = at least one blocker needs resolving first.

If blockers is "none" and questions is "none" — verdict is execute. Period.

### Format discipline

- No preamble ("I've reviewed the plan...").
- No summary of what the plan does.
- No "overall, the plan is solid" framing.
- No closing offer to make edits.
- Just the three-section output to the user, then the append to the plan file. Then stop.
