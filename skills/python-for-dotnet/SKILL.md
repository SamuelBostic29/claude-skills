---
name: python-for-dotnet
version: 1.0.0
description: |
  Conventions layer for writing Python in the Data Plane Transaction Hub repo
  as a .NET-first team. Fires whenever editing or writing .py files under the
  DPTH repo (txservices, search, mulesoft/Rx), or when the user asks "how do I
  do <C# thing> in Python" / "what's the Moq / LINQ / DI equivalent". Keeps
  output in this repo's actual idioms — sync Flask vs async Quart per service,
  MethodView + constructor injection, unittest.mock — and explains in C# terms
  when asked. Not a command; it shapes code the session is already writing.
allowed-tools:
  - Read
  - Grep
  - Glob
---

# Python-for-dotnet: write DPTH Python the way DPTH writes it

You are writing or explaining Python in the Data Plane Transaction Hub repo for developers whose home language is C#. The job is two-sided: produce Python that matches *this repo's* established idioms, and when asked "how do I X", answer with the C# concept named alongside the Python one. The failure mode to guard against is **importing .NET architecture into Python** — DI containers, interface hierarchies for single implementations, async-everywhere, PascalCase locals — or its mirror image, "clever" idiomatic-Python golf the team can't review. The repo's existing code is the bar; match it.

For the full C#→Python translation catalog (LINQ, Moq, DI, null-handling, async, gotchas), read `references/csharp-to-python.md` — load it when translating a concept, not preemptively.

## When to use this skill

- Editing or creating `.py` files anywhere under the DPTH repo
- "How do I do <C# thing> in Python?" / "what's the LINQ / Moq / DI / using-block equivalent?"
- Reviewing or explaining existing DPTH Python to a .NET developer

## When NOT to use this skill

- **.NET Paradigm repos** — the user's .NET conventions apply there (never `var`, `DateTime.UtcNow`, etc.); none of this file does.
- **Setting up environments or running checks** — `/py-env` and `/py-check` own those jobs.
- **Non-DPTH Python projects** — general Python advice is fine there; this file's idioms are repo-specific.

## The repo's idioms (verified, not aspirational)

**txservices & search — synchronous Flask:**
- Handlers are `flask.views.MethodView` classes with **constructor injection**: the DAO and helper callables arrive as `__init__` parameters (see `txservices/apis/handlers/tenant_handler.py`). This *is* the repo's DI — explicit arguments, no container.
- `request.get_json(silent=True) or {}` for bodies; `current_app.logger.info("[API] %s %s", method, path)` — lazy `%`-style args, never f-strings inside logger calls.
- Private helpers prefixed `_`; module-level `UPPER_SNAKE` constants read from `os.environ` at import time.
- Type hints on signatures (`Dict[str, Any]`, `Optional[...]`, `from __future__ import annotations`); bodies stay unannotated.
- `datetime.utcnow().isoformat()` for timestamps — match it, don't modernize it.

**mulesoft (Rx) — asynchronous Quart:**
- Everything is `async def` / `await`. Layering: `src/routes/<entity>.py` is a thin initializer delegating to shared `init_resource_routes`; logic lives in `src/domains/<entity>/` with factory + query-spec classes; config is pydantic-settings (`src/common/config.py`).
- New endpoints follow the existing domain folder pattern — look at a sibling domain first; don't invent a new layout.

**Tests (all services):** `unittest.TestCase` + `unittest.mock.patch` / `MagicMock` in `test_*.py`; Flask tests wrap calls in `app.test_request_context(...)`. pytest is the runner, unittest is the style — keep new tests in the file's existing style.

**API contracts:** JSON keys are PascalCase (`TenantId`, `TxnType`, `Limit`) because that's the wire contract — never "fix" them to snake_case. Python identifiers around them stay snake_case.

## Steps

1. **Locate the service.** Path prefix decides the model: `txservices/`/`search/` → sync Flask; `mulesoft/` → async Quart. This decides more than style — mixing the models is the one genuinely breaking mistake (see Rules).
2. **Read a sibling first.** Before writing a handler/domain/test, read the closest existing one and mirror its structure, naming, and import style.
3. **Write (or explain) in repo idiom.** When the user asks a translation question, name the C# concept and the Python equivalent side by side; pull `references/csharp-to-python.md` for the catalog and use a *repo* file as the example where one exists.
4. **Stop.** This skill never expands scope: no env setup, no test runs, no refactoring of untouched code to "better" Python.

## Rules

### What to do

- **Match the service's concurrency model — hard rule.** Sync code in Flask services; `async`/`await` throughout mulesoft. Blocking I/O (sync cosmos/redis/requests calls) inside a Quart route stalls the whole event loop; `asyncio.run()` inside a Flask handler is equally wrong.
- **Constructor args are the DI.** New dependencies enter through `__init__` parameters wired at registration, exactly like the existing handlers.
- **snake_case functions/variables, PascalCase classes, UPPER_SNAKE constants.** Wire-contract JSON keys keep their PascalCase.
- **Type-hint new signatures** — the repo does. The .NET "never `var`" instinct maps to "always annotate the function signature", not to annotating every local.
- **Raise exceptions; catch specific ones** (`azure.cosmos.exceptions.CosmosHttpResponseError` style) — no error-code returns, no Result<T> wrappers.

### What NOT to do

- **NEVER introduce a DI container, ABC/interface for a single implementation, or a new architectural layer.** If C# muscle memory says "add an interface", the repo answer is a plain class and a constructor argument.
- **Don't retrofit** type hints, f-string logging, `datetime.now(timezone.utc)`, or pytest-style tests onto code you aren't otherwise changing — diffs stay surgical.
- **Don't install packages ad hoc.** A new dependency is a team decision: it goes in the service's `requirements.txt` or `mulesoft/pyproject.toml` via PR, never just `pip install`ed into an env.
- **Don't apply the user's .NET conventions to Python.** No `var` rule, no `.IsNullOrEmpty()` — the Python falsy idiom `if not items:` is the repo norm (and a gotcha: see the catalog's null vs falsy entry).

### Format discipline

- Code first, C#-analogy commentary second and brief. Don't lecture about Python philosophy.
- Translation answers: one repo-grounded example beats three generic ones.
