# Databricks notebook source
# MAGIC %md
# MAGIC # Silver Layer — Shipments Data Cleaning & Quality Checks
# MAGIC **GlobalMart Assessment 1 | Tredence DE Advanced**
# MAGIC
# MAGIC | | |
# MAGIC |---|---|
# MAGIC | **Source** | `gbmart.bronze_as.shipments` (Postgres via Lakeflow Connect) |
# MAGIC | **Target** | `gbmart.silver_as.shipments` + `gbmart.silver_as.shipments_quarantine` |
# MAGIC | **SCD Type** | SCD1 — transactional record, updated in place |
# MAGIC
# MAGIC ### What this notebook does
# MAGIC | Step | Action |
# MAGIC |---|---|
# MAGIC | 1 | Setup |
# MAGIC | 2 | Read Bronze + inspect (note: Lakeflow lowercases all column names) |
# MAGIC | 3 | Rename lowercased columns to snake_case |
# MAGIC | 4 | Investigate: ActualArrival before DispatchDate |
# MAGIC | 5 | Investigate: Orphaned CarrierID |
# MAGIC | 6 | Investigate: ShippingCostINR mismatch vs tier rate |
# MAGIC | 7 | Investigate: NULL WeightKg |
# MAGIC | 8 | DQ scan summary |
# MAGIC | 9 | Quarantine invalid rows + write clean to Silver |
# MAGIC | 10 | Verify |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Setup

# COMMAND ----------

from pyspark.sql.functions import *
from pyspark.sql.types import *

CATALOG             = "gbmart"
BRONZE_TABLE        = "gbmart.bronze_as.shipments"
SILVER_TABLE        = "gbmart.silver_as.shipments"
QUARANTINE_TABLE    = "gbmart.silver_as.shipments_quarantine"

