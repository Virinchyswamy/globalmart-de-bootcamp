# Accessing ADLS from Databricks
## Content Type
Scenario

## Overview
Connect Databricks to Azure Data Lake Storage Gen2 using two approaches — spark.conf.set() for session-level access and a mount point for persistent workspace-wide access — then use COPY INTO to load files incrementally into a Delta table.

## Learning Objectives
- Configure ADLS Gen2 access in Databricks using spark.conf.set() and read files into a DataFrame.
- Create a persistent DBFS mount point and access ADLS files using a short /mnt/ path.
- Use COPY INTO to load CSV files from ADLS into a Delta table and observe its idempotent behaviour.

## Prerequisites
- Basic understanding of ADLS & Pysparrk

## Duration of Completion
30 minutes

## Level
Beginner

## Industries
- retail-and-cpg

## Tags
- batch-etl (skill)
- data-storage (skill)
- databricks (tool)

#### Overview
Connect Databricks to Azure Data Lake Storage Gen2 using two approaches — spark.conf.set() for session-level access and a mount point for persistent workspace-wide access — then use COPY INTO to load files incrementally into a Delta table.

#### Level
beginner

#### Industries
- retail-and-cpg

#### Tags
- batch-etl (skill)
- data-storage (skill)
- databricks (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

### The Problem We Are Solving

GlobalMart's files and customers live in **Azure Data Lake Storage Gen2 (ADLS)**. This is the raw source for everything we will build in the Silver and Gold layers.

Before Databricks can read, transform, or load any of this data, it needs to know how to authenticate with ADLS. There is no automatic connection — you have to tell Databricks which storage account to access and provide the credentials to do so.

There are two common ways to establish this connection:

| Approach | How it works | Best for |
|---|---|---|
| **spark.conf.set()** | Sets the storage key directly in the Spark session | Quick exploration, dev/POC, single notebook |
| **Mount Point** | Maps the ADLS path to `/mnt/` in DBFS — access like a local path | Shared access across notebooks, legacy workspaces |

Once connected, we will use **COPY INTO** — a SQL command that loads files from ADLS into a Delta table incrementally, tracking which files have already been loaded so they are never processed twice.

**Tags**


##### Input 2
**Type:** Text

>[!IMPORTANT] 
> Before You Begin — Setup Checklist

> Complete the following before running any notebook cells:
>
> **1. Confirm your ADLS is ready**
> Ensure the storage account (`ecomadlsdata`) and container (`ecom-demo-data`) are accessible. Your instructor will confirm access details.
>
> **2. Upload the first file now**
> Go to **Azure Portal → Storage Account → `ecomadlsdata` → Containers → `ecom-demo-data` → `customers/`** and upload:
> - ✅ `customers_1.csv` — [Dataset](https://cdn.enqurious.com/documents/17efb59f-93de-4dd0-aa1d-6e47d681b93c_customers1.csv)

> **3. Hold the second file**
> - ⏸ `customers_2.csv` — [Dataset](https://cdn.enqurious.com/documents/bfaa4904-d4cd-4510-8bc2-06a00e573fc9_customers2.csv) (**do not upload yet.** You will be explicitly told when to upload it in the COPY INTO Part 2 step. Uploading it early will affect the exercise outcome.)

**Tags**


##### Input 3
**Type:** Text

### Approach 1 — spark.conf.set()

> **Open the notebook provided** (`adls_connection_approaches.ipynb`) in your Databricks workspace and follow along. The steps below mirror the notebook cells.
- [Notebook](https://cdn.enqurious.com/others/48fe2df9-14fa-40a4-9d66-f102adcff007_adlsconnectionapproaches.ipynb)

Follow the steps below to do it yourself.

**How it works**

You register the storage account key with the current Spark session. Databricks uses this key whenever it sees a path pointing to that storage account. The configuration lasts for the duration of the session — when the cluster restarts or a new session opens, you need to set it again.

The ADLS Gen2 path format is:
```
abfss://<container>@<storage-account>.dfs.core.windows.net/<path>
```

---

**Step 1 — Open a new notebook and run the following:**

```python
# Storage account details
storage_account = "ecomadlsdata"
container       = "ecom-demo-data"
access_key      = "<access-key-provided-by-instructor>"

# Register the key with the Spark session
spark.conf.set(
    f"fs.azure.account.key.{storage_account}.dfs.core.windows.net",
    access_key
)

print("Spark session configured for ADLS access.")
```

---

**Step 2 — Build the path and list files:**

```python
adls_path = f"abfss://{container}@{storage_account}.dfs.core.windows.net/"

# List files in the container
dbutils.fs.ls(adls_path)
```

You should see the files and folders available in the container.

---

**Step 3 — Read data into a DataFrame:**

```python
df = (spark.read.format("csv")
      .option("header", "true")
      .option("inferSchema", "true")
      .load(adls_path + "customers/"))

display(df)
```

**Tags**


##### Input 4
**Type:** File Upload

**Question:** Upload a screenshot showing the customers data loaded into a DataFrame using `spark.conf.set()`. The screenshot should show the `display(df)` output with column names and rows visible.

**Max No. of Files:** 2

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- databricks / ingestion-and-parsing (tool)

##### Input 5
**Type:** Text

### Approach 2 — Mount Point

> **Continue in the same notebook** — scroll to the Approach 2 section and follow along.


**What is a Mount Point?**

A mount point maps an ADLS container to a short, friendly path in DBFS — usually under `/mnt/`. Once mounted, you access files using that short path instead of the full `abfss://` URL, and the mount persists across cluster restarts until you explicitly remove it.

Think of it like mapping a network drive:
- **Without mount:** `abfss://ecom-demo-data@ecomadlsdata.dfs.core.windows.net/customers/`
- **With mount:** `/mnt/ecom-demo-data/customers/`

---

**Advantages and Disadvantages**

| Advantages | Disadvantages |
|---|---|
| Set once — accessible from any notebook in the workspace | Deprecated in Unity Catalog environments |
| Cleaner, shorter paths | No fine-grained access control — anyone in the workspace can access the mount |
| No need to repeat `spark.conf.set()` in every notebook | Updating credentials requires unmounting and remounting |

---

**Step 1 — Create the mount:**

```python
storage_account = "ecomadlsdata"
container       = "ecom-demo-data"
access_key      = "<access-key-provided-by-instructor>"
mount_point     = "/mnt/ecom-demo-data"

# Check if already mounted
existing_mounts = [m.mountPoint for m in dbutils.fs.mounts()]

if mount_point in existing_mounts:
    print(f"Already mounted at {mount_point} — skipping.")
else:
    dbutils.fs.mount(
        source        = "wasbs://{0}@{1}.blob.core.windows.net".format(container, storage_account),
        mount_point   = mount_point,
        extra_configs = {
            "fs.azure.account.key.{0}.blob.core.windows.net".format(storage_account): access_key
        }
    )
    print(f"Successfully mounted at {mount_point}")
```

---

**Step 2 — Verify the mount and list files:**

```python
# Confirm the mount appears in the list
display(dbutils.fs.mounts())

# List files using the short path
dbutils.fs.ls(mount_point + "/customers/")
```

---

**Step 3 — Read data using the mount path:**

```python
df_mount = (spark.read.format("csv")
            .option("header", "true")
            .option("inferSchema", "true")
            .load(mount_point + "/customers/"))

display(df_mount)
```

**Tags**


##### Input 6
**Type:** File Upload

**Question:** Upload a screenshot of `display(dbutils.fs.mounts())` showing your mount point `/mnt/ecom-demo-data` listed as active.

**Max No. of Files:** 2

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- databricks / ingestion-and-parsing (tool)

##### Input 7
**Type:** Text

### COPY INTO — Load Files into a Delta Table (Part 1)

So far, `spark.read` and the mount point let you explore data interactively. But for building a proper pipeline, you need data to land in a **governed Delta table** — not just a temporary DataFrame.

**COPY INTO** is a SQL command that loads files from a cloud storage path into a Delta table. What makes it powerful is that it is **idempotent** — it tracks which files have already been loaded and skips them automatically on subsequent runs. You can point it at the same folder repeatedly and it will only process new files.

---

> 📁 **Dataset:** You have been provided with two files — `customers_1.csv` and `customers_2.csv`. For this step, **upload only `customers_1.csv`** to your ADLS container under `customers/`.
>
> Go to **Azure Portal → Storage Account → Containers → ecom-demo-data → customers/** and upload `customers_1.csv` before running the steps below.

---

**Step 1 — Create the target Delta table:**

```sql
CREATE TABLE IF NOT EXISTS <your-catalog>.raw_schema.customers_raw (
    CustomerID  STRING,
    FirstName   STRING,
    LastName    STRING,
    Email       STRING,
    Phone       STRING,
    CreatedAt   TIMESTAMP
)
USING DELTA;
```

---

**Step 2 — Run COPY INTO:**

```sql
COPY INTO <your-catalog>.raw_schema.customers_raw
FROM '/mnt/ecom-demo-data/customers/'
FILEFORMAT = CSV
FORMAT_OPTIONS (
    'header'      = 'true',
    'inferSchema' = 'true'
)
COPY_OPTIONS (
    'mergeSchema' = 'true'
);
```

---

**Step 3 — Verify the row count:**

```sql
SELECT COUNT(*) AS total_rows FROM <your-catalog>.raw_schema.customers_raw;
```

Note the row count — you will compare this after uploading the second file.

**Tags**


##### Input 8
**Type:** File Upload

**Question:** Upload a screenshot showing the row count in `customers_raw` after the first COPY INTO run (with only `customers_1.csv` loaded).

**Max No. of Files:** 2

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- databricks / ingestion-and-parsing (tool)

##### Input 9
**Type:** Text

### COPY INTO — Idempotency in Action (Part 2)

Now upload `customers_2.csv` to the same `customers/` folder in ADLS — then rerun the exact same COPY INTO command from the previous step.

> Go to **Azure Portal → Storage Account → Containers → ecom-demo-data → customers/** and upload `customers_2.csv`.

Once uploaded, rerun:

```sql
COPY INTO <your-catalog>.raw_schema.customers_raw
FROM '/mnt/ecom-demo-data/customers/'
FILEFORMAT = CSV
FORMAT_OPTIONS (
    'header'      = 'true',
    'inferSchema' = 'true'
)
COPY_OPTIONS (
    'mergeSchema' = 'true'
);
```

Then check the row count again:

```sql
SELECT COUNT(*) AS total_rows FROM <your-catalog>.raw_schema.customers_raw;
```

> **What you should observe:**
> - The row count increases by exactly the number of rows in `customers_2.csv`
> - `customers_1.csv` is **not re-loaded** — COPY INTO tracked it from the first run and skipped it
> - No duplicates, no manual file tracking needed

---

**COPY INTO — One Important Limitation**

COPY INTO works by **directly listing all files** in the folder on every run to determine which ones are new. With two files, this is instant. But imagine a folder that has grown to 100,000 files over two years — listing that entire directory on every pipeline run becomes a significant bottleneck.

This is exactly the problem that **Autoloader** solves. Instead of listing files, Autoloader uses file notification events from the cloud storage — it only processes the files that actually arrived since the last run, without scanning the entire folder. For large-scale, continuously growing datasets, Autoloader is the right choice.

> COPY INTO → great for small to medium batch ingestion  
> Autoloader → built for continuously growing, high-volume file ingestion at scale

**Tags**


##### Input 10
**Type:** File Upload

**Question:** Upload a screenshot showing the row count in `customers_raw` after the second COPY INTO run (with both files loaded). The count should have increased by only the rows in `customers_2.csv`.

**Max No. of Files:** 2

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- data-storage / delta-lakehouse / copy-into (skill)

##### Input 11
**Type:** Choice

**Question:** You ran COPY INTO twice against the same `customers/` folder — first with `customers_1.csv` present, then after adding `customers_2.csv`. On the second run, why was `customers_1.csv` not loaded again?

**Options:** 
- COPY INTO automatically deduplicates rows using the primary key, so even if the file is re-read, duplicates are removed

- COPY INTO tracks which files have already been loaded. On subsequent runs it skips files it has already processed and only loads new ones

- COPY INTO only reads the most recently modified file in the folder, so older files are ignored

- The Delta table schema prevents the same file from being inserted twice

**Correct Options:** 
- COPY INTO tracks which files have already been loaded. On subsequent runs it skips files it has already processed and only loads new ones

**Solution:** 
COPY INTO maintains an internal record of every file it has successfully loaded. On each run, it compares the files currently in the folder against this record and processes only the ones that are new. This makes it **idempotent** — safe to re-run at any time without risk of duplicating data. It is important to note that this tracking is file-name based, not content-based. If you upload the same data under a new filename, COPY INTO will load it again.

**Tags**
- data-storage / delta-lakehouse / copy-into (skill)

