namespace Example.Catalog.Domain;

// Sample entity for dto-mapping evals. Neutral domain, deliberately includes:
//   - a to-one navigation (Category) and a to-many collection (Reviews)
//   - a server-owned field (CreatedUtc) and an internal field (RowVersionHash)
// so a correct run must right-size the variants and omit what must not leak.
public class Product
{
    public int Id { get; set; }
    public string Name { get; set; } = "";
    public string? Description { get; set; }
    public decimal Price { get; set; }
    public bool IsDiscontinued { get; set; }

    public int CategoryId { get; set; }
    public Category Category { get; set; } = null!;

    public ICollection<ProductReview> Reviews { get; set; } = new List<ProductReview>();

    public DateTime CreatedUtc { get; set; }         // server-owned — not client-settable
    public string RowVersionHash { get; set; } = ""; // internal concurrency token — never expose
}

public class Category
{
    public int Id { get; set; }
    public string Name { get; set; } = "";
}

public class ProductReview
{
    public int Id { get; set; }
    public int ProductId { get; set; }
    public int Rating { get; set; }
    public string? Comment { get; set; }
}
