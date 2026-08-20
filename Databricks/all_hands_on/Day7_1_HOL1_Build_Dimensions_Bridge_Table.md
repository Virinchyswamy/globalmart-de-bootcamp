---
name: Day 7 HOL 1 — Verify Dimensions + Bridge Table Concept
content_type: Scenario
overview: Before building fact_sales later today, this hands-on first confirms Day 6's 6 Gold dimensions are still healthy, then tackles a concept every star schema eventually needs to reason about — bridge tables. You will learn exactly when a many-to-one relationship (a plain foreign key) isn't enough and a genuine many-to-many relationship needs a bridge table instead, check GlobalMart's real fact_sales grain to see it doesn't need one today, and then build one small illustrative bridge table (products tagged under marketing campaigns) so the concept isn't purely theoretical — including the double-counting risk a bridge table can introduce if you forget it's many-to-many.
learning_objectives:
  - Verify a previously built set of Gold dimension tables are still healthy before building on top of them
  - Distinguish a many-to-one relationship (plain foreign key) from a many-to-many relationship (needs a bridge table)
  - Check a fact table's grain first to determine whether a bridge table is actually needed
  - Build a small illustrative bridge table connecting two dimensions with a genuine many-to-many relationship
  - Recognize and avoid the double-counting risk when joining through a bridge table
  - Write a correct multi-way attribution query across a bridge table
prerequisites:
  - Completed Day 6 HOL 1 — all 6 dimensions built in gbmart.gold
  - A Databricks workspace with read/write access to the gbmart catalog (or your own equivalent)
duration: 60 minutes
level: Intermediate
industries:
  - e-commerce
tags:
  - databricks (tool)
  - spark (tool)
  - sql (tool)
  - data-modeling / dimension-design (skill)
---

---

## Scenario 1 — Verify Day 6's Dimensions Are Still Healthy

**Overview:** Before building anything new today, this hands-on first re-runs the exact same health check Day 6 ended on. Both today's bridge-table work and the fact_sales build coming up later today assume all 6 Gold dimensions from Day 6 — `dim_customer`, `dim_product`, `dim_date`, `dim_address`, `dim_payment_method`, and `dim_orders` — are correct right now.

**Outcome:** Confirmation that all 6 Day 6 dimensions are present and healthy, with a non-zero row count each.

---

## Input 1

**Type:** Text

### Setup and verify

>[!IMPORTANT]
>The code in this hands-on uses the literal `gbmart` catalog — this is GlobalMart's own real Gold-layer run. Your own catalog will be named differently; replace `gbmart` with your own catalog name throughout.

```python
print(f"{'Table':<25} {'Rows':>10}  {'Columns':>8}")
print("-" * 48)

for table in ["dim_customer", "dim_product", "dim_date", "dim_address", "dim_payment_method", "dim_orders"]:
    df = spark.table(f"gbmart.gold.{table}")
    print(f"{table:<25} {df.count():>10,}  {len(df.columns):>8}")
```

If any table is missing or shows 0 rows, go back and re-run the relevant cell in Day 6 HOL 1 before continuing — don't skip this check.

---

## Input 2

**Type:** Short Answer

**Question:** List the row count and column count printed for each of the 6 dimension tables. Are all 6 present with a non-zero row count?

**Template:** null

**Tags**
- data-modeling / dimension-design (skill)

---

## Scenario 2 — What Is a Bridge Table, and When Do You Actually Need One?

**Overview:** Every dimension built in Day 6 relates to `fact_sales` with a clean many-to-one relationship — many order lines share one customer, many order lines share one product, and so on. A plain foreign key handles many-to-one perfectly. A bridge table exists for a different shape entirely: many-to-many, where neither side can hold a single foreign key to the other because there isn't one right answer — the textbook example is a bank account with multiple joint holders, where a person can also hold multiple accounts.

**Outcome:** A clear understanding of the many-to-one vs. many-to-many distinction, and why only the latter actually requires a bridge table.

---

## Input 3

**Type:** Text

### The concept

