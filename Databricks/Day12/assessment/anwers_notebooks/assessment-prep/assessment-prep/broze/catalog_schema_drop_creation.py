# Databricks notebook source
# MAGIC %sql
# MAGIC create schema gbmart.bronze_as;

# COMMAND ----------

# MAGIC %sql
# MAGIC create schema gbmart.silver_as;

# COMMAND ----------

# MAGIC %sql
# MAGIC create schema gbmart.gold_as;

# COMMAND ----------

# MAGIC %sql
# MAGIC drop table gbmart.bronze_as.suppliers;