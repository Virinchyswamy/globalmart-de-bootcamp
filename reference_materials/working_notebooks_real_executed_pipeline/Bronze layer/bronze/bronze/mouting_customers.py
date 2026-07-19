# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze Layer — Customers Ingestion via Autoloader (Mounting Version)
# MAGIC **GlobalMart | Tredence DE Advanced Training**
# MAGIC
# MAGIC | | |
# MAGIC |---|---|
# MAGIC | **Source** | Blob Storage container, mounted via `dbutils.fs.mount()` → `raw-data/customers/` |
# MAGIC | **Mount source** | `wasbs://YOUR_CONTAINER@YOUR_STORAGE_ACCOUNT.blob.core.windows.net/` |
# MAGIC | **Target** | `YOUR_CATALOG.bronze.customers` (Managed Delta Table) |
# MAGIC | **Auth** | Storage account access key, set once at mount time — no Unity Catalog External Location involved |
# MAGIC | **Mode** | `trigger(availableNow=True)` — processes all new files, then stops |
# MAGIC
# MAGIC ### How this differs from the External-Location version of this same task
# MAGIC
# MAGIC | | External Location version | This (Mounting) version |
# MAGIC |---|---|---|
# MAGIC | Connection | Unity Catalog Storage Credential + External Location | `dbutils.fs.mount()` with a storage account key |
# MAGIC | Protocol | `abfss://` + `.dfs.core.windows.net` (requires ADLS Gen2 / Hierarchical Namespace) | `wasbs://` + `.blob.core.windows.net` |
# MAGIC | Catalog | `gbmart` (the shared course catalog) | Your own catalog — different from `gbmart` |
# MAGIC | Checkpoint/schema location | Shared root `_checkpoints/<table>/` and `_schemas/<table>/` folders | Nested **inside** each table's own source folder — `raw-data/customers/_checkpoints/` |
# MAGIC
# MAGIC > **Why `wasbs://` and not `abfss://` here:** `abfss://` only works for mounting/reading against a storage account with **Hierarchical Namespace (ADLS Gen2)** enabled. If your storage account doesn't have that enabled, or your workspace's mount setup doesn't support `abfss://` mounting, `wasbs://` against the `.blob.core.windows.net` endpoint is the working alternative — same underlying data, older Blob Storage protocol.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 0 — Mount the Container
# MAGIC
# MAGIC Unlike the External Location version, this notebook reaches storage the old way: a real storage account key, set once via `dbutils.fs.mount()`. Get your key first:
# MAGIC
# MAGIC ```
# MAGIC Azure Portal → Storage accounts → YOUR_STORAGE_ACCOUNT
# MAGIC   → Security + networking → Access keys
# MAGIC   → click "Show" next to key1 → Copy
# MAGIC ```
# MAGIC
# MAGIC Paste it into the cell below, run it, then replace it back with the placeholder before saving/sharing this notebook — never leave a real key in a notebook anyone else can open.

# COMMAND ----------

# Storage Details
STORAGE_ACCOUNT = "ecomdata"
CONTAINER = "raw-demo-data"
MOUNT_POINT = "/mnt/virinchy_gbmart_data"

STORAGE_ACCOUNT_KEY = "YOUR_STORAGE_ACCOUNT_KEY"  # paste your own key here, never commit a real one (see Step 0 above)

configs = {
    f"fs.azure.account.key.{STORAGE_ACCOUNT}.blob.core.windows.net": STORAGE_ACCOUNT_KEY
}

# Check if already mounted
if any(m.mountPoint == MOUNT_POINT for m in dbutils.fs.mounts()):
    print(f"✅ {MOUNT_POINT} is already mounted.")
else:
    dbutils.fs.mount(
        source=f"wasbs://{CONTAINER}@{STORAGE_ACCOUNT}.blob.core.windows.net/",
        mount_point=MOUNT_POINT,
        extra_configs=configs
    )
    print(f"✅ Successfully mounted at {MOUNT_POINT}")

# COMMAND ----------

