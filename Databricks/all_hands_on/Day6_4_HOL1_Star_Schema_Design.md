---
name: Day 6 HOL 1 — Gold Layer: Build the Star Schema Dimension Tables
content_type: Scenario
overview: With Silver fully cleaned and conformed, this hands-on builds all 6 Gold-layer dimension tables for GlobalMart's star schema — dim_customer and dim_product (reusing SCD2 surrogate keys already generated in Silver), dim_date (generated directly from real data bounds, not copied from any source table), and dim_address, dim_payment_method, and dim_orders (each getting a brand-new surrogate key generated here in Gold). By the end you will understand why some dimensions reuse a key, why others generate one, why a full overwrite is the right write strategy here, and which key type fact_sales actually uses to join to each dimension.
learning_objectives:
  - Reuse an already-versioned SCD2 surrogate key from Silver rather than re-deciding history in Gold
  - Explain why a full overwrite is correct for this Gold dimension build instead of a MERGE
  - Generate a Kimball-style date dimension directly from real data bounds instead of an arbitrary hardcoded range
  - Generate a new surrogate key for a dimension that doesn't already have one, using a hash of its natural key
  - Identify a degenerate dimension and explain why some of its attributes are deliberately left unresolved
  - State which key type (natural vs. surrogate) fact_sales actually uses to join to its dimensions
prerequisites:
  - A Databricks workspace with read access to the gbmart.silver.* tables
  - Completed Day 6 ILT 1 (Business Process Mapping & Star Schema/Kimball), ILT 2 (Grain Definition & Dimension Design), and ILT 3 (Fact Tables Deep Dive)
duration: 60 minutes
level: Intermediate
industries:
  - e-commerce
tags:
  - databricks (tool)
  - spark (tool)
  - data-modeling / dimension-design (skill)
---

---

## Scenario 1 — dim_customer & dim_product: Reusing Silver's SCD2 Keys

**Overview:** GlobalMart's Silver layer already generated the SCD2 surrogate keys and full version history for customers and products back on Day 5 — `silver.customers` and `silver.products` already carry `customer_sk`/`product_sk`, `is_current`, and effective-date columns. Gold's job here is not to re-decide any SCD2 versioning — that decision already happened in Silver — it's simply to re-publish exactly the columns the business and BI layer need, using a full table overwrite on every run.

**Outcome:** `dim_customer` and `dim_product` built as Gold Delta tables, each reusing its Silver-generated SCD2 surrogate key.

---

## Input 1

**Type:** Text

### Setup

>[!IMPORTANT]
>The code in this hands-on uses the literal `gbmart` catalog — this is GlobalMart's own real Gold-layer run. Your own catalog will be named differently; replace `gbmart` with your own catalog name throughout.

```python
from pyspark.sql.functions import *
from pyspark.sql.types import *

CATALOG = "gbmart"
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.gold")
```

---

## Input 2

**Type:** Text

### Build dim_customer

| Column | Why it's here |
|---|---|
| `customer_sk` | Join target for `fact_sales`; decouples the fact from the natural key and is what makes SCD2 versioning possible |
| `customer_id` | Business key — traces back to the source system, same value across all versions of one customer |
| `full_name`, `email`, `phone_number` | What the business actually looks at; `email`/`phone_number` are also exactly the fields that trigger a new SCD2 version when they change |
| `is_current` | Lets new `fact_sales` rows find "the current version" without date-range logic |
| `effective_start_date`, `effective_end_date` | What makes point-in-time history possible |

```python
dim_customer_df = spark.table("gbmart.silver.customers").select(
    "customer_sk", "customer_id", "full_name", "email", "phone_number",
    "is_current", "effective_start_date", "effective_end_date"
)

dim_customer_df.write.format("delta").mode("overwrite").saveAsTable("gbmart.gold.dim_customer")
print(f"dim_customer rows: {spark.table('gbmart.gold.dim_customer').count():,}")
```

