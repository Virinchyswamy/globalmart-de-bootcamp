# Databricks notebook source
# MAGIC %md
# MAGIC # Gold Layer — Fact Table & Pre-Aggregated Facts
# MAGIC **GlobalMart Assessment 1 | Tredence DE Advanced**
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## What this notebook builds
# MAGIC
# MAGIC | Table | Type | Business Question |
# MAGIC |---|---|---|
# MAGIC | `fact_shipments` | Fact | What happened in each shipment? |
# MAGIC | `agg_carrier_performance` | Pre-aggregated | Which carrier delivers fastest and cheapest? |
# MAGIC | `agg_tier_analysis` | Pre-aggregated | How does each delivery tier perform in practice? |
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## fact_shipments — Grain
# MAGIC
# MAGIC > **One row = one shipment**
# MAGIC
# MAGIC Each row records a single shipment event with:
# MAGIC - **Foreign keys** linking to all 3 dimensions
# MAGIC - **Measures** that can be summed or averaged: `shipping_cost_inr`, `weight_kg`, `delivery_delay_days`
# MAGIC - **Derived flags**: `is_on_time` — computed from actual vs expected arrival
# MAGIC
# MAGIC ```
# MAGIC fact_shipments
# MAGIC ├── shipment_key (surrogate PK)
# MAGIC ├── shipment_id (natural key)
# MAGIC ├── order_id
# MAGIC ├── supplier_key      → dim_supplier
# MAGIC ├── carrier_key       → dim_carrier       (NULL if carrier unresolvable)
# MAGIC ├── shipping_tier_key → dim_shipping_tier
# MAGIC ├── shipment_status
# MAGIC ├── warehouse_city
# MAGIC ├── dispatch_date
# MAGIC ├── expected_arrival
# MAGIC ├── actual_arrival
# MAGIC ├── weight_kg
# MAGIC ├── shipping_cost_inr  (measure)
# MAGIC ├── delivery_delay_days (measure — actual minus expected, in days)
# MAGIC └── is_on_time         (flag — True if actual_arrival <= expected_arrival)
# MAGIC ```
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Setup

# COMMAND ----------

from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window

CATALOG = "gbmart"

# Sources
SILVER_SHIPMENTS  = "gbmart.silver_as.shipments"
DIM_SUPPLIER      = "gbmart.gold_as.dim_supplier"
DIM_CARRIER       = "gbmart.gold_as.dim_carrier"
DIM_SHIPPING_TIER = "gbmart.gold_as.dim_shipping_tier"

# Targets
FACT_SHIPMENTS         = "gbmart.gold_as.fact_shipments"
AGG_CARRIER_PERF       = "gbmart.gold_as.agg_carrier_performance"
AGG_TIER_ANALYSIS      = "gbmart.gold_as.agg_tier_analysis"

print("Setup complete.")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Step 2 — Read Silver Shipments + Dimensions
# MAGIC

# COMMAND ----------

shipments_df   = spark.table(SILVER_SHIPMENTS)
dim_supplier   = spark.table(DIM_SUPPLIER)
dim_carrier    = spark.table(DIM_CARRIER)
dim_tier       = spark.table(DIM_SHIPPING_TIER)

print(f"silver_as.shipments : {shipments_df.count()} rows")
print(f"dim_supplier        : {dim_supplier.count()} rows")
print(f"dim_carrier         : {dim_carrier.count()} rows")
print(f"dim_shipping_tier   : {dim_tier.count()} rows")

# COMMAND ----------

shipments_df.printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Step 3 — Resolve Surrogate Keys
# MAGIC
# MAGIC Join each shipment to its dimension to retrieve the surrogate key.
# MAGIC
# MAGIC **Join strategy:**
# MAGIC - `supplier_id` → `dim_supplier` : INNER JOIN — all shipments have a valid supplier
# MAGIC - `carrier_id` → `dim_carrier` : **LEFT JOIN** — 3 shipments reference `CAR-99` (flagged in Silver);
# MAGIC   these will get `carrier_key = NULL` in the fact table rather than being dropped
# MAGIC - `shipping_tier_id` → `dim_shipping_tier` : INNER JOIN — all shipments have a valid tier
# MAGIC

# COMMAND ----------

# Select only key columns from dims to avoid column name collisions
sup_keys  = dim_supplier.select("supplier_id",      "supplier_key")
car_keys  = dim_carrier.select("carrier_id",         "carrier_key")
tier_keys = dim_tier.select("shipping_tier_id",      "shipping_tier_key")

