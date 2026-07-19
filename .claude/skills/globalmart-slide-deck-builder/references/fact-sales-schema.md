# `fact_sales` — Two Framings, One Decision Rule

There are two legitimate descriptions of `fact_sales` floating around this
project's source material, and they use **different vocabulary for the same
underlying idea**. They are not interchangeable, and mixing them mid-deck
is a real mistake, not a stylistic choice — a learner who reads "quantity" on
one slide and `Quantity_purchased` on the next will assume they're different
columns.

## The decision rule

**The moment a slide shows real code against `gbmart` (a `spark.table(...)`
call, a `SELECT` with real column names, a schema diagram meant to match what
Catalog Explorer will actually show) — use the REAL/TECHNICAL schema below,
every time, regardless of which day it is.**

The simplified/story version exists for exactly one purpose: early
motivational "why does this table matter to the business" framing, before any
real code has appeared. Once a session's notebook has real code in it, the
slide deck built for that session shouldn't fall back to simplified language
either — a learner about to open `gbmart.gold.fact_sales` needs to see
`Sales_amount`, not "line_total". (Day 1 ILT 1's deck is the one legitimate
exception — it's the pure motivational opener, before any notebook has run
real code yet.)

## Simplified / story version

Source: `globalmart_problem_statement_architecture (1).html`, Section 5. Used
for Day 1's opening motivational framing — no session's deck past that point
should use this vocabulary once its paired notebook starts touching real
columns.

- **Grain:** one row per order line item
- **Measures:** `quantity`, `unit_price`, `line_total`
- **Connects to (5 dims):** `dim_customer` (who), `dim_product` (what),
  `dim_date` (when), `dim_address` (where it shipped), `dim_payment_method`
  (how paid)
- **Framing:** "one trusted table answering what sold, when, to whom, for how
  much" — narrative language about solving GlobalMart's 5 documented business
  problems (data silos, inconsistency, access control, complex
  transformations, unclear lineage). No SQL, no PySpark, no real column names.

## Real / technical version — ground truth

Source: verified directly against `Day7/Day7_3_HOL2_Build_Gold_Layer_Fact_Sales.ipynb`
(the notebook that actually builds this table), cross-checked against
`00_Instructor_Guide_How_To_Use_This_Bootcamp.html` Section 4b and
`HOW_TO_USE_THIS_COURSE.html` Section 4b.

**Grain:** one row per `order_item` (from `silver.order_items`).

**Sources:** `silver.order_items`, `silver.orders`, `silver.products`,
`silver.payments`, `silver.address`, `gold.dim_date`.

```
gbmart.gold.fact_sales
├── fact_sales_sk        surrogate PK — the ONLY generated key in this table,
│                        sha2(order_item_id, 256)
├── Payment_ID           natural key, from silver.payments (join key: Order_ID, 1:1)
├── Customer_ID          natural key, from silver.orders
├── Product_ID           natural key, from silver.order_items
├── Order_ID             natural key, from silver.order_items/orders
├── Address_ID           natural key, from silver.address (customer's primary address —
│                        see the one-to-many trap below)
├── Time_ID              natural key = gold.dim_date.date_key, resolved via order_date
├── Quantity_purchased   measure — ADDITIVE
├── Actual_price         measure — NON-ADDITIVE (from silver.products, is_current=true)
├── Discounted_price     measure — NON-ADDITIVE (from silver.products, is_current=true)
└── Sales_amount         measure — ADDITIVE, = Quantity_purchased * Discounted_price
```

**Never SUM or AVG `Actual_price`/`Discounted_price` directly on a slide** —
they're a per-line-item snapshot, not something that means anything summed
across rows. `Quantity_purchased` and `Sales_amount` are safe to SUM/AVG, and
safe to describe that way.

### The 6 dimensions — and the natural-key rule

`dim_customer`, `dim_product`, `dim_date`, `dim_address`, `dim_payment_method`,
`dim_orders` — **all 6 have their own proper surrogate key** (built Day 6,
several as SCD2), **but `fact_sales` joins to none of them by surrogate key.**
Every join in the fact-table build (Step 2 through Step 6 of the Day 7 HOL) is
a natural/business-key join: `Order_ID`, `Product_ID`, `Customer_ID`, plain
column-to-column matches against `silver.*` tables and `gold.dim_date`. This
is a real, deliberate, documented simplification for this training build —
not a mistake to "fix" if a slide shows it, and not something to silently
correct in a diagram.

**`Payment_ID` is a pure non-joiner in `fact_sales`.** It comes from
`silver.payments` (a 1:1 join to `Order_ID`) and sits in a **completely
different ID space than `dim_payment_method`** — `fact_sales.Payment_ID` does
not resolve to `dim_payment_method`'s surrogate key or its own natural key.
Never draw or narrate a slide that joins them.

**`dim_orders` is a degenerate dimension that `fact_sales` does not join
either.** `Order_ID` lives on the fact table directly (carried through from
`silver.order_items`/`orders`), which is what makes it degenerate — but this
does not mean a slide should show `fact_sales` joining `dim_orders.order_sk`.
It doesn't happen. The only *table* `fact_sales`'s build actually joins beyond
`silver.*` is `gold.dim_date`, and even that join is by natural key
(`order_date` = `dim_date.date`) rather than `dim_date`'s surrogate key.

> **Known discrepancy, resolved toward this file's wording:**
> `HOW_TO_USE_THIS_COURSE.html` Section 4b contains looser phrasing —
> "`Order_ID` genuinely does join `dim_orders` on its natural key" — that
> reads as contradicting the "fact_sales joins none of the 6 dimensions" rule
> above. The real notebook (`Day7_3_HOL2_Build_Gold_Layer_Fact_Sales.ipynb`)
> settles it: `dim_orders` is never referenced anywhere in the fact build.
> Treat this file's wording as authoritative — `fact_sales` does not join
> `dim_orders` — and don't propagate the slide's looser phrasing into any new
> deck (including, ironically, into a rebuild of the very slide this
> discrepancy came from).

### The one-to-many trap (Address_ID)

`silver.address` links to `Customer_ID`, not to a specific order — a customer
can have more than one address (Billing, Shipping, or both). The real build
resolves this with a window function ranked per customer, preferring
`Shipping`, taking the first available:

```python
address_window = Window.partitionBy("customer_id").orderBy(
    when(col("address_type").contains("Shipping"), 0).otherwise(1)
)
address_primary = spark.table("harsh_kumar01_npmentorskool_onmicrosoft_com.silver.address") \
    .withColumn("_rank", row_number().over(address_window)) \
    .filter("_rank = 1") \
    .select(col("customer_id").alias("Customer_ID"), col("address_id").alias("Address_ID"))
```

If a slide walks through joining `fact_sales`/`order_items` to `address`, show
this same collapsing step — omitting it would teach a join that silently fans
out rows.

### Write strategy

The real build uses `overwrite` mode for `fact_sales` — "the simple,
always-correct strategy at GlobalMart's current volume," per the notebook's
own comment. Incremental `MERGE`-based refresh is introduced in Day 9-10 once
learners have felt why a full rebuild gets wasteful at scale — don't show a
Day 7-style build slide using MERGE.

### Downstream views, not direct fact_sales queries

Real business questions get answered by **views** on top of `fact_sales`
(e.g. `gold.vw_monthly_category_sales`, `gold.vw_regional_sales`), not by
every analyst writing their own join. If a slide's purpose is to show "the
actual deliverable" served to business users, showing a view is more
realistic than showing every analyst querying `fact_sales` directly — but
that's a framing choice for the session at hand, not a rule this file
enforces.