---

## Input 3

**Type:** Choice

**Question:** Why does this Gold build use a full `overwrite` instead of a `MERGE INTO`, even though `dim_customer` and `dim_product` are SCD2 dimensions?

**Options:**
- `MERGE INTO` doesn't work on Delta tables with SCD2 columns
- The SCD2 versioning decision already happened in Silver — by the time Gold reads it, rows are already correctly versioned, so a MERGE here would just match `customer_sk` to itself with no real decision left to make
- Overwrite is always faster than MERGE, regardless of the data
- Gold tables are never allowed to use MERGE

**Correct Options:**
- The SCD2 versioning decision already happened in Silver — by the time Gold reads it, rows are already correctly versioned, so a MERGE here would just match `customer_sk` to itself with no real decision left to make

**Solution:**
`silver.customers` already carries the correct `customer_sk`, `is_current`, and effective-date values, worked out during Silver's own SCD2 `MERGE`. Gold reading and overwriting those same rows isn't re-deciding anything — it's re-publishing what Silver already decided. At GlobalMart's scale (~20K customers, 500 products), a full overwrite is simpler and equally correct.

**Tags**
- approach (skill)

---

## Input 4

**Type:** Code

**Question:** Build `dim_product` the same way `dim_customer` was built in Input 2: select the columns GlobalMart's Gold layer needs from `silver.products`, and overwrite `gbmart.gold.dim_product`. Include the product's business key, its name and category fields, the attribute that actually changes over time, and its SCD2 control columns.

**Language:** python

**Snippet:**
```python
dim_product_df = spark.table("gbmart.silver.products").select(
    # your column list here
)

# your write code here
```

**Solution:**
```python
dim_product_df = spark.table("gbmart.silver.products").select(
    "product_sk", "product_id", "product_name", "category", "sub_category",
    "discounted_price_inr", "is_current", "effective_start_date", "effective_end_date"
)

dim_product_df.write.format("delta").mode("overwrite").saveAsTable("gbmart.gold.dim_product")
print(f"dim_product rows: {spark.table('gbmart.gold.dim_product').count():,}")
```
This is the identical select-and-overwrite pattern from `dim_customer`, applied to `silver.products`: `product_sk`/`product_id` are the surrogate/natural key pair, `product_name`/`category`/`sub_category` are what "revenue by category" reporting groups and filters by, `discounted_price_inr` is the attribute that actually changes and is the reason this dimension is SCD2 at all, and `is_current`/`effective_start_date`/`effective_end_date` are the same SCD2 control columns as `dim_customer`.

**Tags**
- spark (tool)
- data-wrangling / dataframe-processing (skill)

---

## Input 5

**Type:** Choice

**Question:** Why is `discounted_price_inr` specifically the reason `dim_product` is tracked as SCD2 rather than SCD1?

**Options:**
- Because product names change frequently
- Because price is the attribute that actually changes over time, and price history is the textbook use case for SCD2
- Because `dim_product` needs a longer surrogate key than other dimensions
- Because SCD1 cannot be applied to product tables

**Correct Options:**
- Because price is the attribute that actually changes over time, and price history is the textbook use case for SCD2