# ─── Verify the mount worked ───────────────────────────────────────────────────
print(f"Contents of {MOUNT_POINT} :")
for f in dbutils.fs.ls(MOUNT_POINT):
    print(f"  {f.name}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Configuration
# MAGIC
# MAGIC **The important change from the External Location version:** checkpoint and schema paths are **not** in a shared root `_checkpoints/` / `_schemas/` folder with one subfolder per table. They live **inside each table's own source folder** instead — `raw-data/customers/_checkpoints/`, not `raw-data/_checkpoints/customers/`.
# MAGIC
# MAGIC ```
# MAGIC OLD (shared root folders):                 NEW (nested inside each table's own folder):
# MAGIC raw-data/                                  raw-data/
# MAGIC   _checkpoints/                              customers/
# MAGIC     customers/          ← shared root          customers_010626.csv
# MAGIC     orders/                                    _checkpoints/     ← nested here
# MAGIC   _schemas/                                    _schemas/         ← nested here
# MAGIC     customers/                               orders/
# MAGIC     orders/                                    ...
# MAGIC ```
# MAGIC
# MAGIC > **One thing worth knowing before you commit to this layout:** having Autoloader's own checkpoint/schema state sit inside the exact folder it's scanning for source files is a slightly unusual pattern — most Databricks reference architectures keep those state folders completely separate from the data folder to avoid any chance of the listing operation touching its own metadata. In practice this works because `cloudFiles.format="csv"` only picks up files that look like CSVs, so the JSON/state files Autoloader writes under `_checkpoints/`/`_schemas/` won't get ingested as data — but it's worth being aware this is a deliberate, non-default choice.

# COMMAND ----------

from pyspark.sql.functions import input_file_name, current_timestamp

# Mounted base path — set once, reuse everywhere
MOUNT_BASE = f"{MOUNT_POINT}"

SOURCE_FOLDER = "customers"

CATALOG = "harsh_kumar01_npmentorskool_onmicrosoft_com"   # ← different catalog than gbmart
SCHEMA = "bronze"
TABLE = "customers"
TARGET_TABLE = f"{CATALOG}.{SCHEMA}.{TABLE}"

# Source data path
SOURCE_PATH = f"{MOUNT_BASE}/{SOURCE_FOLDER}/"

# Auto Loader metadata paths
# Each table gets its own checkpoint and schema subfolder.
CHECKPOINT_PATH = f"{MOUNT_BASE}/_checkpoints/{SOURCE_FOLDER}/"
SCHEMA_PATH = f"{MOUNT_BASE}/_schemas/{SOURCE_FOLDER}/"

print(f"Source      : {SOURCE_PATH}")
print(f"Target table: {TARGET_TABLE}")
print(f"Checkpoint  : {CHECKPOINT_PATH}")
print(f"Schema      : {SCHEMA_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 — Verify Files in the Mounted Source Folder

# COMMAND ----------

files = dbutils.fs.ls(SOURCE_PATH)
print(f"Files found in {SOURCE_FOLDER}/:\n")
for f in files:
    print(f"  {f.name}  ({f.size / 1024:.1f} KB)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 — Create Catalog & Schema (if not exists)

# COMMAND ----------

spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
print(f"Catalog '{CATALOG}' and schema '{SCHEMA}' are ready.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 — Autoloader Ingestion
# MAGIC
# MAGIC | Option | Value | Why |
# MAGIC |---|---|---|
# MAGIC | `cloudFiles.format` | `csv` | source file format |
# MAGIC | `cloudFiles.schemaLocation` | `SCHEMA_PATH` (nested under `customers/_schemas/`) | saves inferred schema — reused on next run |
# MAGIC | `cloudFiles.inferColumnTypes` | `true` | infers proper types instead of all string |
# MAGIC | `cloudFiles.schemaEvolutionMode` | `addNewColumns` | new columns in future files are added automatically |
# MAGIC | `mergeSchema` | `true` | Delta write-side schema merge — resolves schema mismatch on first encounter |
# MAGIC | `trigger(availableNow)` | — | batch-style: process all new files then stop |

# COMMAND ----------

from pyspark.sql.functions import *

# COMMAND ----------

customers_df = spark.readStream\
        .format("cloudFiles")\
        .option("cloudFiles.format",              "csv")\
        .option("cloudFiles.schemaLocation",      SCHEMA_PATH)\
        .option("cloudFiles.inferColumnTypes",    "true")\
        .option("cloudFiles.schemaEvolutionMode", "addNewColumns")\
        .option("header",                         "true")\
        .load(SOURCE_PATH)\
        .withColumn("_source_file", col("_metadata.file_path"))\
        .withColumn("_ingested_at", current_timestamp())

# COMMAND ----------

customers_df.display()

# COMMAND ----------

customers_df.writeStream\
        .format("delta")\
        .outputMode("append")\
        .option("checkpointLocation", CHECKPOINT_PATH)\
        .option("mergeSchema",        "true")\
        .trigger(availableNow=True)\
        .toTable(TARGET_TABLE)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5 — Verify Data in Bronze Table

# COMMAND ----------

df = spark.table(TARGET_TABLE)
print(f"Total rows : {df.count()}")
print(f"Columns    : {df.columns}")
df.display(5, truncate=False)

# COMMAND ----------

# Row count per source file
df.groupBy("_source_file").count().orderBy("_source_file").display(truncate=False)