print(f"Reading from : {BRONZE_TABLE}")
print(f"Writing to   : {SILVER_TABLE}")
print(f"Quarantine   : {QUARANTINE_TABLE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 — Read Bronze + Inspect
# MAGIC
# MAGIC Lakeflow Connect lowercases all column names during ingestion.
# MAGIC `ShipmentID` → `shipmentid`, `OrderID` → `orderid`, etc.
# MAGIC The first task is to rename these to readable snake_case before any DQ work.

# COMMAND ----------

bronze_df = spark.table(BRONZE_TABLE)
print(f"Total records: {bronze_df.count()}")
bronze_df.printSchema()

# COMMAND ----------

bronze_df.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 — Rename Lowercased Columns to snake_case

# COMMAND ----------

renamed_df = bronze_df \
    .withColumnRenamed("shipmentid",     "shipment_id") \
    .withColumnRenamed("orderid",        "order_id") \
    .withColumnRenamed("carrierid",      "carrier_id") \
    .withColumnRenamed("supplierid",     "supplier_id") \
    .withColumnRenamed("shippingtierid", "shipping_tier_id") \
    .withColumnRenamed("shipmentstatus", "shipment_status") \
    .withColumnRenamed("warehousecity",  "warehouse_city") \
    .withColumnRenamed("trackingnumber", "tracking_number") \
    .withColumnRenamed("dispatchdate",   "dispatch_date") \
    .withColumnRenamed("expectedarrival","expected_arrival") \
    .withColumnRenamed("actualarrival",  "actual_arrival") \
    .withColumnRenamed("weightkg",       "weight_kg") \
    .withColumnRenamed("shippingcostinr","shipping_cost_inr")

print("Columns after rename:")
renamed_df.printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 — Investigate: ActualArrival Before DispatchDate
# MAGIC
# MAGIC Delivery performance SLA reports compute `delivery_delay_days = actual_arrival - expected_arrival`.
# MAGIC If `actual_arrival < dispatch_date`, the delay calculation produces a negative number —
# MAGIC meaning the parcel arrived before it was even dispatched. This is physically impossible and
# MAGIC indicates a data entry error at the source.
# MAGIC
# MAGIC Unlike the `orders` timezone case (where all gaps were exactly 1 day and traceable to UTC/IST),
# MAGIC these gaps are 1–3 days with no consistent pattern — not a timezone artifact.

# COMMAND ----------

invalid_arrival = renamed_df.filter(
    col("actual_arrival").isNotNull() &
    (col("actual_arrival") < col("dispatch_date"))
)

print(f"Rows where ActualArrival < DispatchDate: {invalid_arrival.count()}")
invalid_arrival.select(
    "shipment_id", "dispatch_date", "expected_arrival", "actual_arrival", "shipment_status"
).display()

# COMMAND ----------

# Confirm the gaps are NOT a consistent 1-day timezone offset
invalid_arrival.withColumn(
    "_gap_days", datediff(col("dispatch_date"), col("actual_arrival"))
).select("shipment_id", "_gap_days").display()

# COMMAND ----------

# MAGIC %md
# MAGIC **Finding:** 5 rows affected. Gaps are 1, 2, and 3 days — no consistent pattern.
# MAGIC This rules out a timezone artifact (which would always be exactly 1 day).
# MAGIC
# MAGIC **Decision:** Quarantine these 5 rows. Delivery SLA metrics would be corrupted if included.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5 — Investigate: Orphaned CarrierID
# MAGIC
# MAGIC `carrier_id` in shipments must reference a valid carrier in `silver_as.carriers`.
# MAGIC An orphaned ID means carrier performance metrics (on-time %, delivery delay by carrier)
# MAGIC cannot be computed for those shipments.

# COMMAND ----------

valid_carriers = spark.table("gbmart.silver_as.carriers").select("carrier_id")

orphaned = renamed_df.join(valid_carriers, on="carrier_id", how="left_anti")
print(f"Shipments with orphaned carrier_id: {orphaned.count()}")
orphaned.select("shipment_id", "carrier_id", "shipment_status").display()

# COMMAND ----------

# MAGIC %md
# MAGIC **Finding:** 3 rows reference `CAR-99` which does not exist in `silver_as.carriers`.
# MAGIC
# MAGIC **Decision:** Flag these rows with `_data_note = 'ORPHANED_CARRIER_ID'` — keep in Silver
# MAGIC but exclude from carrier performance aggregations in Gold.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6 — Investigate: ShippingCostINR Mismatch vs Tier Rate
# MAGIC
# MAGIC `shipping_cost_inr` should match the `cost_inr` defined in `silver_as.shipping_tier` for the
# MAGIC corresponding `shipping_tier_id`. A mismatch means the billing team is charging customers
# MAGIC a different amount than the contracted tier rate — a reconciliation failure.

# COMMAND ----------

tier_costs = spark.table("gbmart.silver_as.shipping_tier") \
    .select(col("shipping_tier_id"), col("cost_inr").alias("expected_cost"))

cost_check = renamed_df.join(tier_costs, on="shipping_tier_id", how="left") \
    .withColumn("_cost_mismatch",
        (col("shipping_cost_inr") != col("expected_cost")) &
        col("shipping_cost_inr").isNotNull() &
        col("expected_cost").isNotNull()
    )

mismatches = cost_check.filter(col("_cost_mismatch") == True)
print(f"Rows with cost mismatch: {mismatches.count()}")
mismatches.select(
    "shipment_id", "shipping_tier_id", "shipping_cost_inr", "expected_cost"
).display()

# COMMAND ----------

# MAGIC %md
# MAGIC **Finding:** 3 rows have a shipping cost that does not match the contracted tier rate.
# MAGIC
# MAGIC **Decision:** Flag with `_data_note = 'COST_MISMATCH'` — keep in Silver, flag for
# MAGIC billing reconciliation team.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 7 — Investigate: NULL WeightKg
# MAGIC
# MAGIC `weight_kg` is used to validate carrier eligibility (some carriers have weight limits).
# MAGIC Before flagging nulls as missing data, check whether they follow a business pattern.

# COMMAND ----------

renamed_df.filter(col("weight_kg").isNull()) \
    .select("shipment_id", "shipping_tier_id", "shipment_status", "weight_kg").display()

# COMMAND ----------

# MAGIC %md
# MAGIC **Finding:** Both NULL weight rows use `SHP-004` (In-store Pickup) — no physical parcel
# MAGIC is moved so weight is not applicable.
# MAGIC
# MAGIC **Decision:** NULL `weight_kg` for In-store Pickup is a valid business rule, not a data error. Keep as-is.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 8 — DQ Scan Summary

# COMMAND ----------

tier_costs_ref = spark.table("gbmart.silver_as.shipping_tier") \
    .select(col("shipping_tier_id"), col("cost_inr").alias("expected_cost"))
valid_carriers_ref = spark.table("gbmart.silver_as.carriers").select("carrier_id")

dq_df = renamed_df \
    .join(tier_costs_ref, on="shipping_tier_id", how="left") \
    .join(valid_carriers_ref.withColumnRenamed("carrier_id", "_valid_carrier"),
          renamed_df.carrier_id == col("_valid_carrier"), how="left") \
    .withColumn("_dq_flag",
        when(
            col("actual_arrival").isNotNull() &
            (col("actual_arrival") < col("dispatch_date")), "ARRIVAL_BEFORE_DISPATCH"
        )
        .when(col("_valid_carrier").isNull(), "ORPHANED_CARRIER_ID")
        .when(
            (col("shipping_cost_inr") != col("expected_cost")) &
            col("shipping_cost_inr").isNotNull(), "COST_MISMATCH"
        )
        .otherwise(None)
    )

print("DQ Summary:")
dq_df.groupBy("_dq_flag").count().display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 9 — Quarantine + Write Clean to Silver

# COMMAND ----------

# Quarantine: rows where arrival before dispatch (unrecoverable)
quarantine_df = dq_df.filter(col("_dq_flag") == "ARRIVAL_BEFORE_DISPATCH") \
    .select(*[c for c in renamed_df.columns], "_dq_flag") \
    .withColumn("_quarantine_reason", col("_dq_flag")) \
    .withColumn("_quarantined_at", current_timestamp())

quarantine_df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(QUARANTINE_TABLE)

print(f"Quarantined: {spark.table(QUARANTINE_TABLE).count()} rows → {QUARANTINE_TABLE}")

# COMMAND ----------

# Clean dataset: exclude quarantine, add _data_note flags for other issues
clean_df = dq_df.filter(
    col("_dq_flag").isNull() | col("_dq_flag").isin("ORPHANED_CARRIER_ID", "COST_MISMATCH")
) \
    .withColumn("_data_note", col("_dq_flag")) \
    .withColumn("_silver_updated_at", current_timestamp()) \
    .select(
        "shipment_id", "order_id", "carrier_id", "supplier_id", "shipping_tier_id",
        "shipment_status", "warehouse_city", "tracking_number",
        "dispatch_date", "expected_arrival", "actual_arrival",
        "weight_kg", "shipping_cost_inr",
        "_data_note", "_silver_updated_at"
    )

clean_df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(SILVER_TABLE)

print(f"Written {spark.table(SILVER_TABLE).count()} rows to {SILVER_TABLE}")

# COMMAND ----------

spark.sql(f"ALTER TABLE {SILVER_TABLE} ADD CONSTRAINT pk_shipment_id NOT NULL (shipment_id)")
spark.sql(f"ALTER TABLE {SILVER_TABLE} ADD CONSTRAINT fk_order_id NOT NULL (order_id)")
print("Constraints added.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 10 — Verify

# COMMAND ----------

df = spark.table(SILVER_TABLE)
q_df = spark.table(QUARANTINE_TABLE)

print(f"silver_as.shipments            : {df.count()} rows")
print(f"silver_as.shipments_quarantine : {q_df.count()} rows")
print(f"Total                          : {df.count() + q_df.count()} (should be 120)")

# COMMAND ----------

# Confirm no arrival-before-dispatch in clean Silver
df.filter(
    col("actual_arrival").isNotNull() &
    (col("actual_arrival") < col("dispatch_date"))
).count()

# COMMAND ----------

# Show flagged rows still in Silver
df.filter(col("_data_note").isNotNull()) \
    .select("shipment_id", "carrier_id", "shipping_cost_inr", "_data_note").display()

# COMMAND ----------

df.display()