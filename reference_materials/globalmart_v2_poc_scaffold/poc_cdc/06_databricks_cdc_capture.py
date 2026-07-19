# Databricks notebook
# Step 6: Read the replication slot via JDBC -> see the 50 "Day 2" inserts as CDC events.
#
# pg_logical_slot_get_changes() is a regular SQL function, so Spark JDBC can call it
# like any other query. Each call DRAINS the slot up to the current WAL position --
# run it again afterwards and you'll get an empty result until the next change happens.

jdbc_url = "jdbc:postgresql://<SUPABASE_HOST>:5432/postgres?sslmode=require"

connection_props = {
    "user": "<SUPABASE_USER>",
    "password": dbutils.secrets.get(scope="poc-cdc", key="supabase-password"),
    "driver": "org.postgresql.Driver",
}

cdc_query = (
    "(SELECT * FROM pg_logical_slot_get_changes('poc_orders_slot', NULL, NULL)) AS cdc_changes"
)

cdc_raw_df = spark.read.jdbc(url=jdbc_url, table=cdc_query, properties=connection_props)

print("CDC events captured:", cdc_raw_df.count())
display(cdc_raw_df)

# Each row's `data` column looks like:
#   table public.orders: INSERT: order_id[character varying]:'OR-10009' customer_id[...]:'CUST-13976' ...
#
# For this POC, just confirm you see ~50 INSERT lines, one per Day-2 order.
# In a real pipeline you'd parse this text (or switch to the wal2json plugin for
# structured JSON output) and MERGE the parsed rows into bronze.orders.
