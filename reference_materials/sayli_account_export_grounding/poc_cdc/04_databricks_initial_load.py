# Databricks notebook source
# MAGIC %md
# MAGIC # Step 4 — Initial Load (Day 1)
# MAGIC
# MAGIC JDBC read of `public.poc_orders` (200 rows) from Supabase -> full snapshot into `bronze.poc_orders`.

# COMMAND ----------

from pyspark.sql.functions import current_timestamp, lit

jdbc_url = "jdbc:postgresql://aws-0-ap-south-1.pooler.supabase.com:5432/postgres?sslmode=require"

connection_props = {
    "user": "postgres.isqcnhvlfnjszllicxqi",
    "password": "A1qaZ@Vfr$2#3",
    "driver": "org.postgresql.Driver",
}

# COMMAND ----------

raw_orders_df = spark.read.jdbc(url=jdbc_url, table="public.poc_orders", properties=connection_props)

bronze_orders_df = (
    raw_orders_df
    .withColumn("ingestion_timestamp", current_timestamp())
    .withColumn("source_system", lit("supabase_jdbc"))
    .withColumn("batch_id", lit("day1_initial_load"))
)

# COMMAND ----------

raw_orders_df.display()

# COMMAND ----------

bronze_orders_df.display()

# COMMAND ----------

bronze_orders_df.write.format("delta").mode("overwrite").saveAsTable("shopsphere_retail.poc_bronze.poc_orders")

# COMMAND ----------

print("bronze.poc_orders row count:", spark.table("bronze.poc_orders").count())
display(spark.table("bronze.poc_orders"))