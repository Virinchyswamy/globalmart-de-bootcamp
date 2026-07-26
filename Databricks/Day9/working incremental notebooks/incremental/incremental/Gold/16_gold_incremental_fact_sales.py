# Databricks notebook source
# MAGIC %md
# MAGIC # Gold Incremental — fact_sales (CDF + MERGE)
# MAGIC **GlobalMart | Tredence DE Advanced Training | Day 12 Pattern**
# MAGIC
# MAGIC | | |
# MAGIC |---|---|
# MAGIC | **Grain** | One row per order line item (`order_items`) |
# MAGIC | **Source** | `silver.order_items` (CDF), `silver.orders`, `silver.products`, `silver.payments`, `silver.address`, `gold.dim_date` |
# MAGIC | **Target** | `gbmart.gold.fact_sales` |
# MAGIC | **Write strategy** | MERGE on `fact_sales_sk` — safe to re-run |
# MAGIC
# MAGIC ### Two cases handled in this notebook
# MAGIC
# MAGIC | Case | What happened | How we handle it |
# MAGIC |---|---|---|
# MAGIC | **A — New order_items** | `OR-900001`/`OR-900002` inserted via Lakeflow CDC + Autoloader; `silver.order_items` now has new rows | CDF read → build fact rows → MERGE INSERT |
# MAGIC | **B — NULL Payment_IDs resolved** | `PAY-900001`/`PAY-900002` landed in `silver.payments` via notebook 14 | LEFT JOIN update — fact rows for those orders now get real Payment_IDs |
# MAGIC
# MAGIC ### Run order dependency
# MAGIC ```
# MAGIC 10_products_incremental_scd2_merge.ipynb      ← Silver products SCD2
# MAGIC 11_customers_incremental_scd2_merge.ipynb     ← Silver customers SCD2
# MAGIC 12_orders_incremental_scd1_merge.ipynb        ← Silver orders SCD1
# MAGIC 13_order_items_incremental_scd1_merge.ipynb   ← Silver order_items SCD1
# MAGIC 14_payments_incremental_scd1_merge.ipynb      ← Silver payments SCD1
# MAGIC 15_gold_incremental_dim_refresh.ipynb         ← Gold dim_customer + dim_product refresh
# MAGIC 16_gold_incremental_fact_sales.ipynb          ← THIS NOTEBOOK
# MAGIC ```
# MAGIC All Silver notebooks must complete before this runs.
# MAGIC
# MAGIC ### The flow
# MAGIC | Step | What it does |
# MAGIC |---|---|
# MAGIC | 1 | Setup + baseline |
# MAGIC | 2 | CDF read — new order_items from Silver |
# MAGIC | 3 | Build fact rows for new order_items (same joins as full-load) |
# MAGIC | 4 | MERGE new fact rows into fact_sales |
# MAGIC | 5 | Resolve NULL Payment_IDs (Case B) |
# MAGIC | 6 | Verify — row count, NULL check, spot-check new orders |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Setup + Baseline

# COMMAND ----------

from pyspark.sql.functions import *
from pyspark.sql.window import Window
from delta.tables import DeltaTable

CATALOG          = "harsh_kumar01_npmentorskool_onmicrosoft_com"
SILVER_OI_TABLE  = f"{CATALOG}.silver.order_items"
FACT_TABLE       = f"{CATALOG}.gold.fact_sales"

baseline_count = spark.table(FACT_TABLE).count()
null_payment_before = spark.table(FACT_TABLE).filter(col("Payment_ID").isNull()).count()