fact_df = shipments_df     .join(sup_keys,  on="supplier_id",      how="inner")     .join(car_keys,  on="carrier_id",       how="left")     .join(tier_keys, on="shipping_tier_id", how="inner")

print(f"Rows after joins: {fact_df.count()}  (should be {shipments_df.count()})")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Step 4 — Add Derived Measures
# MAGIC
# MAGIC ### `delivery_delay_days`
# MAGIC Number of days between expected and actual arrival.
# MAGIC - **Positive** → shipment arrived late
# MAGIC - **0** → on time
# MAGIC - **Negative** → arrived early
# MAGIC - **NULL** → shipment not yet delivered (`actual_arrival` is NULL)
# MAGIC
# MAGIC ### `is_on_time`
# MAGIC Boolean flag: True if `actual_arrival <= expected_arrival`
# MAGIC Used in aggregations to compute on-time delivery percentage per carrier.
# MAGIC

# COMMAND ----------

fact_shipments = fact_df     .withColumn("delivery_delay_days",
        when(col("actual_arrival").isNull(), None)
        .otherwise(datediff(col("actual_arrival"), col("expected_arrival")))
    )     .withColumn("is_on_time",
        when(col("actual_arrival").isNull(), None)
        .when(col("actual_arrival") <= col("expected_arrival"), lit(True))
        .otherwise(lit(False))
    )     .withColumn("shipment_key", monotonically_increasing_id())     .select(
        "shipment_key",
        "shipment_id",
        "order_id",
        "supplier_key",
        "carrier_key",
        "shipping_tier_key",
        "shipment_status",
        "warehouse_city",
        "dispatch_date",
        "expected_arrival",
        "actual_arrival",
        "weight_kg",
        "shipping_cost_inr",
        "delivery_delay_days",
        "is_on_time",
        "_data_note",
        current_timestamp().alias("_gold_updated_at")
    )

fact_shipments.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Step 5 — Write fact_shipments to Gold
# MAGIC

# COMMAND ----------

fact_shipments.write     .format("delta")     .mode("overwrite")     .option("overwriteSchema", "true")     .saveAsTable(FACT_SHIPMENTS)

print(f"Written {spark.table(FACT_SHIPMENTS).count()} rows to {FACT_SHIPMENTS}")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Step 6 — Validate Fact Integrity
# MAGIC

# COMMAND ----------

fact = spark.table(FACT_SHIPMENTS)

# NULL foreign keys signal unresolvable references
null_supplier = fact.filter(col("supplier_key").isNull()).count()
null_carrier  = fact.filter(col("carrier_key").isNull()).count()
null_tier     = fact.filter(col("shipping_tier_key").isNull()).count()

print(f"NULL supplier_key      : {null_supplier}  (expected 0)")
print(f"NULL carrier_key       : {null_carrier}   (expected 3 — CAR-99 orphans from Silver)")
print(f"NULL shipping_tier_key : {null_tier}  (expected 0)")

# COMMAND ----------

# Delivery delay distribution
print("Delivery delay breakdown:")
fact.filter(col("shipment_status") == "Delivered")     .withColumn("_delay_band",
        when(col("delivery_delay_days") < 0,  "Early")
        .when(col("delivery_delay_days") == 0, "On Time")
        .when(col("delivery_delay_days") <= 2, "Slightly Late (1-2d)")
        .otherwise("Late (3d+)")
    )     .groupBy("_delay_band").count().orderBy("_delay_band").display()

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Step 7 — Pre-Aggregated Fact: `agg_carrier_performance`
# MAGIC
# MAGIC **Business question:** Which carrier delivers most reliably and at what cost?
# MAGIC
# MAGIC This table is pre-computed from `fact_shipments` so dashboards don't need to run
# MAGIC expensive GROUP BY queries over the full fact table every time.
# MAGIC
# MAGIC **Scope:** Delivered shipments only — in-transit and dispatched rows have NULL `actual_arrival`
# MAGIC and cannot contribute to delay or on-time metrics.
# MAGIC

# COMMAND ----------

agg_carrier = spark.table(FACT_SHIPMENTS)     .join(dim_carrier.select("carrier_key", "carrier_id", "carrier_name", "carrier_type", "service_region"),
          on="carrier_key", how="left")     .filter(col("shipment_status") == "Delivered")     .groupBy("carrier_key", "carrier_id", "carrier_name", "carrier_type", "service_region")     .agg(
        count("shipment_id")                              .alias("total_shipments"),
        round(avg("delivery_delay_days"), 2)              .alias("avg_delay_days"),
        round(avg("shipping_cost_inr"), 2)                .alias("avg_cost_inr"),
        round(
            sum(when(col("is_on_time") == True, 1).otherwise(0)) /
            count("shipment_id") * 100, 1
        )                                                 .alias("on_time_pct"),
        round(avg("weight_kg"), 2)                        .alias("avg_weight_kg")
    )     .orderBy(desc("on_time_pct"))

