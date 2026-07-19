# Real Hands-On Sample Data — `reference_materials/reference_data_for_hands_on_docs/adls_data_new/`

This is the real, flat-file sample dataset available for writing hands-on
scenarios that ask a learner to work with raw/ADLS-shaped data directly
(rather than the already-built `gbmart` Bronze/Silver/Gold tables described
in `architecture-facts.md`/`fact-sales-schema.md`). It sits at:

```
C:\Yvirinchy\DE notebooks\reference_materials\reference_data_for_hands_on_docs\adls_data_new\
```

Row counts and columns below were measured directly against the real files
in this folder, not estimated — if you need a fact about this data not
listed here, go re-check the folder rather than guessing.

## The gotcha to always get right: `addresses` (folder) vs. `address` (table)

The raw folder here is **plural**, `addresses/`, because it mirrors how the
files land before ingestion. Once ingested through Autoloader, the real
table is **singular**, `harsh_kumar01_npmentorskool_onmicrosoft_com.silver.address` (see `architecture-facts.md`).
If a hands-on scenario references both the raw files and the downstream
table in the same Input, use the correct name for each — don't assume they
match, and don't silently "fix" one to match the other.

## Folder-by-folder

### `addresses/` — 3 daily drops, PascalCase, ~19-20k rows each

| File | Rows |
|---|---|
| `addresses_010626.csv` | 20,138 |
| `addresses_020626.csv` | 19,899 |
| `addresses_030626.csv` | 18,696 |

Columns: `AddressID, CustomerID, AddressLine1, City, State, PinCode, AddressType`
(`AddressType` is e.g. `Billing`/`Shipping` — this is the same one-to-many
relationship described in `fact-sales-schema.md`'s "one-to-many trap": one
`CustomerID` can have more than one address row).

### `customers/` — 3 daily drops, PascalCase, ~6.6k rows each

| File | Rows |
|---|---|
| `customers_010626.csv` | 6,666 |
| `customers_020626.csv` | 6,667 |
| `customers_030626.csv` | 6,667 |

Columns: `CustomerID, FirstName, LastName, Email, PhoneNumber, DateOfBirth,
RegistrationDate, PreferredPaymentMethodID`.

### `payments/` — 3 daily drops, PascalCase, ~42k rows each

| File | Rows |
|---|---|
| `payments_010626.csv` | 42,012 |
| `payments_020626.csv` | 42,012 |
| `payments_030626.csv` | 42,012 |

Columns: `PaymentID, OrderID, PaymentDate, GiftCardUsage, GiftCardAmount,
CouponUsage, CouponAmount, PaymentMethodID`.

### `payment_methods/` — 1 file, 5 rows total (a reference/lookup table, not a daily drop)

Full contents of `payment_methods_010626.csv`:

```
PaymentMethodID,MethodName
PM-001,Credit Card
PM-002,UPI
PM-003,Debit Card
PM-004,Net Banking
PM-005,Cash-on-Delivery
```

### `products/` — 1 file, 500 records, **nested JSON, already snake_case**

`products_010626.json` is a JSON array of 500 objects — unlike the other
folders, this one is not flat CSV and is already `snake_case` (not
PascalCase like the rest of the raw drops). Top-level keys:

```
product_id, product_name, category, sub_category, rating, num_ratings,
discounted_price_inr, actual_price_inr, specs, tags, supplier_info,
last_updated
```

`specs` is a nested object: `warranty_months, color_options, weight_kg,
country_of_origin, is_returnable, return_window_days, power_source`.
`supplier_info` is a nested object: `supplier_id, name, city`. `tags` is a
flat array of strings. If a hands-on scenario has a learner read this file
with `spark.read.json(...)`, expect a nested/struct schema, not a flat table
— flattening `specs`/`supplier_info` (e.g. with dot-notation `col("specs.weight_kg")`
or `explode` on `tags`) is a legitimate, realistic task to ask for.

### `returns/` — 1 file, 29,000 rows — supplementary, NOT one of the 7 official Bronze tables

Columns: `ReturnID, OrderId, ProductID, Return_reason, ReturnDate,
ReturnStatus, RefundAmount, ReturnMethod`.

This is real, well-formed practice data, useful for a hands-on scenario that
wants an extra join/aggregation target — but it is not part of the real
`gbmart` 7-Bronze-table pipeline described in `architecture-facts.md`. Never
describe `returns` as core pipeline data or as one of the two real ingestion
pathways' outputs; it's supplementary practice data sitting alongside the
real dataset, nothing more.

## When to use this data vs. the real `gbmart` schema

- Use this folder's real files when a hands-on scenario is teaching
  file-based ingestion mechanics directly (reading CSV/JSON off a Volume or
  ADLS path, schema inference, nested-JSON flattening, joining raw daily
  drops) — this mirrors Day 1's HOL, which works directly with uploaded CSVs
  in a Volume rather than the already-built `gbmart` tables.
- Use `architecture-facts.md`/`fact-sales-schema.md`'s real `gbmart.bronze/
  silver/gold` schema once a scenario is about a session that already has
  the pipeline built (Day 4 onward) — a learner at that point should be
  querying real Bronze/Silver/Gold tables, not raw files, unless the
  session's own notebook explicitly does otherwise.
- Never mix the two in one scenario without checking the sibling `.ipynb`
  first — if the notebook reads from a Volume path, the hands-on `.md`
  should too; if it reads `harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.customers`, the `.md` should too.
