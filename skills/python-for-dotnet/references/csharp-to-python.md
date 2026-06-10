# C# → Python translation catalog (DPTH-grounded)

Load this when translating a concept or answering "what's the C# equivalent" questions.
Where a repo example exists, prefer showing it over a generic one.

## Language constructs

| C# | Python | Notes |
|---|---|---|
| `$"Hello {name}"` | `f"Hello {name}"` | But **never** inside logger calls — use `logger.info("Hello %s", name)` (lazy formatting, repo style) |
| `using (var x = ...)` / `IDisposable` | `with open(...) as x:` | Context managers; `__enter__`/`__exit__` is `Dispose` |
| `null` | `None` | Compare with `is None` / `is not None`, never `== None` |
| `x ?? y` | `x if x is not None else y` | `x or y` is the common shortcut but treats `0`, `""`, `[]`, `{}` as null — see gotcha below |
| `x?.Prop` | `x.prop if x is not None else None` | No null-conditional operator; chains get explicit checks |
| `nameof(x)` | no equivalent | Hardcode the string |
| `readonly` / `const` | `UPPER_SNAKE` module constant | Convention only — nothing enforces it |
| `enum` | `enum.Enum` subclass | Repo mostly uses plain string constants instead |
| `namespace A.B` | package dirs + modules | Imports are absolute from the service root (`from handlers.x import Y` in txservices, `from src.domains... import Y` in mulesoft) |
| `partial class` | no equivalent | One class, one file |
| Properties (`get; set;`) | plain attributes | `@property` only when there's real logic; the repo default is plain attributes set in `__init__` |

## LINQ → comprehensions

| C# | Python |
|---|---|
| `items.Where(x => x.Active)` | `[x for x in items if x.active]` |
| `items.Select(x => x.Name)` | `[x.name for x in items]` |
| `items.Where(p).Select(s)` | `[s(x) for x in items if p(x)]` — one comprehension, not chained calls |
| `items.FirstOrDefault(p)` | `next((x for x in items if p(x)), None)` |
| `items.Any(p)` / `items.All(p)` | `any(p(x) for x in items)` / `all(...)` |
| `items.Count(p)` | `sum(1 for x in items if p(x))` |
| `items.OrderBy(k)` | `sorted(items, key=lambda x: x.k)` |
| `items.ToDictionary(k, v)` | `{k(x): v(x) for x in items}` |
| `items.SelectMany(f)` | `[y for x in items for y in f(x)]` |
| `items.GroupBy(k)` | `dict` accumulation loop or `itertools.groupby` (requires sorted input — the classic trap) |

Readability cap: if a comprehension needs more than one `if` and one `for`, write a loop.
The team reviews loops faster than nested comprehensions.

## Async (mulesoft only)

| C# | Python |
|---|---|
| `async Task<T> F()` | `async def f() -> T:` |
| `await x` | `await x` |
| `Task.WhenAll(a, b)` | `await asyncio.gather(a, b)` |
| `Task.Run(...)` | does not translate — no thread-pool escape hatch in Quart routes; if something is blocking, it needs an async client library |
| `.Result` / `.Wait()` | **forbidden instinct** — there is no safe sync-over-async; calling a coroutine without `await` silently does nothing (returns a coroutine object) |

The "forgot to await" bug is the #1 .NET-dev Python-async mistake: no compiler warning,
the call just never runs. Watch for unawaited coroutine warnings in logs.

## Testing: Moq → unittest.mock

| Moq | unittest.mock (repo style) |
|---|---|
| `new Mock<IFoo>()` | `MagicMock()` — no interface needed; any attribute/method materializes on use |
| `mock.Setup(m => m.Get(1)).Returns(x)` | `mock.get.return_value = x` (args don't constrain — assert them at verify time) |
| `.ReturnsAsync(x)` | `AsyncMock(return_value=x)` or `mock.get = AsyncMock(return_value=x)` |
| `.Throws<T>()` | `mock.get.side_effect = SomeError()` |
| `mock.Verify(m => m.Get(1), Times.Once)` | `mock.get.assert_called_once_with(1)` |
| `It.IsAny<string>()` | `unittest.mock.ANY` |
| DI-injecting the mock | `@patch("handlers.txn_handler.execute_search")` decorator/context-manager — patches the name *where it's used*, the single most common patch mistake (patch the importing module, not the defining one) |

Repo example: `txservices/apis/tests/test_search_handler.py` — Flask `test_request_context`
plus nested `patch(...)` context managers.

## Platform / tooling

| .NET thing | DPTH equivalent |
|---|---|
| `appsettings.json` + IConfiguration | `.env` file + `os.environ.get(...)` (Flask services) or pydantic-settings `BaseSettings` (mulesoft) |
| NuGet / `.csproj` `PackageReference` | `requirements.txt` (txservices, search) / `pyproject.toml` + `uv.lock` (mulesoft) — change via PR, never ad-hoc `pip install` |
| `dotnet run` | `/run <service>` |
| `dotnet test` + analyzers | `/py-check` |
| Solution/project structure | each service is self-contained; there is **no shared library** between txservices and search — duplicated modules are intentional, don't "extract a common project" |
| `DateTime.UtcNow` | `datetime.utcnow()` — repo convention (yes, it's the legacy API; match it) |
| `ArgumentNullException` / `InvalidOperationException` | `ValueError` / `RuntimeError`; domain errors get specific exception classes only if a sibling already defines them |

## Gotchas with no C# analog

1. **Falsy vs null.** `if not items:` is true for `None` *and* `[]` *and* `""` *and* `0`.
   When "empty list" and "no list" mean different things, test `is None` explicitly.
   (`string.IsNullOrEmpty(s)` ≈ `not s` — that one maps cleanly.)
2. **Mutable default arguments.** `def f(tags=[])` shares ONE list across every call.
   Use `def f(tags=None):` then `tags = tags or []` inside.
3. **Late-binding closures in loops.** `[lambda: i for i in range(3)]` — all three return 2.
   Bind with a default: `lambda i=i: i`.
4. **Indentation is syntax.** A mis-indented line isn't a style issue, it's a different program.
5. **Imports run code.** Module top-level executes on first import — txservices reads env
   vars at import time, which is why `.env` must load *before* `from app import app`
   (see `run_local.py` ordering).
6. **No access modifiers.** `_name` is a convention, not enforcement. Respect it anyway.