Every Day 6 dimension relates to `fact_sales` many-to-one: many order lines share one customer, many order lines share one product. A plain foreign key (`Customer_ID` on `fact_sales`) handles that perfectly — no extra table needed.

A **bridge table** exists for a genuinely different shape: **many-to-many**. Classic example — a bank account can have multiple joint holders, and a person can hold multiple accounts. Neither `dim_account` nor `dim_customer` can hold a single foreign key to the other, because there isn't one right answer. The fix is a third table sitting *between* the two, with one row per valid (account, holder) pair:

```
dim_customer  <---  bridge_account_holder  --->  dim_account
  customer_id         customer_id, account_id       account_id
                       (one row per pairing)
```

Anything joining fact data through this bridge has to be careful about **double-counting**: a $500 deposit touching 2 joint holders should not silently become $1,000 across the report.

---

## Input 4

**Type:** Choice

**Question:** What is the defining condition that means two dimensions need a bridge table between them, rather than a plain foreign key on one side?

**Options:**
- One of the dimensions has more rows than the other
- The relationship between them is many-to-many — neither side can hold a single foreign key to the other because there isn't one right answer
- The two dimensions are in different schemas
- One of the dimensions uses SCD2 and the other uses SCD1

**Correct Options:**
- The relationship between them is many-to-many — neither side can hold a single foreign key to the other because there isn't one right answer

**Solution:**
A plain foreign key only works when one side of a relationship can point to exactly one row on the other side (many-to-one). A bank account with multiple joint holders, where a person can also hold multiple accounts, can't be expressed that way in either direction — a third table, with one row per valid pairing, is the only way to represent it.

**Tags**
- data-modeling / dimension-design (skill)

---

## Input 5

**Type:** Choice

**Question:** What must you be careful about when joining fact data through a bridge table?

**Options:**
- Bridge tables cannot be joined more than once per query
- Double-counting — a single fact row can be multiplied across every matching row on the many-to-many side
- Bridge tables must always be cached before joining
- Bridge tables can only be queried using PySpark, never SQL

**Correct Options:**
- Double-counting — a single fact row can be multiplied across every matching row on the many-to-many side

**Solution:**
Because a bridge table's whole purpose is to let one row on either side match multiple rows on the other, joining through it can silently multiply a fact row for every match it picks up — a $500 deposit touching 2 joint holders becoming $1,000 across a report if you're not deliberate about how you aggregate afterward.

**Tags**
- data-modeling / dimension-design (skill)

---

## Scenario 3 — Does GlobalMart's fact_sales Actually Need One?

**Overview:** With the many-to-one vs. many-to-many distinction clear, the next step is checking GlobalMart's own `fact_sales` table against it — not by assumption, but by walking its actual grain. `fact_sales` (built in HOL 2 later today) has grain = one row per order line item, from `order_items`. Every relationship at that grain needs to be checked before deciding whether a bridge table is needed.

**Outcome:** A documented conclusion, grounded in `fact_sales`'s real grain, for whether GlobalMart's core model needs a bridge table today.

---

## Input 6

**Type:** Text

### Walk the grain

**Check the grain first, always.** At the `order_items` grain:

| Relationship at the `order_items` grain | Shape | Bridge needed? |
|---|---|---|
| order line → customer | many-to-one | No — plain FK |
| order line → product | many-to-one | No — plain FK |
| order line → order | many-to-one | No — plain FK |
| order line → shipping address | many-to-one (GlobalMart picks one primary address per customer) | No — plain FK |
| order line → payment | many-to-one (payments are 1:1 with orders in this model) | No — plain FK |

**Conclusion: GlobalMart's core `fact_sales` does not need a bridge table today.** This isn't a shortcut — `order_items` being the grain is exactly what already resolves the one real many-to-many relationship in this data (an order can contain many products, and a product appears on many orders). The grain choice did the work; a bridge table would be solving a problem that doesn't exist here.

---

## Input 7

**Type:** Short Answer

**Question:** In one sentence: why doesn't `fact_sales` need a bridge table today, even though "an order can contain many products, and a product can appear on many orders" is itself a many-to-many relationship?

