# Databricks notebook source
# MAGIC %md
# MAGIC # Mount ADLS Storage — Assessment Raw Data
# MAGIC **Storage Account:** `ecomadlsdata`  
# MAGIC **Container:** `assessment-raw-data`  
# MAGIC **Mount Point:** `/mnt/assessment-raw-data`

# COMMAND ----------

storage_account = "ecomadlsdata"
container       = "assessment-raw-data"
mount_point     = "/mnt/assessment-raw-data"

# Replace with your actual storage account key — do not commit real keys to git
storage_key = "YOUR_STORAGE_ACCOUNT_KEY_HERE"

dbutils.fs.mount(
    source       = f"wasbs://{container}@{storage_account}.blob.core.windows.net",
    mount_point  = mount_point,
    extra_configs = {
        f"fs.azure.account.key.{storage_account}.blob.core.windows.net": storage_key
    }
)

print(f"Mounted: {mount_point}")

# COMMAND ----------

# MAGIC %md
# MAGIC Verify the mount — you should see `suppliers/`, `shipping-tier/`, `carriers/` folders.

# COMMAND ----------

display(dbutils.fs.ls("/mnt/assessment-raw-data"))

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC If you need to **unmount** and remount (e.g. wrong key), run this first:

# COMMAND ----------

# Only run if you need to remount
# dbutils.fs.unmount("/mnt/assessment-raw-data")