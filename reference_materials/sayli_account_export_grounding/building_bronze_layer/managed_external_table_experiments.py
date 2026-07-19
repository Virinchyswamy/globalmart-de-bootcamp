# Databricks notebook source
# MAGIC %sql
# MAGIC -- create schema gbmart.expschema;
# MAGIC -- drop table gbmart.expschema.customers_managed;
# MAGIC -- drop table gbmart.expschema.customers_external;

# COMMAND ----------

customers_df = spark.read \
    .option("header", "true") \
    .option("inferSchema","true")\
    .csv("abfss://ecom-external-data@ecomadlsdata.dfs.core.windows.net/raw-data/customers_010626.csv")

# COMMAND ----------

display(customers_df)

# COMMAND ----------

# MAGIC %md
# MAGIC #### Stored data as the managed table

# COMMAND ----------

customers_df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("gbmart.expschema.customers_managed")

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from gbmart.expschema.customers_managed;

# COMMAND ----------

# MAGIC %sql
# MAGIC describe history gbmart.expschema.customers_managed;

# COMMAND ----------

# MAGIC %md
# MAGIC #### Stored data as external table

# COMMAND ----------

customers_df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("path","abfss://ecom-external-data@ecomadlsdata.dfs.core.windows.net/customers_external")\
    .saveAsTable("gbmart.expschema.customers_external")

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from gbmart.expschema.customers_external;

# COMMAND ----------

# MAGIC %sql
# MAGIC describe history gbmart.expschema.customers_external;

# COMMAND ----------

# MAGIC %md
# MAGIC #### Drop managed table

# COMMAND ----------

# MAGIC %sql
# MAGIC drop table gbmart.expschema.customers_managed;

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from gbmart.expschema.customers_managed;

# COMMAND ----------

# MAGIC %sql
# MAGIC describe history gbmart.expschema.customers_managed;

# COMMAND ----------

# MAGIC %md
# MAGIC #### Drop external table

# COMMAND ----------

# MAGIC %sql
# MAGIC drop table gbmart.expschema.customers_external;

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from gbmart.expschema.customers_external;

# COMMAND ----------

# MAGIC %sql
# MAGIC describe history gbmart.expschema.customers_external;

# COMMAND ----------

display(
    dbutils.fs.ls(
        "abfss://ecom-external-data@ecomadlsdata.dfs.core.windows.net/customers_external"
    )
)