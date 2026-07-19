# Databricks notebook source
# MAGIC %md
# MAGIC # Verify Incremental Load — bronze.orders & bronze.order_items
# MAGIC **GlobalMart | Tredence DE Advanced Training**
# MAGIC
# MAGIC > **No Autoloader code in this notebook.** Unlike `customers`/`products`/
# MAGIC > `payments` (ADLS, Autoloader, ingested from this kind of notebook),
# MAGIC > `orders` and `order_items` come in via the **Lakeflow Connect**
# MAGIC > managed CDC pipeline (`globalmart-orders-cdc`), straight from the
# MAGIC > Postgres source. That pipeline has already been triggered and run from
# MAGIC > the Databricks Pipelines UI — there's no `readStream`/`writeStream`
# MAGIC > cell to run here.
# MAGIC
# MAGIC This notebook is purely **verification** — confirming the changes made
# MAGIC in Supabase (`05_make_order_changes_for_incremental.sql`: the
# MAGIC `OR-000478` update + the `OR-900001`/`OR-900002` inserts) actually landed
# MAGIC in `gbmart.bronze.orders` / `gbmart.bronze.order_items` after the
# MAGIC pipeline run.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Check 1 — Did the UPDATE on `OR-000478` Come Through?
# MAGIC Expect `actualdeliverydate` populated, and `updated_at` advanced to a
# MAGIC recent timestamp (the `trg_orders_updated_at` trigger sets this
# MAGIC automatically on every Postgres update).

# COMMAND ----------

# MAGIC %sql
# MAGIC select orderid, customerid, shippingdate, actualdeliverydate, orderchannel, updated_at
# MAGIC from harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.orders
# MAGIC where orderid = 'OR-000478';

# COMMAND ----------

# MAGIC %md
# MAGIC ## Check 2 — Did the 2 New Orders Land?
# MAGIC `OR-900001` and `OR-900002` were inserted directly into
# MAGIC `globalmart.orders` in Postgres. Expect 2 rows here.

# COMMAND ----------

# MAGIC %sql
# MAGIC select orderid, customerid, orderdate, orderchannel, updated_at
# MAGIC from harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.orders
# MAGIC where orderid in ('OR-900001', 'OR-900002');

# COMMAND ----------

# MAGIC %md
# MAGIC ## Check 3 — Total Row Count on bronze.orders
# MAGIC Should be `126,036 + 2 = 126,038`.

# COMMAND ----------

# MAGIC %sql
# MAGIC select count(*) as total_orders from harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.orders;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Check 4 — Did Matching order_items Land?
# MAGIC Only relevant if the optional `INSERT INTO globalmart.order_items` block
# MAGIC in `05_make_order_changes_for_incremental.sql` was uncommented and run.
# MAGIC Expect 0 rows if that block was left commented out, 2 rows if it was run.

# COMMAND ----------

# MAGIC %sql
# MAGIC select orderitemid, orderid, productid, quantity
# MAGIC from harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.order_items
# MAGIC where orderid in ('OR-900001', 'OR-900002');

# COMMAND ----------

# MAGIC %md
# MAGIC ## Check 5 — Total Row Count on bronze.order_items
# MAGIC Should be `377,866` (unchanged), or `377,868` if the order_items insert
# MAGIC was run.

# COMMAND ----------

# MAGIC %sql
# MAGIC select count(*) as total_order_items from harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.order_items;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Check 6 — Combined Glance
# MAGIC One quick view of both row counts side by side.

# COMMAND ----------

# MAGIC %sql
# MAGIC select 'orders' as table_name, count(*) as row_count from gbmart.bronze.orders
# MAGIC union all
# MAGIC select 'order_items', count(*) from gbmart.bronze.order_items;

# COMMAND ----------

# MAGIC %md
# MAGIC ## If the Counts Haven't Changed
# MAGIC If `total_orders` is still `126,036` with no `OR-900001`/`OR-900002`
# MAGIC rows, the Lakeflow pipeline run either hasn't happened yet, or didn't
# MAGIC pick up the Postgres changes — go back to the Pipelines UI and re-trigger
# MAGIC `globalmart-orders-cdc` before re-running these checks.
# MAGIC
# MAGIC ## Next Step
# MAGIC Once confirmed, re-run the **Silver `orders` notebook** — its
# MAGIC `MERGE INTO` will pick up both the `OR-000478` update and the 2 new
# MAGIC inserts. Then re-run **Silver `order_items`** if its matching rows were
# MAGIC added.