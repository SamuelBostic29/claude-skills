---
name: call-trace
version: 1.0.0
description: |
  Trace the full call chain in both directions — callers (upstream) and callees
  (downstream) — around a target piece of code, reading whole method bodies for
  deep context. Use when asked to "get a full/complete understanding", to trace
  callers, assess blast radius, or understand how something is used before
  changing shared or foundational code, or when working through PR review feedback.
allowed-tools:
  - Read
  - Grep
  - Glob
---

# Call Trace: map the full call chain in both directions

You are gathering deep context around a target piece of code before it's changed or assessed — tracing every caller above it (upstream) and every callee below it (downstream). Your job is to build a complete picture of how the code is reached and what it touches, then stop. This is a context-gathering skill: you read and map, you do not edit.

The failure mode this skill exists to prevent is **shallow tracing** — reading a 20-line window around each call site and missing the side effects, early returns, and branches that live in the rest of the method. Read whole method bodies, always; partial windows produce confident-but-wrong analysis.

## When to use this skill

- "Get a full / complete understanding" of how something works, or any close variant.
- Tracing callers, assessing blast radius, or understanding how a method is used.
- Before changing shared or foundational code where the impact isn't obvious.
- Working through PR review feedback — trace each review item independently.

## When NOT to use this skill

- You only need a single definition or a quick lookup — just Read/Grep it; a full bidirectional trace is overkill.
- You're about to make a small, well-understood, local change — don't manufacture a trace for it.
- You need to *edit* code — this skill only gathers context; move to the change once the trace is done.

## Upward trace (callers)

1. **Find callers.** `Grep` for every call site of the target method/function across the repo.
2. **Read whole bodies.** For each caller, `Read` the **entire containing method** — signature to end. Never just a window around the call site.
3. **Recurse upward.** Identify what calls *that* method and repeat, building the chain toward the entry points.
4. **Stop at an entry point or dead end:**
   - A request/route handler — the app's inbound edge (HTTP, RPC, GraphQL resolver).
   - A background or scheduled entry point (job runner, message/queue consumer, cron/timer task, worker loop).
   - A CLI command, or the program's `main`/startup entry point.
   - A test.
   - A public API surface with no callers inside this repo.
   - A method invoked only via dependency-injection/reflection/registration with no static callers — note it and stop.

## Downward trace (callees)

1. **List callees.** From the target, identify every non-trivial method/function it calls. Skip standard-library and noise calls (collection/string helpers, logging, simple getters).
2. **Read whole bodies.** `Read` the full body of each callee.
3. **Recurse downward** into *their* callees until a dead end: the data-access/persistence layer, an external client (HTTP/SDK/queue publish), third-party or standard-library code, or a pure helper with no further branching.

## Rules

### What to do

- **Read whole method bodies — always.** Signature to end. The side effects and branches that matter are rarely next to the call site.
- **Parallelize by depth.** Issue all `Read` calls at the same depth in a single batched tool block; never serialize reads that don't depend on each other.
- **Stay inside the current repo by default.** If a caller or callee lives in another service/package, note it by name and stop there. Cross a repo/service boundary only when the user explicitly asks.

### What NOT to do

- **NEVER read narrow windows** around a call site — it is the cardinal sin here; it produces shallow analysis and missed side effects.
- **Don't chase trivial callees** (standard-library/collection helpers, logging) — they add noise, not understanding.
- **Don't delegate to subagents by default.** Agent summaries sacrifice the raw-code fidelity this skill exists to preserve. Fan out only when (a) the call graph is very wide and most branches are clearly irrelevant, or (b) the user opted into a cross-repo trace.

### Format discipline

- Token usage and speed are not concerns here — accuracy and full context are the only priorities.
- When the trace is done, summarize the chain in both directions (entry points → target → leaves) and call out the side effects you found. Then stop — do not start editing.
