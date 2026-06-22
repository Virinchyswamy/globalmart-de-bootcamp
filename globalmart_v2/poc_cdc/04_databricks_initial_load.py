# Databricks notebook
# Step 4: JDBC read of public.orders (200 rows) -> bronze.orders (full snapshot, "Day 1")

from pyspark.sql.functions import current_timestamp, lit

jdbc_url = "jdbc:postgresql://<SUPABASE_HOST>:5432/postgres?sslmode=require"

connection_props = {
    "user": "<SUPABASE_USER>",
    "password": dbutils.secrets.get(scope="poc-cdc", key="supabase-password"),
    "driver": "org.postgresql.Driver",
}

raw_orders_df = spark.read.jdbc(url=jdbc_url, table="public.orders", properties=connection_props)

bronze_orders_df = (
    raw_orders_df
    .withColumn("ingestion_timestamp", current_timestamp())
    .withColumn("source_system", lit("supabase_jdbc"))
    .withColumn("batch_id", lit("day1_initial_load"))
)

spark.sql("CREATE SCHEMA IF NOT EXISTS bronze")
bronze_orders_df.write.format("delta").mode("overwrite").saveAsTable("bronze.orders")

print("bronze.orders row count:", spark.table("bronze.orders").count())
display(spark.table("bronze.orders"))
