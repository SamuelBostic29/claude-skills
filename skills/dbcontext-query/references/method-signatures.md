# Method-signature catalog + annotated example — layer-3 reference

## When to read this

Step 4 of `SKILL.md` sends you here once the entity, context, scope field, methods, and knobs are settled. Use the catalog to pick each method's shape, then follow the annotated example for the exact code. Everything project-specific is a `<PLACEHOLDER>` — the neutral domain is **Product** (key `int`) scoped by **`CategoryId`**, with a **`Category`** navigation, living on a context written here as `<DbContext>` in namespace `<RootNamespace>.Data`.

## Signature catalog

Signatures shown for `Product` / key `int`; substitute the real entity and `<TKey>`. "Scope" = whether the requested scope field filters the query.

| Method | Signature (async-suffix style) | Reads / Writes | Scope | Tracking | Notes / knobs |
|---|---|---|---|---|---|
| Get by id | `Task<Product?> GetProductByIdAsync(int id, CancellationToken ct)` | read (1) | optional | `AsNoTracking` | nullable return = "not found"; **knob:** throw instead |
| List | `Task<IReadOnlyList<Product>> GetProductsAsync(int categoryId, CancellationToken ct)` | read (n) | **required** | `AsNoTracking` | needs deterministic `OrderBy` |
| Paginate | `Task<PagedResult<Product>> GetProductsPageAsync(int categoryId, int page, int pageSize, CancellationToken ct)` | read (n) | **required** | `AsNoTracking` | `PagedResult<T>` is **your** paging wrapper; count + page; stable `OrderBy` before `Skip`/`Take` |
| Exists | `Task<bool> ProductExistsAsync(int id, CancellationToken ct)` | read (bool) | optional | n/a | `AnyAsync`, no entity materialized |
| Add | `void AddProduct(Product product)` | write | n/a | tracked | **knob:** `Add` vs `AddAsync` (below); **knob:** save here vs unit-of-work |
| Update | `void UpdateProduct(Product product)` | write | n/a | tracked | `Update` marks all properties modified; for partial updates, attach + set state |
| Remove | `Task RemoveProductAsync(int id, CancellationToken ct)` | write | optional | tracked | **knob:** soft (flag + timestamp) vs hard (`Remove`) |

## The knobs (present these as choices, never as law)

- **Async-method suffix.** `GetProductByIdAsync` vs `GetProductById`. Match the repo; default to the `Async` suffix only if nothing says otherwise.
- **`Add` vs `AddAsync`.** Prefer `Add` — it's synchronous and sufficient for the common case. `AddAsync` exists only for value generators that need store access to make a key (e.g. HiLo sequences); use it only then.
- **Save in the method vs unit-of-work.** Writes above stage changes and let the caller's `SaveChangesAsync` commit them. **Knob:** if the repo saves per call, `await SaveChangesAsync(ct)` inside each write instead.
- **Nullable return vs throw.** `Task<Product?>` returns `null` for not-found. **Knob:** throw a not-found exception if the data layer is expected to guarantee existence.
- **Tracking default.** Reads use `AsNoTracking`. **Knob:** drop it if the repo tracks reads by default.
- **Soft vs hard delete.** Soft = set a deleted flag + UTC timestamp on a tracked entity. Hard = `Set<Product>().Remove(entity)`. Pick one; don't do both.
- **`Set<Product>()` vs the `DbSet` property.** `Set<T>()` avoids depending on a property name; swap in the repo's `DbSet` (e.g. `Products`) if it has one.

## Annotated worked example

Generated for: entity `Product` (key `int`), scope `CategoryId`, include `Category`, methods get-by-id / list / paginate / exists / add / update / remove (soft). Shown with **explicit types** and the `Async` suffix — match the repo's `var`/explicit and naming conventions instead where they differ. `// ←` marks every placeholder or knob.

```csharp
using Microsoft.EntityFrameworkCore;

namespace <RootNamespace>.Data;                      // ← your context's namespace

// The context must be declared `partial` somewhere (usually its main file):
//     public partial class <DbContext> : DbContext { ... }
public partial class <DbContext>                     // ← your DbContext type
{
    // READ — single by key. Nullable return signals "not found" without throwing (knob).
    public Task<Product?> GetProductByIdAsync(int id, CancellationToken cancellationToken = default) =>
        Set<Product>()                               // ← or your DbSet property, e.g. Products
            .AsNoTracking()                          // ← reads don't track by default (knob)
            .Include(p => p.Category)                // ← chosen include
            .FirstOrDefaultAsync(p => p.Id == id, cancellationToken);

    // READ — list scoped by CategoryId. The scope filter is mandatory, not optional.
    public async Task<IReadOnlyList<Product>> GetProductsAsync(
        int categoryId, CancellationToken cancellationToken = default) =>
        await Set<Product>()
            .AsNoTracking()
            .Where(p => p.CategoryId == categoryId)  // ← scope filter — never omit
            .Include(p => p.Category)
            .OrderBy(p => p.Name)                    // ← deterministic order
            .ToListAsync(cancellationToken);

    // READ — one page within a scope. Returns items + total for the caller.
    public async Task<PagedResult<Product>> GetProductsPageAsync(   // ← PagedResult<T>: your paging wrapper
        int categoryId, int page, int pageSize, CancellationToken cancellationToken = default)
    {
        IQueryable<Product> query = Set<Product>()
            .AsNoTracking()
            .Where(p => p.CategoryId == categoryId)
            .OrderBy(p => p.Name);                   // ← stable order REQUIRED before Skip/Take

        int total = await query.CountAsync(cancellationToken);

        List<Product> items = await query
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .Include(p => p.Category)
            .ToListAsync(cancellationToken);

        return new PagedResult<Product>(items, total, page, pageSize);  // ← shape to your wrapper
    }

    // READ — existence only; materializes no entity.
    public Task<bool> ProductExistsAsync(int id, CancellationToken cancellationToken = default) =>
        Set<Product>().AnyAsync(p => p.Id == id, cancellationToken);

    // WRITE — stage an add; caller's SaveChangesAsync commits it (knob: save here instead).
    // Use Add unless a value generator needs async key generation (e.g. HiLo) → then AddAsync.
    public void AddProduct(Product product) =>
        Set<Product>().Add(product);

    // WRITE — stage an update. Update marks every property modified.
    public void UpdateProduct(Product product) =>
        Set<Product>().Update(product);

    // WRITE — soft delete (knob: hard delete instead). Entity is TRACKED so the flag persists.
    public async Task RemoveProductAsync(int id, CancellationToken cancellationToken = default)
    {
        Product? product = await Set<Product>()
            .FirstOrDefaultAsync(p => p.Id == id, cancellationToken);
        if (product is null) return;

        product.IsDeleted = true;                    // ← soft-delete flag
        product.DeletedUtc = DateTime.UtcNow;        // ← UTC timestamp
        // Hard-delete variant: Set<Product>().Remove(product);
    }
}
```
