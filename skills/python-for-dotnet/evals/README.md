# Evals for `python-for-dotnet`

## What this skill is supposed to fix

Without this skill, a .NET-shaped session writing DPTH Python imports .NET architecture
(interfaces + DI containers for single implementations, async sprinkled into Flask,
PascalCase locals, retrofitted "modern Python" cleanup in untouched code) or answers
"how do I X in Python" generically instead of in this repo's idiom. With it, new code
mirrors the sibling file's patterns — sync Flask MethodView vs async Quart domains —
and translation answers name the C# concept next to the repo-grounded Python one.

## How to run

1. Install the skill: `cp -r skills/python-for-dotnet ~/.claude/skills/`
2. Run each case in a fresh session inside the DPTH clone
   (`C:\Users\Samuel.Bostic\Documents\Paradigm\Repos\Backend\Data Plane Transaction Hub`).
3. Compare the result to **Expected**. A case passes only if every checkbox holds.

## Cases

### Case 1 — new Flask endpoint stays in repo idiom

- **Setup / fixture:** none (real repo).
- **Prompt:** "Add a GET /1.0/tenants/{id}/status endpoint to txservices that returns the
  tenant's status field."
- **Expected:**
  - [ ] Handler is a `MethodView` class (or extends the existing TenantHandler) with
        dependencies as `__init__` parameters — no DI container, no ABC/interface
  - [ ] Synchronous code — no `async def`, no `asyncio`
  - [ ] snake_case identifiers; response JSON keys keep the contract's PascalCase (`TenantId`)
  - [ ] Logging uses `current_app.logger` with lazy `%`-style args, not f-strings
  - [ ] Signatures are type-hinted; untouched code is not reformatted or re-typed

### Case 2 — translation question answered repo-first

- **Setup / fixture:** none.
- **Prompt:** "In Moq I'd do `mock.Setup(m => m.Get(1)).Returns(x)` and then
  `mock.Verify(...)`. What's the equivalent in this repo's tests?"
- **Expected:**
  - [ ] Reads/loads `references/csharp-to-python.md` rather than answering purely from memory
  - [ ] Answer pairs the Moq concept with `unittest.mock` (`return_value`,
        `assert_called_once_with`, `patch`), in unittest style — not pytest fixtures
  - [ ] Mentions the patch-where-it's-used rule and points at a real repo test file

### Case 3 — async service gets async idiom (and vice versa nowhere else)

- **Setup / fixture:** none.
- **Prompt:** "Add a lookup that calls Cosmos for a single delivery by id in the mulesoft
  service."
- **Expected:**
  - [ ] Code is `async def` end-to-end and follows the `src/domains/<entity>/` +
        thin-route pattern after reading a sibling domain
  - [ ] No blocking I/O calls inside the route; awaits the async Cosmos client
  - [ ] Does not propose extracting shared code into a cross-service library

### Case 4 — negative: .NET repo, skill stays out of the way

- **Setup:** working directory is a .NET Paradigm repo (e.g. Builder Catalog).
- **Prompt:** "Add a null check before we enumerate the collection."
- **Expected:**
  - [ ] python-for-dotnet does NOT fire; the user's .NET conventions
        (`.IsNullOrEmpty()`, no `var`, etc.) govern the change
