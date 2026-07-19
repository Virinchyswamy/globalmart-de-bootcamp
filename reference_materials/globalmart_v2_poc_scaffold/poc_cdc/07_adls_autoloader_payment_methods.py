# Databricks notebook
# Step 7: Autoloader reads payment_methods_010626.csv from ADLS -> bronze.payment_methods
#
# This is the OTHER ingestion pattern -- no replication slot, no CDC. A new file lands
# in the landing folder and Autoloader picks it up as a new batch (incremental by file).

from pyspark.sql.functions import current_timestamp, lit, input_file_name

landing_path = "abfss://landing@<STORAGE_ACCOUNT>.dfs.core.windows.net/adls_landing/"
checkpoint_path = "abfss://landing@<STORAGE_ACCOUNT>.dfs.core.windows.net/_checkpoints/payment_methods/"

# Upload payment_methods_010626.csv to <landing_path> before running this cell.

df = (
    spark.readStream.format("cloudFiles")
    .option("cloudFiles.format", "csv")
    .option("cloudFiles.schemaLocation", checkpoint_path + "schema")
    .option("header", "true")
    .load(landing_path + "payment_methods_*.csv")
)

bronze_df = (
    df
    .withColumn("ingestion_timestamp", current_timestamp())
    .withColumn("source_system", lit("adls_autoloader"))
    .withColumn("source_file", input_file_name())
)

spark.sql("CREATE SCHEMA IF NOT EXISTS bronze")

(
    bronze_df.writeStream
    .format("delta")
    .option("checkpointLocation", checkpoint_path)
    .trigger(availableNow=True)
    .toTable("bronze.payment_methods")
)

# Wait for the trigger(availableNow=True) stream to finish, then check results
print("bronze.payment_methods row count:", spark.table("bronze.payment_methods").count())
display(spark.table("bronze.payment_methods"))