**Solution:**
SCD2 exists specifically to preserve history when an attribute changes — a product's price changing over time, and needing to know what price was in effect for a given past sale, is exactly the scenario SCD2 is built for. Attributes that don't need historical tracking (like a lookup table's display name) are handled with SCD1 instead.

**Tags**
- approach (skill)

---

## Scenario 2 — dim_date: A Generated Dimension, Not Copied from Silver

**Overview:** Unlike `dim_customer` and `dim_product`, GlobalMart's date dimension isn't sourced from any Silver table at all — it's generated directly from the actual date range `fact_sales` will need (from the earliest order to the latest delivery), producing a standard Kimball-style date dimension with a pre-computed time hierarchy, rather than an arbitrarily wide hardcoded range.

**Outcome:** `dim_date` built with one row per calendar day across exactly the real date range GlobalMart's orders and deliveries span, with `date_key`, `day_of_week`, `month`, `quarter`, `year`, and `is_weekend` all pre-computed.

---

## Input 6

**Type:** Text

### Build dim_date from real data bounds

```python
date_bounds = spark.table("gbmart.silver.orders").select(
    min("order_date").alias("min_date"),
    max("actual_delivery_date").alias("max_date")
).collect()[0]

min_date, max_date = date_bounds["min_date"], date_bounds["max_date"]

date_range_df = spark.sql(f"""
    SELECT explode(sequence(to_date('{min_date}'), to_date('{max_date}'), interval 1 day)) AS date
""")

dim_date_df = date_range_df.select(
    date_format(col("date"), "yyyyMMdd").cast("int").alias("date_key"),
    col("date"),
    date_format(col("date"), "EEEE").alias("day_of_week"),
    month(col("date")).alias("month"),
    quarter(col("date")).alias("quarter"),
    year(col("date")).alias("year"),
    (dayofweek(col("date")).isin([1, 7])).alias("is_weekend")
)

dim_date_df.write.format("delta").mode("overwrite").saveAsTable("gbmart.gold.dim_date")
print(f"dim_date rows: {spark.table('gbmart.gold.dim_date').count():,}")
```

---

## Input 7

**Type:** Choice

**Question:** Why is `date_key` stored as an integer in `yyyyMMdd` form (e.g. `20260115`) instead of as a native `DATE` type?

**Options:**
- Delta tables cannot store `DATE` type columns
- It's the standard Kimball convention — an integer surrogate key joins and partitions faster than a `DATE` type, while the actual `date` column is kept separately for real date-math and display
- `DATE` columns can't be used in a `WHERE` clause
- It saves storage space compared to any other column in the table

**Correct Options:**
- It's the standard Kimball convention — an integer surrogate key joins and partitions faster than a `DATE` type, while the actual `date` column is kept separately for real date-math and display

**Solution:**
`dim_date` keeps both: `date_key` as a fast-joining integer surrogate key, and `date` itself as a real `DATE` type for anything that needs actual date arithmetic or display formatting. This is standard Kimball dimensional modeling practice, not specific to Delta or Databricks.

**Tags**
- approach (skill)

---

## Input 8

**Type:** Short Answer

**Question:** Why does this notebook derive `dim_date`'s range from `MIN(order_date)`/`MAX(actual_delivery_date)` in `silver.orders`, instead of hardcoding an arbitrary wide range like all of 2020–2030?

**Template:** null

**Tags**
- approach (skill)

---

## Scenario 3 — dim_address & dim_payment_method: Generating a New Surrogate Key

**Overview:** `silver.address` and `silver.payment_methods` don't have their own surrogate keys the way `silver.customers`/`silver.products` do, since Silver never needed SCD2 versioning for either. Gold generates one here for both, by hashing each table's natural key — so that every dimension, regardless of whether it's SCD1, SCD2, or a simple lookup, can be joined to `fact_sales` the exact same way, with no special-case logic per dimension type.

**Outcome:** `dim_address` and `dim_payment_method` built, each with a newly-generated `sha2`-based surrogate key.

---

## Input 9

**Type:** Text

### Build dim_address

| Column | Why it's here |
|---|---|
| `address_sk` | Even an SCD1 dimension gets a surrogate key — keeps the join pattern uniform across every dimension, so `fact_sales` doesn't need special-case logic per dimension |
| `address_id` | Business key, traces back to source |
| `customer_id` | Lets you filter "this customer's addresses" without going through the fact table |
| `city`, `state`, `pincode` | The entire reason this dimension exists — "revenue by city/state" reporting |
| `address_type` | Distinguishes Billing vs Shipping when it matters for a fact row |

```python
dim_address_df = spark.table("gbmart.silver.address").select(
    sha2(col("address_id"), 256).alias("address_sk"),
    "address_id", "customer_id", "city", "state", "pincode", "address_type"
)

dim_address_df.write.format("delta").mode("overwrite").saveAsTable("gbmart.gold.dim_address")
print(f"dim_address rows: {spark.table('gbmart.gold.dim_address').count():,}")
```

---

## Input 10

**Type:** Choice

**Question:** Why does `dim_address` get its own generated surrogate key (`address_sk`), even though it's a simple SCD1 dimension with no version history to track?

**Options:**
- Surrogate keys are legally required for GDPR compliance
- It keeps the join pattern uniform across every dimension — `fact_sales` doesn't need special-case logic depending on whether a dimension is SCD1, SCD2, or a lookup
- SCD1 dimensions cannot use their natural key for any purpose
- It makes the table smaller on disk

**Correct Options:**
- It keeps the join pattern uniform across every dimension — `fact_sales` doesn't need special-case logic depending on whether a dimension is SCD1, SCD2, or a lookup

**Solution:**
Whether a dimension is SCD1 (no history), SCD2 (full history), or a simple lookup, giving every one of them a surrogate key means anything joining to a dimension does it the same way every time — no conditional logic based on which "kind" of dimension it's joining to.

**Tags**
- approach (skill)

---

## Input 11

**Type:** Code

**Question:** Build `dim_payment_method` using the same surrogate-key-generation pattern as `dim_address`: hash the natural key to create the surrogate key, then select the columns GlobalMart's Gold layer needs from `silver.payment_methods`, and overwrite `gbmart.gold.dim_payment_method`.

**Language:** python

**Snippet:**
```python
dim_payment_method_df = spark.table("gbmart.silver.payment_methods").select(
    # your column list here, including a generated surrogate key
)

# your write code here
```

**Solution:**
```python
dim_payment_method_df = spark.table("gbmart.silver.payment_methods").select(
    sha2(col("payment_method_id"), 256).alias("payment_method_sk"),
    "payment_method_id", "method_name"
)

dim_payment_method_df.write.format("delta").mode("overwrite").saveAsTable("gbmart.gold.dim_payment_method")
print(f"dim_payment_method rows: {spark.table('gbmart.gold.dim_payment_method').count():,}")
```
Same pattern as `dim_address`: `sha2(...)` over the natural key (`payment_method_id`) generates the surrogate key, since `silver.payment_methods` doesn't have one of its own. `method_name` is included because `PM-001` on its own means nothing to a business user without the human-readable value alongside it.

**Tags**
- spark (tool)
- data-wrangling / dataframe-processing (skill)

---

## Scenario 4 — dim_orders: A Degenerate Dimension

**Overview:** `dim_orders` is different from every other dimension built so far: `order_id` itself will live directly on `fact_sales` (carried through from `silver.order_items`/`orders`), which is what makes `dim_orders` a degenerate dimension. It still gets built here, and still gets its own generated surrogate key for uniformity with the rest of the star schema — but two of its columns, `shipping_tier_id` and `supplier_id`, are deliberately left as plain, un-decoded IDs, since this build has no `dim_supplier` or shipping-tier-name lookup table.

**Outcome:** `dim_orders` built with its own generated surrogate key, carrying `order_channel` as the one attribute with real standalone reporting value.

---

## Input 12

**Type:** Text

### Build dim_orders

| Column | Why it's here |
|---|---|
| `order_sk` | Join target for `fact_sales` — same uniformity reason as every other dimension |
| `order_id` | Business key, traces back to source |
| `customer_id` | Lets you filter "this customer's orders" without going through the fact table |
| `order_date` | Order header date — also independently available via `dim_date` through the fact, kept here too since it's a natural attribute of the order itself |
| `shipping_tier_id`, `supplier_id` | Carried as plain IDs — no backing lookup table exists for either (no `dim_supplier`, no shipping-tier names), so they stay undecoded here rather than needing their own dimension |
| `order_channel` | The one attribute with real reporting value — "Online" vs "Retail PoS" — worth a dimension column on its own |

```python
dim_orders_df = spark.table("gbmart.silver.orders").select(
    sha2(col("order_id"), 256).alias("order_sk"),
    "order_id", "customer_id", "order_date",
    "shipping_tier_id", "supplier_id", "order_channel"
)

dim_orders_df.write.format("delta").mode("overwrite").saveAsTable("gbmart.gold.dim_orders")
print(f"dim_orders rows: {spark.table('gbmart.gold.dim_orders').count():,}")
```

---

## Input 13

**Type:** Short Answer

**Question:** This build deliberately does not create a `dim_supplier` table or a shipping-tier-name lookup table, even though `dim_orders` carries `supplier_id` and `shipping_tier_id` as plain, un-decoded IDs. Based on the rationale given for this dimension, why is that an acceptable modeling choice here rather than a missing piece?

**Template:** null

**Tags**
- data-modeling / dimension-design (skill)

---

## Input 14

**Type:** Choice

**Question:** What makes `dim_orders` a "degenerate dimension"?

**Options:**
- It has fewer columns than the other dimensions
- `order_id` lives directly on `fact_sales` itself (carried through from `silver.order_items`/`orders`), rather than only being reachable through a dimension join
- It uses SCD1 instead of SCD2
- It was built last in this notebook

**Correct Options:**
- `order_id` lives directly on `fact_sales` itself (carried through from `silver.order_items`/`orders`), rather than only being reachable through a dimension join

**Solution:**
A degenerate dimension is one whose key already lives on the fact table directly, rather than requiring a join to reach it. `order_id` is carried onto `fact_sales` straight from `silver.order_items`/`orders` — `dim_orders` still gets built for reporting convenience, but `fact_sales` doesn't need to join it to know which order a row belongs to.

**Tags**
- data-modeling / dimension-design (skill)

---

## Scenario 5 — Verify All Dimensions

**Overview:** With all 6 dimensions built — `dim_customer`, `dim_product`, `dim_date`, `dim_address`, `dim_payment_method`, and `dim_orders` — this final scenario confirms each one landed correctly before moving on to building `fact_sales` itself in the next session.

**Outcome:** A verified row and column count for every one of the 6 dimension tables.

---

## Input 15

**Type:** Text

### Verify

```python
for table in ["dim_customer", "dim_product", "dim_date", "dim_address", "dim_payment_method", "dim_orders"]:
    df = spark.table(f"gbmart.gold.{table}")
    print(f"{table:25s}: {df.count():>8,} rows, {len(df.columns)} columns")
```

---

## Input 16

**Type:** Short Answer

**Question:** List the row count and column count your verification loop printed for each of the 6 dimension tables.

**Template:** null

**Tags**
- data-modeling / dimension-design (skill)

---

## Input 17

**Type:** Choice

**Question:** Which of these 6 dimensions does the real `fact_sales` build actually join to by its generated surrogate key (`customer_sk`, `product_sk`, `address_sk`, etc.)?

**Options:**
- All 6, always by surrogate key
- Only `dim_customer` and `dim_product`, since those are the SCD2 ones
- None — every join in the real `fact_sales` build uses natural/business keys instead
- Only `dim_date`, via `date_key`

**Correct Options:**
- None — every join in the real `fact_sales` build uses natural/business keys instead

**Solution:**
This is a real, deliberate simplification in this training build: even though all 6 dimensions here get their own proper surrogate key, `fact_sales` joins to `silver.*` tables and `gold.dim_date` entirely by natural/business keys (`Order_ID`, `Product_ID`, `Customer_ID`, and `order_date` = `dim_date.date`) — never by a dimension's surrogate key. The surrogate keys still matter (they're what makes each dimension's own versioning and joins-elsewhere work), but `fact_sales` itself doesn't use them.

**Tags**
- data-modeling / dimension-design (skill)
