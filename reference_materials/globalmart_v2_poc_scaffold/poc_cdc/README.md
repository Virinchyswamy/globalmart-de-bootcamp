# POC: Supabase (CDC) + ADLS → Databricks Bronze

A minimal, beginner-friendly walkthrough using just **2 source files**:

- `orders_sample.csv` (200 rows) → loaded into Supabase Postgres = "Day 1" baseline
- `day2_orders_sample.csv` (50 rows) → "Day 2" new orders, used to demonstrate CDC
- `payment_methods_010626.csv` (6 rows, from `../adls_landing/`) → ADLS file-drop ingestion (separate, simpler path)

## Prerequisites

- A Supabase project (free tier is fine) — you'll need the connection string (host, port, db, user, password)
- `pip install psycopg2-binary pandas`
- Databricks cluster with the Postgres JDBC driver (Databricks Runtime ships this by default)
- Store your Supabase password in a Databricks secret scope, e.g. `databricks secrets put-secret poc-cdc supabase-password`

## Run order

| Step | File | Where it runs | What it does |
|---|---|---|---|
| 1 | `01_create_table.sql` | Supabase SQL editor | Creates the `orders` table |
| 2 | `02_load_orders_sample.py` | Local machine | Bulk-loads `orders_sample.csv` (200 rows) into Supabase = "Day 1" |
| 3 | `03_enable_cdc.sql` | Supabase SQL editor | Enables logical replication: publication + replication slot |
| 4 | `04_databricks_initial_load.py` | Databricks notebook | JDBC read of `orders` table → `bronze.orders` (full snapshot) |
| 5 | `05_simulate_day2_changes.py` | Local machine | Inserts `day2_orders_sample.csv` (50 rows) into the **live** Supabase table = "Day 2 activity" |
| 6 | `06_databricks_cdc_capture.py` | Databricks notebook | Reads the replication slot via JDBC → see the 50 new rows as CDC events |
| 7 | `07_adls_autoloader_payment_methods.py` | Databricks notebook | Autoloader reads `payment_methods_010626.csv` from ADLS → `bronze.payment_methods` (separate, no-CDC path) |

## What you should observe

- After step 4: `bronze.orders` has exactly 200 rows.
- After step 5: the live Supabase `orders` table has 250 rows, but `bronze.orders` is still 200 (Databricks hasn't re-read yet).
- After step 6: the CDC query returns ~50 change events corresponding to the rows you just inserted — this is the proof that CDC is working. In a real pipeline, you'd parse these events and `MERGE` them into `bronze.orders`, bringing it to 250.
- Step 7 is intentionally separate — it shows the *other* ingestion pattern (new file lands → Autoloader picks it up), with no replication slot involved at all.

## If replication slot creation fails (step 3)

Some managed Postgres tiers restrict `pg_create_logical_replication_slot`. If you get a permission error:
- Check Supabase dashboard → Database → Replication (some plans expose a UI toggle)
- Fallback: skip true CDC for now, and instead add an `updated_at` column + watermark-based incremental JDBC read (this is the "Milestone 8 fallback" — still teaches incremental loading, just not WAL-based CDC)
