# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze Layer — Remaining Sources via Auto Loader (Mounting Version)
# MAGIC **GlobalMart | Tredence DE Advanced Training**
# MAGIC
# MAGIC This notebook is the companion to the customers ingestion notebook. It ingests the **5 remaining source folders** into Bronze, using the exact same mount point, checkpoint/schema structure, Auto Loader options, and metadata columns as that reference notebook — just looped across multiple sources instead of hardcoded to one.
# MAGIC
# MAGIC | Source Folder | Target Bronze Table | Format |
# MAGIC |---|---|---|
# MAGIC | `addresses` | `bronze.addresses` | CSV |
# MAGIC | `products` | `bronze.products` | **JSON** *(corrected)* |
# MAGIC | `payment_methods` | `bronze.payment_methods` | CSV |
# MAGIC | `returns` | `bronze.returns` | CSV |
# MAGIC | `payments` | `bronze.payments` | CSV *(corrected)* |
# MAGIC
# MAGIC > **The real container's file formats turned out to be the opposite of the original spec.** Confirmed via two independent pieces of evidence: the Step 3 diagnostic showed `payments/` actually contains `payments_010626.csv` / `_020626.csv` / `_030626.csv` (CSV), and an Azure Portal screenshot of the `raw-demo-data` container confirmed `products/` contains `products_010626.json` (JSON, 394 KiB). `BRONZE_SOURCES` below reflects reality, not the original written mapping.
# MAGIC
# MAGIC | | |
# MAGIC |---|---|
# MAGIC | **Container** | `raw-demo-data` (storage account `ecomdata`) |
# MAGIC | **Mount** | Reused — **no new mount created here**. Assumes the customers notebook already mounted the container at `MOUNT_POINT` in this session/cluster. |
# MAGIC | **Auth** | Same storage account key used at mount time — nothing new to configure |
# MAGIC | **Mode** | `trigger(availableNow=True)` per table — processes all new files, then stops |
# MAGIC
# MAGIC > **This notebook does not call `dbutils.fs.mount()` at all.** If `MOUNT_POINT` isn't already mounted (e.g. this is a fresh cluster session), run the customers notebook's mount cell first, or Step 1 below will fail with a clear error telling you so.
# MAGIC
# MAGIC ### Known issues found via the Step 3 diagnostic — all resolved
# MAGIC
# MAGIC 1. ~~`products/` does not exist~~ — **Resolved.** The folder didn't have data at the time of the first diagnostic run; it's since been populated with `products_010626.json`. Format corrected to JSON above.
# MAGIC 2. ~~`addresses/` had a stale checkpoint~~ — **Resolved, automatically.** Step 4b now cleans up the leftover nested `_checkpoints/`/`_schemas/` clutter inside `addresses/` and resets `addresses`' real shared-root checkpoint/schema/table every time this notebook runs, so it always starts from a clean state rather than requiring a manual reset.
# MAGIC 3. ~~`payments` format~~ — **Resolved**, corrected to CSV above.
# MAGIC
# MAGIC ### Corrections applied in this version
# MAGIC
# MAGIC - `MOUNT_POINT` and `MOUNT_BASE` now match the real customers notebook exactly — `MOUNT_BASE = MOUNT_POINT`, **no** `raw-data`/`raw-demo-data` suffix appended
# MAGIC - Checkpoint/schema paths moved to the **shared root structure** used by the customers notebook — `{MOUNT_BASE}/_checkpoints/{table_name}/` and `{MOUNT_BASE}/_schemas/{table_name}/` — not nested inside each source folder
# MAGIC - CSV and JSON sources are built with **separate, explicit option chains** — no CSV-only option is ever applied to a JSON source
# MAGIC - Every source folder is checked for existence AND for having at least one file matching the expected format extension **before** Auto Loader starts — a missing/empty/mismatched folder is skipped with a clear message, never an exception
# MAGIC - `addresses`' known stale state is cleaned up automatically (Step 4b) instead of requiring you to remember a manual reset

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Reuse the Existing Mount + Shared Config
# MAGIC
# MAGIC Same `MOUNT_POINT`, same `CATALOG`/`SCHEMA`, same `MOUNT_BASE` as the customers notebook — copied verbatim, not redefined differently. `MOUNT_BASE` is the mount point itself; the source folders (`addresses/`, `products/`, etc.) sit directly under it.

# COMMAND ----------

from pyspark.sql.functions import col, current_timestamp

