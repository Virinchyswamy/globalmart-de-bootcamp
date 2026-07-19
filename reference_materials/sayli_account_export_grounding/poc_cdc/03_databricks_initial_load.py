# Databricks notebook source
# MAGIC %md
# MAGIC # Step 3 — Initial Load (Day 1)
# MAGIC
# MAGIC JDBC read of `cdc_poc.products` (4 rows) from Supabase -> full snapshot into `bronze.cdc_poc_products`.
# MAGIC
# MAGIC This is the "baseline" load. After this runs, every future change to `cdc_poc.products` will show up as a CDC event instead of being part of a fresh snapshot.

# COMMAND ----------

from pyspark.sql.functions import current_timestamp, lit

jdbc_url = "jdbc:postgresql://aws-0-ap-south-1.pooler.supabase.com:5432/postgres?sslmode=require"

connection_props = {
    "user": "postgres.isqcnhvlfnjszllicxqi",
    "password": "A1qaZ@Vfr$2#3",
    "driver": "org.postgresql.Driver",
}

# COMMAND ----------

raw_products_df = spark.read.jdbc(url=jdbc_url, table="cdc_poc.products", properties=connection_props)


# COMMAND ----------

raw_products_df.display()

# COMMAND ----------

bronze_products_df = (
    raw_products_df
    .withColumn("ingestion_timestamp", current_timestamp())
    .withColumn("source_system", lit("supabase_jdbc"))
    .withColumn("batch_id", lit("day1_initial_load"))
)

# COMMAND ----------

bronze_products_df.display()

# COMMAND ----------

bronze_products_df.write.format("delta").mode("overwrite").saveAsTable("shopsphere_retail.poc_bronze.cdc_poc_products")


# COMMAND ----------

display(spark.table("shopsphere_retail.poc_bronze.cdc_poc_products"))


# COMMAND ----------

print("bronze.cdc_poc_products row count:", spark.table("shopsphere_retail.poc_bronze.cdc_poc_products").count())