**Template:** null

**Tags**
- data-modeling / dimension-design (skill)

---

## Input 8

**Type:** Choice

**Question:** If GlobalMart added marketing campaigns where one product can be tagged under several campaigns at once, and one campaign covers many products, which of the following would that be an example of?

**Options:**
- A many-to-one relationship, resolvable with a plain foreign key on `dim_product`
- A genuine many-to-many relationship that would require a bridge table
- Something that should be modeled as a new fact table, not a dimension relationship
- A relationship that doesn't need modeling at all

**Correct Options:**
- A genuine many-to-many relationship that would require a bridge table

**Solution:**
Neither `dim_product` nor a `dim_campaign` could hold a single foreign key to the other here — a product can belong to several campaigns, and a campaign covers several products. That's exactly the shape a bridge table exists for, unlike every relationship `fact_sales` itself actually has today.

**Tags**
- data-modeling / dimension-design (skill)

---

## Scenario 4 — Build an Illustrative Bridge: Products ↔ Campaigns

**Overview:** GlobalMart's real source systems (Postgres, ADLS) don't have a campaigns feed today — this scenario's data is deliberately synthetic and illustrative, built purely to make the bridge-table pattern concrete, not because it's part of the graded pipeline. You will build `dim_campaign` (a small new dimension, one row per campaign) and `bridge_product_campaign` (one row per product/campaign pairing), deliberately including at least one product tagged under two campaigns so the many-to-many is real, not hypothetical.

**Outcome:** `dim_campaign` and `bridge_product_campaign` built, with one product appearing under two campaigns and one campaign covering three products.

---

## Input 9

**Type:** Text

### Build dim_campaign

```python
from pyspark.sql.functions import sha2, col, lit

campaign_rows = [
    ("CMP-01", "Diwali Mega Sale",      "2025-10-15", "2025-11-05"),
    ("CMP-02", "New Year Electronics",   "2026-01-01", "2026-01-15"),
    ("CMP-03", "Summer Furniture Fest",  "2026-04-01", "2026-04-30"),
]

dim_campaign_df = spark.createDataFrame(
    campaign_rows, ["campaign_id", "campaign_name", "start_date", "end_date"]
).withColumn("campaign_sk", sha2(col("campaign_id"), 256))

dim_campaign_df.write.format("delta").mode("overwrite").saveAsTable("gbmart.gold.dim_campaign")
print(f"dim_campaign rows: {spark.table('gbmart.gold.dim_campaign').count()}")
```

---

## Input 10

**Type:** Code

**Question:** Using PySpark, build `bridge_product_campaign`: pick a handful of real `product_id`s from `dim_product` (where `is_current = true`), then create a bridge table of `(product_id, campaign_id)` pairs where at least one product is tagged under two different campaigns — the genuine many-to-many this bridge exists for.

**Language:** python

**Snippet:**
```python
sample_products = [row.product_id for row in
    spark.table("gbmart.gold.dim_product").filter("is_current = true").select("product_id").limit(6).collect()]

# your bridge rows and write code here
```

**Solution:**
```python
sample_products = [row.product_id for row in
    spark.table("gbmart.gold.dim_product").filter("is_current = true").select("product_id").limit(6).collect()]

bridge_rows = [
    (sample_products[0], "CMP-01"),
    (sample_products[0], "CMP-02"),   # same product, second campaign
    (sample_products[1], "CMP-01"),
    (sample_products[2], "CMP-01"),
    (sample_products[3], "CMP-02"),
    (sample_products[4], "CMP-03"),
]

bridge_df = spark.createDataFrame(bridge_rows, ["product_id", "campaign_id"])
bridge_df.write.format("delta").mode("overwrite").saveAsTable("gbmart.gold.bridge_product_campaign")
print(f"bridge_product_campaign rows: {spark.table('gbmart.gold.bridge_product_campaign').count()}")
```
Using real `product_id`s from `dim_product` (rather than more synthetic keys) means the bridge joins against real data. `sample_products[0]` deliberately appearing under both `CMP-01` and `CMP-02`, and `CMP-01` deliberately covering three different products, is what makes this a genuine many-to-many rather than a disguised one-to-one — notice the bridge table itself carries no measures of its own; it's pure connective plumbing between two dimensions.