agg_carrier.display()

# COMMAND ----------

agg_carrier.write     .format("delta")     .mode("overwrite")     .option("overwriteSchema", "true")     .saveAsTable(AGG_CARRIER_PERF)

print(f"Written {spark.table(AGG_CARRIER_PERF).count()} rows to {AGG_CARRIER_PERF}")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Step 8 — Pre-Aggregated Fact: `agg_tier_analysis`
# MAGIC
# MAGIC **Business question:** Is the cost of each shipping tier justified by actual delivery performance?
# MAGIC
# MAGIC Compares the **contracted tier cost** (`tier_cost_inr`) against the **actual average cost charged**
# MAGIC (`avg_actual_cost_inr`) to surface billing discrepancies at the tier level.
# MAGIC Also shows whether faster tiers genuinely reduce delay.
# MAGIC
# MAGIC **Scope:** All shipments (not just Delivered) — we want total usage by tier regardless of status.
# MAGIC

# COMMAND ----------

agg_tier = spark.table(FACT_SHIPMENTS)     .join(dim_tier.select("shipping_tier_key", "shipping_tier_id", "tier_name",
                          "tier_cost_inr", "max_delivery_days", "is_available_online"),
          on="shipping_tier_key", how="left")     .groupBy("shipping_tier_key", "shipping_tier_id", "tier_name",
             "tier_cost_inr", "max_delivery_days", "is_available_online")     .agg(
        count("shipment_id")                              .alias("total_shipments"),
        round(avg("shipping_cost_inr"), 2)                .alias("avg_actual_cost_inr"),
        round(avg(
            when(col("shipment_status") == "Delivered", col("delivery_delay_days"))
        ), 2)                                             .alias("avg_delay_days_delivered"),
        round(
            sum(when(col("is_on_time") == True, 1).otherwise(0)) /
            count(when(col("shipment_status") == "Delivered", 1)) * 100, 1
        )                                                 .alias("on_time_pct_delivered")
    )     .orderBy("tier_cost_inr")

agg_tier.display()

# COMMAND ----------

agg_tier.write     .format("delta")     .mode("overwrite")     .option("overwriteSchema", "true")     .saveAsTable(AGG_TIER_ANALYSIS)

print(f"Written {spark.table(AGG_TIER_ANALYSIS).count()} rows to {AGG_TIER_ANALYSIS}")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Final Summary — Gold Layer Complete
# MAGIC
# MAGIC | Table | Type | Rows | Business Purpose |
# MAGIC |---|---|---|---|
# MAGIC | `dim_supplier` | Dimension | 10 | Supplier lookup for shipment context |
# MAGIC | `dim_carrier` | Dimension | 10 | Carrier lookup for delivery performance |
# MAGIC | `dim_shipping_tier` | Dimension | 5 | Tier lookup for cost & SLA analysis |
# MAGIC | `fact_shipments` | Fact | 115 | One row per shipment — all measurable events |
# MAGIC | `agg_carrier_performance` | Pre-agg | 10 | Carrier-level delivery KPIs |
# MAGIC | `agg_tier_analysis` | Pre-agg | 5 | Tier-level cost vs performance comparison |
# MAGIC
# MAGIC > `fact_shipments` = 115 rows because 5 rows were quarantined in Silver
# MAGIC > (ActualArrival < DispatchDate — physically impossible, cannot be used for SLA analysis)
# MAGIC

# COMMAND ----------

tables = [
    ("dim_supplier",          "gbmart.gold_as.dim_supplier"),
    ("dim_carrier",           "gbmart.gold_as.dim_carrier"),
    ("dim_shipping_tier",     "gbmart.gold_as.dim_shipping_tier"),
    ("fact_shipments",        "gbmart.gold_as.fact_shipments"),
    ("agg_carrier_performance","gbmart.gold_as.agg_carrier_performance"),
    ("agg_tier_analysis",     "gbmart.gold_as.agg_tier_analysis"),
]

print(f"{'Table':<30} {'Rows':>6}")
print("-" * 38)
for name, table in tables:
    count = spark.table(table).count()
    print(f"{name:<30} {count:>6}")