# ─── Same values as the customers notebook — reused, not re-mounted ───────────
MOUNT_POINT = "/mnt/virinchy_gbmart_data"
CATALOG = "harsh_kumar01_npmentorskool_onmicrosoft_com"   # ← different catalog than gbmart
SCHEMA = "bronze"

# No raw-data / raw-demo-data suffix -- source folders live directly under the mount
MOUNT_BASE  = MOUNT_POINT

# Fail fast with a clear message instead of a confusing downstream error if
# the mount from the customers notebook isn't active in this session.
mount_exists = any(m.mountPoint == MOUNT_POINT for m in dbutils.fs.mounts())
if not mount_exists:
    raise RuntimeError(
        f"{MOUNT_POINT} is not mounted in this session. "
        f"Run the customers notebook's mount cell first."
    )

print(f"Mount point : {MOUNT_POINT}  (confirmed mounted)")
print(f"Mount base  : {MOUNT_BASE}")
print(f"Catalog     : {CATALOG}")
print(f"Schema      : {SCHEMA}")

# COMMAND ----------

# ─── Make sure the catalog/schema exist (same as the customers notebook) ──────
spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
print(f"Catalog '{CATALOG}' and schema '{SCHEMA}' are ready.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 — Table Configuration
# MAGIC
# MAGIC One entry per source folder — this list is the *only* thing that changes per table. **Only `products` is JSON; the other four are CSV.**

# COMMAND ----------

# ─── Source folder → target table → file format, one row per Bronze table ─────
# UPDATED based on real diagnostic + portal evidence -- the actual mapping is
# the OPPOSITE of what was originally specified:
#   payments/  contains payments_0*.csv   -> CSV  (confirmed via Step 3 diagnostic)
#   products/  contains products_010626.json -> JSON (confirmed via Azure Portal screenshot)
BRONZE_SOURCES = [
    {"source_folder": "addresses",        "table_name": "addresses",        "format": "csv"},
    {"source_folder": "products",         "table_name": "products",         "format": "json"},
    {"source_folder": "payment_methods",  "table_name": "payment_methods",  "format": "csv"},
    {"source_folder": "returns",          "table_name": "returns",          "format": "csv"},
    {"source_folder": "payments",         "table_name": "payments",         "format": "csv"},
]

print("Configured sources:")
for cfg in BRONZE_SOURCES:
    print(f"  {cfg['source_folder']:<18} -> {CATALOG}.{SCHEMA}.{cfg['table_name']:<18} format={cfg['format'].upper()}")

# COMMAND ----------

# ─── Preview the raw content of the products JSON file ────────────────────────
# CF_FAILED_TO_INFER_SCHEMA usually means the JSON reader's default
# assumption (one object PER LINE, i.e. NDJSON) doesn't match the real file.
# A 394 KB single-file export is much more likely to be a pretty-printed
# ARRAY ("[\n {...},\n {...}\n]") -- which needs multiLine=true to parse.
preview_path = "/mnt/virinchy_gbmart_data/products/products_010626.json"
raw_preview = dbutils.fs.head(preview_path, 500)
print(f"First 500 characters of {preview_path}:\n")
print(raw_preview)
print("\n---")
if raw_preview.strip().startswith("["):
    print("Starts with '[' -- JSON ARRAY. Needs cloudFiles.multiLine = \"true\" (added below).")
elif raw_preview.strip().startswith("{"):
    print("Starts with '{' -- likely NDJSON already. If ingestion still fails with")
    print("multiLine=true, this file is probably one-object-per-line and multiLine should be false.")

display(dbutils.fs.ls("/mnt/virinchy_gbmart_data/products"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 — Diagnostic: See the Raw Contents of Every Source Folder
# MAGIC
# MAGIC Run this once before anything else, especially the first time. `dbutils.fs.ls()` shows *every* entry in a folder — including stray marker files, differently-named files, or subfolders — none of which necessarily match what Auto Loader will actually try to read. Look at the real file names and extensions printed below before trusting any later "X files found" summary.

# COMMAND ----------

for cfg in BRONZE_SOURCES:
    path = f"{MOUNT_BASE}/{cfg['source_folder']}/"
    print(f"\n{'='*70}")
    print(f"{cfg['source_folder']}/  (expecting {cfg['format'].upper()} files)  ->  {path}")
    try:
        entries = dbutils.fs.ls(path)
        if not entries:
            print("  (folder exists but is completely empty)")
        for e in entries:
            kind = "DIR " if e.isDir() else "file"
            print(f"  [{kind}] {e.name}   ({e.size:,} bytes)")
    except Exception as ex:
        # Print just the first line of the error -- the full Py4J/Java stack
        # trace is noisy and the first line already says "No such file or directory".
        first_line = str(ex).strip().splitlines()[0] if str(ex).strip() else str(ex)
        print(f"  Folder does not exist or is not accessible: {first_line}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3b — Format-Aware Pre-Flight Check
# MAGIC
# MAGIC The earlier version of this check only asked "does `dbutils.fs.ls()` return anything?" — which said "OK to ingest" even when the entries present didn't actually match the expected file format. That mismatch is exactly what causes `CF_EMPTY_DIR_FOR_SCHEMA_INFERENCE`: Auto Loader's own file discovery filters for files matching `cloudFiles.format`, so a folder that looks non-empty to `ls()` can still look empty to Auto Loader if nothing in it actually matches. This version checks for files with the right extension specifically, and prints their real names so a mismatch is visible immediately instead of surfacing as a cryptic Auto Loader error two steps later.

# COMMAND ----------

def source_has_files(source_folder, source_path, file_format):
    """
    Returns True only if source_path exists AND contains at least one file
    whose name matches the expected file_format's extension. Never raises --
    a missing folder, an empty folder, or a folder with only non-matching
    files is reported and skipped, not a notebook-stopping exception.
    """
    try:
        entries = dbutils.fs.ls(source_path)
    except Exception as e:
        first_line = str(e).strip().splitlines()[0] if str(e).strip() else str(e)
        print(f"  WARNING: source folder does not exist, skipping {source_folder} -> {source_path} ({first_line})")
        return False

    if len(entries) == 0:
        print(f"  Skipping {source_folder} because the folder is empty.")
        return False

    extension = f".{file_format}"
    matching_files = [
        e for e in entries
        if not e.isDir() and e.name.lower().endswith(extension)
    ]

    if not matching_files:
        all_names = [e.name for e in entries]
        print(f"  Skipping {source_folder}: found {len(entries)} entr{'y' if len(entries)==1 else 'ies'} "
              f"but NONE end in '{extension}' -- {all_names}")
        print(f"  Check whether {source_folder}/ actually contains {file_format.upper()} files, "
              f"or whether BRONZE_SOURCES has the wrong format for this source.")
        return False

    print(f"  {source_folder}: {len(matching_files)} matching {file_format.upper()} file(s) found — OK to ingest.")
    for f in matching_files:
        print(f"    - {f.name}")
    return True

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 — Reusable Ingestion Function
# MAGIC
# MAGIC Same checkpoint/schema path pattern as the customers notebook — a **shared root** `_checkpoints/` and `_schemas/` folder directly under `MOUNT_BASE`, each with one subfolder per table:
# MAGIC
# MAGIC ```
# MAGIC /mnt/virinchy_gbmart_data/
# MAGIC │
# MAGIC ├── addresses/
# MAGIC ├── products/
# MAGIC ├── payments/
# MAGIC ├── payment_methods/
# MAGIC ├── returns/
# MAGIC │
# MAGIC ├── _checkpoints/
# MAGIC │      ├── addresses/
# MAGIC │      ├── products/
# MAGIC │      ├── payments/
# MAGIC │      ├── payment_methods/
# MAGIC │      └── returns/
# MAGIC │
# MAGIC └── _schemas/
# MAGIC        ├── addresses/
# MAGIC        ├── products/
# MAGIC        ├── payments/
# MAGIC        ├── payment_methods/
# MAGIC        └── returns/
# MAGIC ```
# MAGIC
# MAGIC **CSV and JSON are built as separate, explicit branches below** — no CSV-only option (`header`) is ever applied when reading the JSON `payments` source, and vice versa. Step 3b's format-aware check runs first; if it fails, the function returns `None` and moves on instead of calling Auto Loader against nothing.

# COMMAND ----------

def ingest_source_to_bronze(source_folder, table_name, file_format):
    """
    Ingest one source folder into one Bronze Delta table via Auto Loader.
    Mirrors the customers notebook's ingestion cell exactly -- only
    source_folder / table_name / file_format vary per call.
    Returns the target table name on success, or None if the source was
    skipped (missing/empty folder, or no files matching file_format).
    """

    # Shared root checkpoint/schema structure -- same as the customers notebook.
    source_path     = f"{MOUNT_BASE}/{source_folder}/"
    checkpoint_path = f"{MOUNT_BASE}/_checkpoints/{table_name}/"
    schema_path     = f"{MOUNT_BASE}/_schemas/{table_name}/"
    target_table    = f"{CATALOG}.{SCHEMA}.{table_name}"

    print(f"\n{'='*70}")
    print(f"Checking : {source_folder}/  ->  {target_table}  ({file_format.upper()})")

    # ─── Step 3b's format-aware pre-flight check -- never start Auto Loader on nothing ──
    if not source_has_files(source_folder, source_path, file_format):
        return None

    print(f"  Source     : {source_path}")
    print(f"  Checkpoint : {checkpoint_path}")
    print(f"  Schema     : {schema_path}")

    # ─── Build the Auto Loader read -- CSV and JSON handled as separate branches ──
    if file_format == "csv":
        source_df = (
            spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", "csv")
            .option("cloudFiles.schemaLocation", schema_path)
            .option("cloudFiles.inferColumnTypes", "true")
            .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
            .option("header", "true")              # CSV-only: first row is a header row
            .load(source_path)
            .withColumn("_source_file", col("_metadata.file_path"))
            .withColumn("_ingested_at", current_timestamp())
        )
    elif file_format == "json":
        source_df = (
            spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", "json")
            .option("cloudFiles.schemaLocation", schema_path)
            .option("cloudFiles.inferColumnTypes", "true")
            .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
            # multiLine=true: CF_FAILED_TO_INFER_SCHEMA on products/ was caused by
            # the JSON reader's default one-object-per-line assumption not matching
            # a pretty-printed JSON array. Check the Step 3 preview -- if the real
            # file starts with '{' instead of '[', set this back to "false".
            .option("multiLine", "true")
            # No "header" option here -- JSON records already carry their own field names.
            .load(source_path)
            .withColumn("_source_file", col("_metadata.file_path"))
            .withColumn("_ingested_at", current_timestamp())
        )
    else:
        raise ValueError(f"Unsupported file_format '{file_format}' for {source_folder} -- expected 'csv' or 'json'")

    # ─── Write to Bronze as a managed Delta table -- identical for both branches ──
    (
        source_df.writeStream
        .format("delta")
        .outputMode("append")
        .option("checkpointLocation", checkpoint_path)
        .option("mergeSchema", "true")
        .trigger(availableNow=True)
        .toTable(target_table)
    )

    row_count = spark.table(target_table).count()
    print(f"  Done. {target_table} now has {row_count:,} rows.")
    return target_table

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4b — Reset Helper + Clean Up Known Stale State
# MAGIC
# MAGIC Two things fixed here, both diagnosed in the previous run:
# MAGIC
# MAGIC 1. **`reset_bronze_table()`** is now a live, callable function (previously it only existed as commented-out example code at the bottom of the notebook) — clears a table's shared-root checkpoint/schema and drops the table, so its next ingestion run starts completely clean.
# MAGIC 2. **`addresses/` gets cleaned up automatically below** — both the stale nested `_checkpoints/`/`_schemas/` subfolders sitting *inside* `addresses/` itself (leftover clutter from an earlier version of this pipeline, harmless but messy), and a full reset of `addresses`' real shared-root checkpoint/schema/table, since the diagnostic evidence pointed to a stale checkpoint there causing 0 rows to land.
# MAGIC
# MAGIC This cell is safe to re-run — `dbutils.fs.rm(..., recurse=True)` and `DROP TABLE IF EXISTS` are both no-ops if there's nothing there to remove.

# COMMAND ----------

def reset_bronze_table(table_name):
    """
    Deletes the Bronze table and attempts to remove its Auto Loader
    checkpoint and schema folders.

    If the folders cannot be deleted (common with Azure Blob Storage),
    the notebook will continue instead of failing.
    """

    checkpoint_path = f"{MOUNT_BASE}/_checkpoints/{table_name}/"
    schema_path     = f"{MOUNT_BASE}/_schemas/{table_name}/"
    target_table    = f"{CATALOG}.{SCHEMA}.{table_name}"

    print(f"\nResetting {target_table}")

    # Remove checkpoint
    try:
        dbutils.fs.rm(checkpoint_path, recurse=True)
        print(f"✓ Deleted {checkpoint_path}")
    except Exception as e:
        print(f"⚠ Could not delete checkpoint: {checkpoint_path}")
        print(f"   {e}")

    # Remove schema
    try:
        dbutils.fs.rm(schema_path, recurse=True)
        print(f"✓ Deleted {schema_path}")
    except Exception as e:
        print(f"⚠ Could not delete schema: {schema_path}")
        print(f"   {e}")

    # Drop Bronze table
    spark.sql(f"DROP TABLE IF EXISTS {target_table}")
    print(f"✓ Dropped table {target_table}")

# COMMAND ----------

# ─── Reset products too -- the failed schema-inference attempt may have already
# written a partial/empty schema log entry at _schemas/products/, which could
# interfere with the retry even after adding multiLine=true. Clean slate.
print("Cleaning up known stale state for 'addresses' and 'products'...")
reset_bronze_table("addresses")
reset_bronze_table("products")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5 — Run the Ingestion for All 5 Sources
# MAGIC
# MAGIC One loop over `BRONZE_SOURCES`, calling the same function each time. Any source that's missing or empty is skipped with a message — the loop keeps going for the rest.

# COMMAND ----------

ingested_tables = []
skipped_sources = []

for cfg in BRONZE_SOURCES:
    try:
        result = ingest_source_to_bronze(
            source_folder=cfg["source_folder"],
            table_name=cfg["table_name"],
            file_format=cfg["format"],
        )

        if result is not None:
            ingested_tables.append(result)
        else:
            skipped_sources.append(cfg["source_folder"])

    except Exception as e:
        print(f"\n❌ Failed to ingest {cfg['table_name']}")
        print(e)
        skipped_sources.append(cfg["source_folder"])

print(f"\n{'='*70}")
print(f"Ingested {len(ingested_tables)} table(s):")
for t in ingested_tables:
    print(f"  - {t}")

if skipped_sources:
    print(f"\nSkipped/Failed {len(skipped_sources)} source(s):")
    for s in skipped_sources:
        print(f"  - {s}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6 — Verify Each Ingested Bronze Table
# MAGIC
# MAGIC Same verification shape as the customers notebook — schema, row count, sample rows, and a per-source-file breakdown — looped across whichever tables actually got ingested (skipped sources have no table to verify yet).

# COMMAND ----------

for target_table in ingested_tables:
    df = spark.table(target_table)

    print(f"\n{'='*70}")
    print(f"{target_table}")
    print(f"  Total rows : {df.count()}")
    print(f"  Columns    : {df.columns}")
    df.display(5, truncate=False)

# COMMAND ----------

# Row count per source file, per table.
for target_table in ingested_tables:
    print(f"\n{target_table} — rows per source file:")
    spark.table(target_table).groupBy("_source_file").count().orderBy("_source_file").display(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 7 — Test Incremental Load (Optional, Same Pattern as the Customers Notebook)
# MAGIC
# MAGIC 1. Note the current row counts printed above for whichever table you want to test (e.g. `returns`).
# MAGIC 2. Upload one additional file into that table's mounted source folder (e.g. `/mnt/virinchy_gbmart_data/returns/`).
# MAGIC 3. Re-run **just that one table's ingestion** using the helper function directly — no need to re-run the whole loop:
# MAGIC ```python
# MAGIC ingest_source_to_bronze(source_folder="returns", table_name="returns", file_format="csv")
# MAGIC ```
# MAGIC 4. Auto Loader's checkpoint (at `_checkpoints/returns/`) skips the files it already processed and only ingests the new one — row count grows with no duplicates, exactly like the customers notebook.
# MAGIC
# MAGIC 5. If a source was skipped in Step 5 because its folder was empty or missing (e.g. `products` had no files uploaded yet), upload files into it now and simply re-run its ingestion the same way:
# MAGIC ```python
# MAGIC ingest_source_to_bronze(source_folder="products", table_name="products", file_format="json")
# MAGIC ```

# COMMAND ----------

# Example: re-run a single table after uploading a new file to its source folder,
# or after populating a source that was previously empty/missing.

# ingest_source_to_bronze(source_folder="returns", table_name="returns", file_format="csv")
# ingest_source_to_bronze(source_folder="products", table_name="products", file_format="json")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Reset (if needed)
# MAGIC `reset_bronze_table()` was already defined in Step 4b — reuse it here for any table, not just `addresses`. Only run for the specific table(s) you want to reset.

# COMMAND ----------

# Example: reset any single table before re-ingesting it.
# reset_bronze_table("returns", "returns")
# reset_bronze_table("products", "products")

# COMMAND ----------

for target_table in ingested_tables:
    display(spark.sql(f"DESCRIBE DETAIL {target_table}"))

# COMMAND ----------

CATALOG = "harsh_kumar01_npmentorskool_onmicrosoft_com"
SCHEMA  = "bronze"

BRONZE_TABLES = [
    "customers", "addresses", "payments", "payment_methods",
    "products", "returns"
]

for table in BRONZE_TABLES:
    full_name = f"{CATALOG}.{SCHEMA}.{table}"
    spark.sql(f"""
        ALTER TABLE {full_name}
        SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
    """)
    print(f"CDF enabled: {full_name}")