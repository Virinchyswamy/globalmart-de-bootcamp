# Databricks notebook source
# MAGIC %md
# MAGIC # Silver Incremental — Products (SCD2 via CDF + MERGE)
# MAGIC **GlobalMart | Tredence DE Advanced Training | Day 12 Pattern**
# MAGIC
# MAGIC | | |
# MAGIC |---|---|
# MAGIC | **Source** | `gbmart.bronze.products` — CDF enabled |
# MAGIC | **Target** | `gbmart.silver.products` |
# MAGIC | **SCD Type** | SCD2 — price change creates a new version, old version closed out |
# MAGIC
# MAGIC ### The flow
# MAGIC | Step | What it does |
# MAGIC |---|---|
# MAGIC | 1 | Read all data — current full state of Bronze |
# MAGIC | 2 | Show what changed in Bronze — inspect Delta history |
# MAGIC | 3 | Take **only** the changes — CDF read, not a full re-scan |
# MAGIC | 4 | Process **only** those changed rows — same cleaning logic as the full-load notebook, scoped down |
# MAGIC | 5 | Load into Silver — SCD2 `MERGE` (close out old version) + insert (new version / new product) |
# MAGIC | 6 | Verify |
# MAGIC
# MAGIC This is deliberately the **incremental** counterpart to
# MAGIC `03_products_data_cleaning_dq_checks.ipynb` (the full load). That
# MAGIC notebook processes all 500+ rows every run; this one processes only what
# MAGIC actually changed.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Read All Data (Current Full State of Bronze)
# MAGIC Not for processing — just to see where things stand before isolating the
# MAGIC incremental piece.

# COMMAND ----------

from pyspark.sql.functions import *
from delta.tables import DeltaTable

CATALOG      = "gbmart"
BRONZE_TABLE = "gbmart.bronze.products"
SILVER_TABLE = "gbmart.silver.products"