print(f"fact_sales before this run     : {baseline_count:,} rows")
print(f"  of which NULL Payment_ID     : {null_payment_before:,} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 — CDF Read: New Order Items from Silver
# MAGIC
# MAGIC Read only the order_item rows that arrived AFTER the full-load Silver notebook
# MAGIC (`05_order_items_data_cleaning_dq_checks.ipynb`) consumed version 0.
# MAGIC
# MAGIC These are the items for `OR-900001` and `OR-900002` inserted via Lakeflow CDC
# MAGIC and then merged into Silver by notebook 13.

# COMMAND ----------

df = spark.sql(f"DESCRIBE HISTORY {SILVER_OI_TABLE}") 
df.display()

# COMMAND ----------

# Set to the version consumed by the full-load Silver notebook
LAST_PROCESSED_VERSION = 6  # <-- update from DESCRIBE HISTORY output above

new_items_df = (
    spark.read.format("delta")
        .option("readChangeFeed", "true")
        .option("startingVersion", LAST_PROCESSED_VERSION + 1)
        .table(SILVER_OI_TABLE)
        .filter(col("_change_type").isin(["insert", "update_postimage"]))
)

new_item_count = new_items_df.count()
print(f"New/changed order_item rows via CDF: {new_item_count:,}")

if new_item_count > 0:
    new_items_df.select("order_item_id", "order_id", "product_id", "quantity", "_change_type").display()
else:
    print("No new order_items found. Skipping Case A (will still run Case B — NULL Payment_ID fix).")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 — Build Fact Rows for New Order Items
# MAGIC
# MAGIC Same join chain as the full-load notebook (`02_build_fact_sales.ipynb`):
# MAGIC ```
# MAGIC new_items
# MAGIC   → silver.orders     (get Customer_ID + order_date for Time_ID lookup)
# MAGIC   → silver.products   (is_current = true → Actual_price, Discounted_price)
# MAGIC   → gold.dim_date     (order_date → Time_ID)
# MAGIC   → silver.address    (prefer Shipping type per customer → Address_ID)
# MAGIC   → silver.payments   (order_id → Payment_ID)
# MAGIC ```
# MAGIC
# MAGIC For `OR-900001`/`OR-900002`: `silver.payments` now has their payment rows
# MAGIC (after notebook 14), so `Payment_ID` will resolve — no NULLs on new inserts.

# COMMAND ----------

if new_item_count > 0:

    # 3a — Grain: new order_items
    grain_df = new_items_df.select(
        col("order_item_id"),
        col("order_id").alias("Order_ID"),
        col("product_id").alias("Product_ID"),
        col("quantity").alias("Quantity_purchased")
    )

    # 3b — Order header: Customer_ID + order_date for Time_ID
    orders_df = spark.table(f"{CATALOG}.silver.orders") \
        .select(col("order_id").alias("Order_ID"), col("customer_id").alias("Customer_ID"), "order_date")
    base_df = grain_df.join(orders_df, "Order_ID")

    # 3c — Product prices (current version only)
    products_current = spark.table(f"{CATALOG}.silver.products").filter("is_current = true") \
        .select(
            col("product_id").alias("Product_ID"),
            col("actual_price_inr").alias("Actual_price"),
            col("discounted_price_inr").alias("Discounted_price")
        )
    enriched_df = base_df.join(products_current, "Product_ID")

    # 3d — Time_ID from dim_date
    dim_date_df = spark.table(f"{CATALOG}.gold.dim_date") \
        .select("date", col("date_key").alias("Time_ID"))
    enriched_df = enriched_df.join(dim_date_df, enriched_df.order_date == dim_date_df.date, "left")

    # 3e — Address_ID: prefer Shipping address per customer
    address_window = Window.partitionBy("customer_id").orderBy(
        when(col("address_type").contains("Shipping"), 0).otherwise(1)
    )
    address_primary = spark.table(f"{CATALOG}.silver.address") \
        .withColumn("_rank", row_number().over(address_window)) \
        .filter("_rank = 1") \
        .select(col("customer_id").alias("Customer_ID"), col("address_id").alias("Address_ID"))
    enriched_df = enriched_df.join(address_primary, "Customer_ID", "left")

    # 3f — Payment_ID (should now resolve for OR-900001/OR-900002 after notebook 14)
    payments_df = spark.table(f"{CATALOG}.silver.payments") \
        .select(col("order_id").alias("Order_ID"), col("payment_id").alias("Payment_ID"))
    enriched_df = enriched_df.join(payments_df, "Order_ID", "left")

    # 3g — Final select with fact_sales_sk + Sales_amount
    new_fact_df = enriched_df \
        .withColumn("fact_sales_sk", sha2(col("order_item_id"), 256)) \
        .withColumn("Sales_amount", col("Quantity_purchased") * col("Discounted_price")) \
        .select(
            "fact_sales_sk", "Payment_ID", "Customer_ID", "Product_ID", "Order_ID", "Address_ID",
            "Time_ID", "Quantity_purchased", "Actual_price", "Discounted_price", "Sales_amount"
        )

    print(f"New fact rows ready to MERGE: {new_fact_df.count():,}")
    print(f"  NULL Payment_ID in new rows: {new_fact_df.filter(col('Payment_ID').isNull()).count():,}  (expected 0 after notebook 14)")
    new_fact_df.display()

else:
    new_fact_df = None
    print("No new fact rows to build.")

# COMMAND ----------

# DBTITLE 1,Cell 9
if new_item_count > 0:

    # 3a — Grain: new order_items
    grain_df = new_items_df.select(
        col("order_item_id"),
        col("order_id").alias("Order_ID"),
        col("product_id").alias("Product_ID"),
        col("quantity").alias("Quantity_purchased")
    )

    # 3b — Order header: Customer_ID + order_date for Time_ID
    orders_df = spark.table(f"{CATALOG}.silver.orders") \
        .select(
            col("order_id").alias("Order_ID"),
            col("customer_id").alias("Customer_ID"),
            col("order_date")
        )

    base_df = grain_df.join(orders_df, "Order_ID", "inner")

    # 3c — Product prices (current version only)
    products_current = spark.table(f"{CATALOG}.silver.products") \
        .filter("is_current = true") \
        .select(
            col("product_id").alias("Product_ID"),
            col("actual_price_inr").alias("Actual_price"),
            col("discounted_price_inr").alias("Discounted_price")
        )

    enriched_df = base_df.join(products_current, "Product_ID", "inner")

    # 3d — Time_ID from dim_date
    dim_date_df = spark.table(f"{CATALOG}.gold.dim_date") \
        .select("date", col("date_key").alias("Time_ID"))

    enriched_df = enriched_df.join(
        dim_date_df,
        enriched_df.order_date == dim_date_df.date,
        "left"
    )

    # 3e — Address_ID
    address_window = Window.partitionBy("customer_id").orderBy(
        when(col("address_type").contains("Shipping"), 0).otherwise(1)
    )

    address_primary = spark.table(f"{CATALOG}.silver.address") \
        .withColumn("_rank", row_number().over(address_window)) \
        .filter("_rank = 1") \
        .select(
            col("customer_id").alias("Customer_ID"),
            col("address_id").alias("Address_ID")
        )

    enriched_df = enriched_df.join(address_primary, "Customer_ID", "left")

    # 3f — Payment_ID
    payments_df = spark.table(f"{CATALOG}.silver.payments") \
        .select(
            col("order_id").alias("Order_ID"),
            col("payment_id").alias("Payment_ID")
        )

    enriched_df = enriched_df.join(payments_df, "Order_ID", "left")

    # 3g — Final fact rows
    new_fact_df = (
        enriched_df
        .withColumn("fact_sales_sk", sha2(col("order_item_id"), 256))
        .withColumn("Sales_amount", col("Quantity_purchased") * col("Discounted_price"))
        .select(
            "fact_sales_sk",
            "Payment_ID",
            "Customer_ID",
            "Product_ID",
            "Order_ID",
            "Address_ID",
            "Time_ID",
            "Quantity_purchased",
            "Actual_price",
            "Discounted_price",
            "Sales_amount"
        )
    )

    print(f"New fact rows ready to MERGE: {new_fact_df.count():,}")
    print(f"NULL Payment_ID in new rows: {new_fact_df.filter(col('Payment_ID').isNull()).count():,}")
    new_fact_df.display()

else:
    new_fact_df = None
    print("No new fact rows to build.")

# COMMAND ----------

# 1. Check schema of silver.orders
orders_df = spark.table(f"{CATALOG}.silver.orders")
orders_df.printSchema()

# 2. Show first 10 rows
orders_df.limit(10).display()

# 3. Check whether Order_IDs OR-900001 and OR-900002 exist
orders_df.filter(col("order_id").isin("OR-900001", "OR-900002")).display()

# 4. Compare join keys between new_items_df and silver.orders
print("new_items_df schema:")
new_items_df.printSchema()
print("orders_df schema:")
orders_df.printSchema()

print("Distinct order_id values in new_items_df:")
new_items_df.select("order_id").distinct().display()
print("Distinct order_id values in orders_df:")
orders_df.select("order_id").distinct().display()

# 5. Identify why the inner join returns 0 rows
# Check for whitespace, case, or datatype mismatches
from pyspark.sql.functions import trim, lower

# Check for trimmed and lowercased values
new_items_ids = new_items_df.select(trim(lower(col("order_id"))).alias("order_id")).distinct()
orders_ids = orders_df.select(trim(lower(col("order_id"))).alias("order_id")).distinct()

print("Trimmed/lowercased order_id values in new_items_df:")
new_items_ids.display()
print("Trimmed/lowercased order_id values in orders_df:")
orders_ids.display()

# Check for datatype mismatches
print("new_items_df order_id type:", [f.dataType for f in new_items_df.schema.fields if f.name == "order_id"])
print("orders_df order_id type:", [f.dataType for f in orders_df.schema.fields if f.name == "order_id"])

# 6. Suggest the fix
# If join keys differ by case, whitespace, or datatype, standardize before join
grain_df_fixed = new_items_df.select(
    col("order_item_id"),
    trim(lower(col("order_id"))).alias("Order_ID"),
    col("product_id").alias("Product_ID"),
    col("quantity").alias("Quantity_purchased")
)

orders_df_fixed = orders_df.select(
    trim(lower(col("order_id"))).alias("Order_ID"),
    col("customer_id").alias("Customer_ID"),
    "order_date"
)

base_df_fixed = grain_df_fixed.join(orders_df_fixed, "Order_ID", "inner")
print("Row count after fixed join:", base_df_fixed.count())
base_df_fixed.display()

# COMMAND ----------

# 1. Check logic used to build silver.orders (show notebook code if available)
# If not, inspect schema and row counts in bronze.orders and silver.orders
bronze_orders = spark.table(f"{CATALOG}.bronze.orders")
silver_orders = spark.table(f"{CATALOG}.silver.orders")

print("Bronze orders schema:")
bronze_orders.printSchema()
print("Silver orders schema:")
silver_orders.printSchema()

print("Bronze orders row count:", bronze_orders.count())
print("Silver orders row count:", silver_orders.count())

# Check if OR-900001/2 exist in bronze.orders and silver.orders
bronze_orders.filter(col("order_id").isin("OR-900001", "OR-900002")).display()
silver_orders.filter(col("order_id").isin("OR-900001", "OR-900002")).display()

# 2. Check incremental CDF logic (if CDF is used for silver.orders)
# Show latest CDF records in bronze.orders
bronze_orders_cdf = (
    spark.read.format("delta")
        .option("readChangeFeed", "true")
        .option("startingVersion", 0)
        .table(f"{CATALOG}.bronze.orders")
        .filter(col("_change_type").isin(["insert", "update_postimage"]))
)
bronze_orders_cdf.filter(col("order_id").isin("OR-900001", "OR-900002")).display()

# 3. Check LAST_PROCESSED_VERSION for silver.orders
spark.sql(f"DESCRIBE HISTORY {CATALOG}.silver.orders").orderBy(desc("version")).limit(5).display()

# 4. Check MERGE condition in silver.orders (if available)
# Show code for MERGE if possible, else check for duplicate keys
silver_orders.groupBy("order_id").count().filter(col("count") > 1).display()

# 5. Check Lakeflow pipeline/job execution (show history if available)
spark.sql(f"DESCRIBE HISTORY {CATALOG}.silver.orders").select("version", "timestamp", "operation", "operationParameters").orderBy(desc("version")).limit(5).display()

# 6. Check for filters or transformations dropping records
# Compare row counts and key values between bronze.orders and silver.orders
bronze_ids = bronze_orders.select("OrderID").distinct()
silver_ids = silver_orders.select("OrderID").distinct()

bronze_ids.filter(col("order_id").isin("OR-900001", "OR-900002")).display()
silver_ids.filter(col("order_id").isin("OR-900001", "OR-900002")).display()

# Find bronze orders not in silver.orders
bronze_ids.join(silver_ids, "order_id", "left_anti").display()

# COMMAND ----------

new_items_df.select("order_id", "order_item_id").display()

# COMMAND ----------

spark.table(f"{CATALOG}.bronze.orders") \
.filter(col("OrderID").isin("OR-900001","OR-900002")) \
.display()

# COMMAND ----------

spark.table(f"{CATALOG}.silver.orders") \
.filter(col("order_id").isin("OR-900001","OR-900002")) \
.display()

# COMMAND ----------

print("new_items_df:", new_items_df.count())

base_df = grain_df.join(orders_df, "Order_ID")
print("after orders join:", base_df.count())

enriched_df = base_df.join(products_current, "Product_ID")
print("after products join:", enriched_df.count())

enriched_df = enriched_df.join(
    dim_date_df,
    enriched_df.order_date == dim_date_df.date,
    "left"
)
print("after date join:", enriched_df.count())

enriched_df = enriched_df.join(address_primary, "Customer_ID", "left")
print("after address join:", enriched_df.count())

enriched_df = enriched_df.join(payments_df, "Order_ID", "left")
print("after payment join:", enriched_df.count())

# COMMAND ----------

new_items_df.select("order_id").distinct().display()

# COMMAND ----------

spark.table(f"{CATALOG}.silver.orders") \
    .filter(col("order_id").isin("OR-900001", "OR-900002")) \
    .display()

# COMMAND ----------

spark.table(f"{CATALOG}.bronze.orders") \
    .filter(col("OrderID").isin("OR-900001", "OR-900002")) \
    .display()

# COMMAND ----------

spark.table(f"{CATALOG}.bronze.orders") \
    .filter(col("order_id").isin("OR-900001", "OR-900002")) \
    .display()

# COMMAND ----------

# DBTITLE 1,Cell 20
# 1. Is bronze.orders CDF returning OR-900001 and OR-900002?
# Use LAST_PROCESSED_VERSION + 1 — CDF is not recorded from v0 on streaming tables
bronze_orders_cdf = (
    spark.read.format("delta")
        .option("readChangeFeed", "true")
        .option("startingVersion", 1)
        .table(f"{CATALOG}.bronze.orders")
        .filter(col("_change_type").isin(["insert", "update_postimage"]))
)
bronze_orders_cdf.filter(col("OrderID").isin("OR-900001", "OR-900002")).display()

# 2. Is LAST_PROCESSED_VERSION correct? (Check history for silver.orders)
spark.sql(f"DESCRIBE HISTORY {CATALOG}.silver.orders").orderBy(desc("version")).limit(5).display()

# 3. Is startingVersion correct? (Check code for CDF read in silver.orders notebook)
# Example: startingVersion = LAST_PROCESSED_VERSION + 1

# 4. Is there any filter removing insert records? (Check CDF read logic)
cdf_df = (
    spark.read.format("delta")
        .option("readChangeFeed", "true")
        .option("startingVersion", 1)
        .table(f"{CATALOG}.bronze.orders")
        .filter(col("_change_type").isin(["insert", "update_postimage"]))
)
cdf_df.filter(col("OrderID").isin("OR-900001", "OR-900002")).display()

# 5. Does the MERGE include whenNotMatchedInsertAll()? (Check merge code)
merge_code = """
MERGE INTO {CATALOG}.silver.orders AS tgt
USING cdf_df AS src
ON tgt.order_id = src.order_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
"""
print("Check if your notebook includes whenNotMatchedInsertAll() or equivalent.")

# 6. Did the MERGE actually insert OR-900001 and OR-900002? (Check post-merge)
spark.table(f"{CATALOG}.silver.orders").filter(col("order_id").isin("OR-900001", "OR-900002")).display()

# 7. Identify the exact line where these two orders are lost.
# Compare CDF read → MERGE source → MERGE target
cdf_ids = cdf_df.select("OrderID").distinct()
silver_ids = spark.table(f"{CATALOG}.silver.orders").select(col("order_id").alias("OrderID")).distinct()
cdf_ids.join(silver_ids, "OrderID", "left_anti").filter(col("OrderID").isin("OR-900001", "OR-900002")).display()

# COMMAND ----------

spark.sql(f"DESCRIBE HISTORY {CATALOG}.silver.orders").display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 — MERGE New Fact Rows into fact_sales (Case A)
# MAGIC
# MAGIC MERGE on `fact_sales_sk` (= sha2 of `order_item_id`):
# MAGIC - **Matched** → update all columns (handles re-runs of this notebook safely)
# MAGIC - **Not matched** → insert as a new row
# MAGIC
# MAGIC Skipped if there are no new order_items.

# COMMAND ----------

if new_fact_df is not None:
    fact_table = DeltaTable.forName(spark, FACT_TABLE)

    (fact_table.alias("tgt")
        .merge(new_fact_df.alias("src"), "tgt.fact_sales_sk = src.fact_sales_sk")
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )

    after_insert_count = spark.table(FACT_TABLE).count()
    print(f"Case A — MERGE complete")
    print(f"fact_sales after Case A : {after_insert_count:,} rows  (was {baseline_count:,})")
else:
    after_insert_count = baseline_count
    print("Case A skipped — no new order_items.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5 — Resolve NULL Payment_IDs (Case B)
# MAGIC
# MAGIC When the full-load `fact_sales` was built, `OR-900001` and `OR-900002` had no
# MAGIC payment records yet — so `Payment_ID` landed as `NULL` for those order lines.
# MAGIC
# MAGIC Notebook 14 merged `PAY-900001` and `PAY-900002` into `silver.payments`.
# MAGIC This step patches the existing fact rows to fill in those NULLs.
# MAGIC
# MAGIC We target only rows where `Payment_ID IS NULL` — not the full table — so
# MAGIC we don't touch any correctly populated rows.

# COMMAND ----------

# Find fact rows that still have a NULL Payment_ID
null_payment_rows = spark.table(FACT_TABLE).filter(col("Payment_ID").isNull())
null_count = null_payment_rows.count()
print(f"fact_sales rows with NULL Payment_ID: {null_count:,}")

if null_count > 0:
    null_payment_rows.select("fact_sales_sk", "Order_ID", "Customer_ID", "Payment_ID").display()
else:
    print("No NULL Payment_IDs to resolve. Case B complete.")

# COMMAND ----------

if null_count > 0:
    # Build a lookup: Order_ID → Payment_ID from Silver (only for orders that had NULL in fact)
    null_order_ids = [row["Order_ID"] for row in null_payment_rows.select("Order_ID").distinct().collect()]

    payment_lookup = spark.table(f"{CATALOG}.silver.payments") \
        .filter(col("order_id").isin(null_order_ids)) \
        .select(col("order_id").alias("Order_ID"), col("payment_id").alias("Payment_ID_resolved"))

    resolved_count = payment_lookup.count()
    print(f"Payment rows found in Silver for the NULL orders: {resolved_count:,}  (expected {null_count:,})")
    payment_lookup.display()

    if resolved_count > 0:
        # Build a MERGE source: fact_sales_sk + resolved Payment_ID
        resolve_df = null_payment_rows.alias("f") \
            .join(payment_lookup.alias("p"), "Order_ID") \
            .select(
                col("f.fact_sales_sk"),
                col("p.Payment_ID_resolved").alias("Payment_ID"),
                col("f.Customer_ID"), col("f.Product_ID"), col("f.Order_ID"), col("f.Address_ID"),
                col("f.Time_ID"), col("f.Quantity_purchased"),
                col("f.Actual_price"), col("f.Discounted_price"), col("f.Sales_amount")
            )

        fact_table = DeltaTable.forName(spark, FACT_TABLE)

        # MERGE targeting only the NULL rows by fact_sales_sk — leaves all other rows untouched
        (fact_table.alias("tgt")
            .merge(resolve_df.alias("src"), "tgt.fact_sales_sk = src.fact_sales_sk")
            .whenMatchedUpdate(set={"Payment_ID": col("src.Payment_ID")})
            .execute()
        )

        print("Case B — NULL Payment_IDs resolved")
    else:
        print("[WARNING] Silver payments still missing for the NULL orders — notebook 14 may not have run yet.")
else:
    print("Case B not needed — no NULL Payment_IDs in fact_sales.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6 — Verify
# MAGIC
# MAGIC Four checks:
# MAGIC 1. Row count (baseline + new order_items)
# MAGIC 2. Zero NULL Payment_IDs
# MAGIC 3. New order_items for OR-900001/OR-900002 have all FKs populated
# MAGIC 4. Revenue totals (spot-check that Sales_amount computed correctly)

# COMMAND ----------

df = spark.table(FACT_TABLE)

final_count        = df.count()
null_payment_after = df.filter(col("Payment_ID").isNull()).count()

print(f"fact_sales row count     : {final_count:,}  (was {baseline_count:,} before this run)")
print(f"NULL Payment_ID          : {null_payment_after:,}  (expected 0)")

# Check all FKs
for fk in ["Payment_ID", "Customer_ID", "Product_ID", "Order_ID", "Address_ID", "Time_ID"]:
    null_count_fk = df.filter(col(fk).isNull()).count()
    status = "OK" if null_count_fk == 0 else f"[WARNING] {null_count_fk:,} NULLs"
    print(f"NULL {fk:15s}: {null_count_fk:,}  ({status})")

# COMMAND ----------

# Spot-check new order rows
print("--- fact_sales rows for OR-900001 / OR-900002 ---")
df.filter(col("Order_ID").isin(["OR-900001", "OR-900002"])) \
    .select("fact_sales_sk", "Order_ID", "Customer_ID", "Payment_ID", "Product_ID",
            "Quantity_purchased", "Discounted_price", "Sales_amount") \
    .display()

print("--- Aggregate check ---")
df.select(
    count("*").alias("total_rows"),
    sum("Quantity_purchased").alias("total_quantity"),
    sum("Sales_amount").alias("total_revenue")
).display()

# COMMAND ----------

# Delta history — confirm new MERGE versions
spark.sql(f"DESCRIBE HISTORY {FACT_TABLE}") \
    .select("version", "timestamp", "operation", "operationMetrics") \
    .orderBy(desc("version")).limit(4).display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pipeline Summary
# MAGIC
# MAGIC After all 7 incremental notebooks run in order:
# MAGIC
# MAGIC | Layer | Table | What changed |
# MAGIC |---|---|---|
# MAGIC | Silver | `products` | New price versions via SCD2 (old versions closed) |
# MAGIC | Silver | `customers` | 997 consent updates via SCD2 (old versions closed, consent columns added) |
# MAGIC | Silver | `orders` | OR-000001/2/3 already Delivered from initial load; OR-900001/OR-900002 inserted |
# MAGIC | Silver | `order_items` | OR-INC-900001/2/3 — new line items for OR-900001/OR-900002 inserted |
# MAGIC | Silver | `payments` | PAY-900001/PAY-900002 inserted |
# MAGIC | Gold | `dim_customer` | Now has 2 versions per consent customer (pre-consent + post-consent) |
# MAGIC | Gold | `dim_product` | Refreshed with latest SCD2 versions |
# MAGIC | Gold | `fact_sales` | New rows for OR-900001/OR-900002; NULL Payment_IDs resolved |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Reset (if needed)

# COMMAND ----------

# Remove only the new fact rows (keep the original full-load rows)
# spark.sql("DELETE FROM gbmart.gold.fact_sales WHERE Order_ID IN ('OR-900001', 'OR-900002')")
# print("New fact rows removed")

# To restore Payment_IDs back to NULL (simulates pre-notebook-14 state):
# spark.sql("UPDATE gbmart.gold.fact_sales SET Payment_ID = NULL WHERE Order_ID IN ('OR-900001','OR-900002')")
# print("Payment_IDs reset to NULL for test orders")