**Tags**
- spark (tool)
- data-modeling / dimension-design (skill)

---

## Scenario 5 — Prove the Double-Counting Risk, Then Query It Correctly

**Overview:** With `dim_campaign` and `bridge_product_campaign` built, this scenario demonstrates exactly what a bridge table can cause if you forget it's many-to-many: joining `dim_product` straight through the bridge multiplies rows for any product tagged under more than one campaign. It then shows the correct way to attribute a real measure — `fact_sales`'s `Sales_amount` — across campaigns, where a multi-campaign product's sales are deliberately counted once per campaign it belongs to.

**Outcome:** A demonstrated row-count increase from joining `dim_product` through the bridge, and a correct sales-by-campaign attribution query using `fact_sales`.

---

## Input 11

**Type:** Text

### The double-counting demo

```python
print("Rows in dim_product BEFORE joining through the bridge:")
print(spark.table("gbmart.gold.dim_product").filter("is_current = true").count())

joined = (
    spark.table("gbmart.gold.dim_product").filter("is_current = true")
    .join(spark.table("gbmart.gold.bridge_product_campaign"), "product_id")
)
print("Rows AFTER joining through the bridge (note: product[0] now appears twice):")
joined.select("product_id", "product_name", "campaign_id").orderBy("product_id").display()
```

This is exactly the mistake a bridge table can cause if you forget it's many-to-many — joining `fact_sales` through the bridge the same way would multiply rows for any product tagged under more than one campaign.

---

## Input 12

**Type:** Short Answer

**Question:** How many rows did `dim_product` (filtered to `is_current = true`) have before joining through the bridge, and how many after? Which `product_id` appears twice in the joined result, and why?

**Template:** null

**Tags**
- data-modeling / dimension-design (skill)

---

## Input 13

**Type:** Text

### The correct attribution query

>[!IMPORTANT]
>This query reads `gbmart.gold.fact_sales`, which is built in HOL 2 later today. If you're running this notebook before HOL 2, come back to this cell afterward.

```sql
SELECT
    c.campaign_name,
    COUNT(DISTINCT f.Order_ID)  AS orders_touching_campaign,
    SUM(f.Sales_amount)         AS attributed_sales
FROM gbmart.gold.fact_sales f
JOIN gbmart.gold.bridge_product_campaign b ON f.Product_ID = b.product_id
JOIN gbmart.gold.dim_campaign c            ON b.campaign_id = c.campaign_id
GROUP BY c.campaign_name
ORDER BY attributed_sales DESC
```

---

## Input 14

**Type:** Choice

**Question:** In this attribution query, a product tagged under 2 campaigns has its sales counted once per campaign it belongs to — so the same sale can appear in more than one campaign's total. Is that a bug that needs fixing, or a deliberate business decision?

**Options:**
- A bug — each sale should only ever be attributed to exactly one campaign
- A deliberate business decision — a sale genuinely counts toward every campaign that was running for that product at the time
- A bug, but only when `COUNT(DISTINCT ...)` is used instead of `COUNT(*)`
- Neither — this query cannot actually produce that outcome

**Correct Options:**
- A deliberate business decision — a sale genuinely counts toward every campaign that was running for that product at the time

**Solution:**
This is exactly the double-counting behavior demonstrated in Input 11-12, but here it's the *correct*, intended outcome rather than a mistake: if a product really was tagged under two active campaigns, a sale of that product genuinely counts toward both campaigns' attributed sales. The risk a bridge table introduces isn't that this happens — it's forgetting that it happens, and reporting a number as if no multi-way attribution occurred.

**Tags**
- data-modeling / dimension-design (skill)

---

## Input 15

**Type:** File Upload

**Question:** Take a screenshot of your notebook output showing the campaign attribution query results (campaign_name, orders_touching_campaign, attributed_sales). Upload it here.

**Max No. of Files:** 1

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- databricks (tool)
