# Evals for `call-trace`

## What this skill is supposed to fix

Without this skill, Claude tends to trace code shallowly — reading a narrow window around each call site and following only one direction — which misses side effects, branches, and the true blast radius. With it, Claude reads whole method bodies and maps the full chain in both directions (callers and callees), stopping cleanly at entry points and leaves, before any change is made.

## How to run

1. Install the skill: `cp -r skills/call-trace ~/.claude/skills/`
2. In a fresh session inside a real codebase, run each case below against the noted target.
3. Compare the result to **Expected**. A case passes only if every checkbox holds.

## Cases

### Case 1 — Bidirectional trace of a shared method

- **Setup / fixture:** any repo with a method called from several places that itself calls into a few layers.
- **Prompt:** "Get a complete understanding of `<Target>` before I change it."
- **Expected:**
  - [ ] Greps for callers and reads each caller's **entire** method body (not a window).
  - [ ] Recurses upward and stops at genuine entry points (request handler, background/scheduled entry, CLI/`main`, a test, or a public API with no in-repo callers).
  - [ ] Traces callees downward, reading full bodies, skipping trivial standard-library/logging calls.
  - [ ] Batches reads at the same depth rather than serializing independent ones.
  - [ ] Produces a both-directions summary (entry points → target → leaves) with side effects noted.
  - [ ] Does NOT edit any code.

### Case 2 — Stops at the repo boundary

- **Setup / fixture:** a target whose caller or callee lives in a different service/package.
- **Prompt:** "Trace how `<Target>` is used."
- **Expected:**
  - [ ] Notes the external caller/callee by name and stops at the repo edge.
  - [ ] Does NOT start opening files in another repo/service unprompted.
  - [ ] Still traces the in-repo portions fully.

### Case 3 — Negative: a trivial lookup that shouldn't trigger a full trace

The "should not fire" case.

- **Setup:** none — just the prompt.
- **Prompt:** "What's the signature of `<Target>`?" / "Where is `<Target>` defined?"
- **Expected:**
  - [ ] Recognizes that a single definition/lookup doesn't warrant a full bidirectional trace.
  - [ ] Just Reads/Greps the definition and answers, rather than tracing the whole call chain.
