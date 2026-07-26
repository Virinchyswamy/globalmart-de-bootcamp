# Databricks notebook source
# MAGIC %md
# MAGIC # Gold — Regional Sales Summary (Aggregated Table)
# MAGIC **GlobalMart | Tredence DE Advanced Training**
# MAGIC
# MAGIC | | |
# MAGIC |---|---|
# MAGIC | **Source** | `gbmart.gold.fact_sales` + `gbmart.gold.dim_address` |
# MAGIC | **Target** | `gbmart.gold.regional_sales_summary` |
# MAGIC | **Pattern** | Full aggregate — one row per city, built from fact_sales |
# MAGIC
# MAGIC ### Why a table, not a view?
# MAGIC The existing `vw_regional_sales` recomputes from 377K+ rows on every query.
# MAGIC This table pre-aggregates once and stores the result — dashboards query a
# MAGIC small fast table instead of the full fact. Refresh it each time new orders land.
# MAGIC
# MAGIC ### The flow
# MAGIC | Step | What it does |
# MAGIC |---|---|
# MAGIC | 1 | Read `fact_sales` + join `dim_address` |
# MAGIC | 2 | Aggregate by state + city |
# MAGIC | 3 | Write to `regional_sales_summary` |
# MAGIC | 4 | Dashboard preview — top cities + top states |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Setup

# COMMAND ----------

from pyspark.sql.functions import *

CATALOG   = "harsh_kumar01_npmentorskool_onmicrosoft_com"
AGG_TABLE = f"{CATALOG}.gold.regional_sales_summary"

fact_df    = spark.table(f"{CATALOG}.gold.fact_sales")
address_df = spark.table(f"{CATALOG}.gold.dim_address") \
                  .select("address_id", "state", "city")

print(f"fact_sales rows  : {fact_df.count():,}")
print(f"dim_address rows : {address_df.count():,}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 — Aggregate by State + City

# COMMAND ----------

regional_agg = fact_df \
    .join(address_df, fact_df.Address_ID == address_df.address_id, "left") \
    .groupBy("state", "city") \
    .agg(
        countDistinct("Order_ID").alias("total_orders"),
        countDistinct("Customer_ID").alias("total_customers"),
        sum("Quantity_purchased").alias("total_quantity"),
        round(sum("Sales_amount"), 2).alias("total_revenue"),
        round(avg("Sales_amount"), 2).alias("avg_order_value")
    ) \
    .withColumn("refreshed_at", current_timestamp())

print(f"Cities in result : {regional_agg.count():,}")
regional_agg.orderBy(desc("total_revenue")).limit(5).display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 — Write to Gold Table

# COMMAND ----------

regional_agg.write.format("delta") \
    .mode("overwrite") \
    .option("mergeSchema","true")\
    .saveAsTable(AGG_TABLE)

print(f"regional_sales_summary written — {spark.table(AGG_TABLE).count():,} city rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 — Dashboard Preview

# COMMAND ----------

summary = spark.table(AGG_TABLE)

# Top 10 cities by revenue
print("--- Top 10 Cities by Revenue ---")
summary.orderBy(desc("total_revenue")).limit(10) \
    .select("state", "city", "total_orders", "total_customers",
            "total_quantity", "total_revenue", "avg_order_value") \
    .display()

# COMMAND ----------

# Top 10 states by revenue
print("--- Top 10 States by Revenue ---")
summary.groupBy("state") \
    .agg(
        sum("total_orders").alias("state_orders"),
        sum("total_customers").alias("state_customers"),
        round(sum("total_revenue"), 2).alias("state_revenue"),
        round(sum("total_revenue") / sum("total_orders"), 2).alias("state_avg_order_value")
    ) \
    .orderBy(desc("state_revenue")) \
    .limit(10) \
    .display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Incremental Refresh
# MAGIC When new orders land in `fact_sales`, re-run Steps 1→3. The `overwrite`
# MAGIC mode replaces the table with the latest aggregated totals.
# MAGIC
# MAGIC For very large fact tables where a full re-scan becomes expensive,
# MAGIC upgrade to the accumulate MERGE pattern:
# MAGIC ```sql
# MAGIC WHEN MATCHED THEN UPDATE SET
# MAGIC     total_orders  = target.total_orders  + source.new_orders,
# MAGIC     total_revenue = target.total_revenue + source.new_revenue
# MAGIC WHEN NOT MATCHED THEN INSERT *
# MAGIC ```
# MAGIC At GlobalMart's current scale, overwrite is simpler and correct.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Reset (if needed)

# COMMAND ----------

# spark.sql(f"DROP TABLE IF EXISTS {AGG_TABLE}")
# print("Table dropped")