bronze_df = spark.table(BRONZE_TABLE)
print(f"Total rows currently in Bronze: {bronze_df.count():,}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 — Show What Changed in Bronze
# MAGIC `DESCRIBE HISTORY` shows every write to this table as a version. The
# MAGIC initial full load was one version; the incremental file
# MAGIC (`products_020626.json`) landing via Autoloader created a later version.
# MAGIC We need the version number **right before** that incremental write — CDF
# MAGIC will read everything **after** it.

# COMMAND ----------

spark.sql(f"DESCRIBE HISTORY {BRONZE_TABLE}") \
    .select("version", "timestamp", "operation", "operationMetrics") \
    .orderBy("version") \
    .display()

# COMMAND ----------

# MAGIC %md
# MAGIC Set `LAST_PROCESSED_VERSION` to the version number of the **initial full
# MAGIC load** (the version the original `03_products_data_cleaning_dq_checks.ipynb`
# MAGIC run already consumed). CDF will read everything strictly **after** this.

# COMMAND ----------

LAST_PROCESSED_VERSION = 0   # <-- set this from the history output above

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 — Take Only the Changes (CDF, Not a Full Re-Scan)
# MAGIC
# MAGIC `readChangeFeed` + `startingVersion` returns only the rows that changed
# MAGIC since `LAST_PROCESSED_VERSION` — not the whole 500+-row table.
# MAGIC `update_preimage` (the "before" snapshot of an update) is dropped; we only
# MAGIC want `insert` and `update_postimage` (the "after" state).

# COMMAND ----------

cdf_changes_df = (
    spark.read.format("delta")
        .option("readChangeFeed", "true")
        .option("startingVersion", LAST_PROCESSED_VERSION + 1)
        .table(BRONZE_TABLE)
        .filter("_change_type != 'update_preimage'")
)

print(f"Changed rows via CDF: {cdf_changes_df.count():,}")
cdf_changes_df.select("product_id", "discounted_price_inr", "_change_type", "_commit_version").display()

# COMMAND ----------

# MAGIC %md
# MAGIC **This is the core difference from a full load.** The full-load notebook
# MAGIC reads and re-processes all 500+ rows every time. This cell reads only the
# MAGIC handful of rows that actually changed — 2 price updates + 1 new product,
# MAGIC regardless of how large `bronze.products` eventually grows.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 — Process Only These Changed Rows
# MAGIC Same flatten/clean logic as the full-load notebook (`specs.*`,
# MAGIC `supplier_info.*`), just scoped to the small CDF result instead of the
# MAGIC whole table.

# COMMAND ----------

processed_df = cdf_changes_df.select(
    "product_id", "product_name", "category", "sub_category",
    "actual_price_inr", "discounted_price_inr", "rating", "num_ratings",
    col("specs.power_source").alias("power_source"),
    col("specs.country_of_origin").alias("country_of_origin"),
    col("specs.color_options").alias("color_options"),
    col("specs.is_returnable").alias("is_returnable"),
    col("specs.return_window_days").alias("return_window_days"),
    col("specs.material").alias("material"),
    col("specs.warranty_months").alias("warranty_months"),
    col("specs.weight_kg").alias("weight_kg"),
    col("supplier_info.supplier_id").alias("supplier_id"),
    col("supplier_info.name").alias("supplier_name"),
    col("supplier_info.city").alias("supplier_city"),
    "tags", "last_updated"
)

processed_df.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5 — Load into Silver: SCD2 (Close Old Version + Insert New)
# MAGIC
# MAGIC Two-step pattern, in order:
# MAGIC
# MAGIC **5a. Close out the old version** — for any `product_id` already
# MAGIC `is_current = true` in Silver where the incoming price differs, flip
# MAGIC `is_current` to `false` and stamp `effective_end_date`. This is a
# MAGIC `MERGE` that only ever updates, never inserts.
# MAGIC
# MAGIC **5b. Insert the new version** — every row in `processed_df` becomes a
# MAGIC brand-new Silver row with a fresh `product_sk`, `is_current = true`. This
# MAGIC covers both cases at once: a changed product (new price version) and a
# MAGIC genuinely new product (no prior Silver row to close out — 5a simply
# MAGIC won't match it).

# COMMAND ----------

# 5a — close out old versions where the price actually changed
silver_table = DeltaTable.forName(spark, SILVER_TABLE)

(silver_table.alias("tgt")
    .merge(
        processed_df.alias("src"),
        "tgt.product_id = src.product_id AND tgt.is_current = true "
        "AND tgt.discounted_price_inr <> src.discounted_price_inr"
    )
    .whenMatchedUpdate(set={
        "is_current": "false",
        "effective_end_date": "current_date()"
    })
    .execute()
)

print("Step 5a complete — old versions closed out where price changed")

# COMMAND ----------

# 5b — insert new versions (price changes) + brand-new products
new_versions_df = processed_df \
    .withColumn("effective_start_date", current_date()) \
    .withColumn("effective_end_date", lit(None).cast("date")) \
    .withColumn("is_current", lit(True)) \
    .withColumn("product_sk",
        sha2(concat_ws("|", col("product_id"), col("effective_start_date").cast("string")), 256)
    ) \
    .withColumn("discount_pct",
        round((col("actual_price_inr") - col("discounted_price_inr")) / col("actual_price_inr") * 100, 2)
    ) \
    .withColumn("_silver_updated_at", current_timestamp()) \
    .select(
        "product_sk", "product_id", "product_name", "category", "sub_category",
        "actual_price_inr", "discounted_price_inr", "discount_pct",
        "rating", "num_ratings",
        "power_source", "country_of_origin", "color_options", "is_returnable",
        "return_window_days", "material", "warranty_months", "weight_kg",
        "supplier_id", "supplier_name", "supplier_city",
        "tags",
        "is_current", "effective_start_date", "effective_end_date",
        "last_updated", "_silver_updated_at"
    )

new_versions_df.write.format("delta").mode("append").saveAsTable(SILVER_TABLE)
print(f"Step 5b complete — {new_versions_df.count()} new version row(s) inserted")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6 — Verify
# MAGIC Each changed `product_id` should now show **2 rows** — old version
# MAGIC (`is_current=false`, `effective_end_date` set) and new version
# MAGIC (`is_current=true`, `effective_end_date=NULL`). The new product
# MAGIC (`PRD-00501`) should show as a single `is_current=true` row.

# COMMAND ----------

df = spark.table(SILVER_TABLE)
print(f"silver.products rows : {df.count():,}")

df.filter(col("product_id").isin(["PRD-00001", "PRD-00002", "PRD-00501"])) \
  .select("product_sk", "product_id", "discounted_price_inr", "is_current",
          "effective_start_date", "effective_end_date") \
  .orderBy("product_id", "effective_start_date") \
  .display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Reset (if needed)
# MAGIC This only undoes the incremental run — re-run the full-load notebook
# MAGIC afterward to get back to a clean baseline.

# COMMAND ----------

# spark.sql(f"DELETE FROM {SILVER_TABLE} WHERE product_id IN ('PRD-00001','PRD-00002','PRD-00501') AND effective_start_date = current_date()")
# print("Incremental rows removed — re-run the full-load notebook to restore baseline")