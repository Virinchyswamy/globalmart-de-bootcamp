# Building a CDC Pipeline with Lakeflow Connect
## Content Type
Project

## Overview
<p style="text-align:justify;">
GlobalMart processes thousands of orders every day; new orders come in, statuses change, and some orders are cancelled and deleted. A traditional full-load pipeline running at midnight would miss every hard delete and lag hours behind the source. This project solves that problem using a CDC-based ingestion pipeline built entirely on Databricks.

<p style="text-align:justify;">
You will set up a live Postgres database on Supabase to simulate GlobalMart's transactional source, connect it to Databricks via Lakeflow Connect, and create an Ingestion Pipeline to land data into a Delta Streaming Table in Unity Catalog. Finally, you will make real changes in the source, updates and inserts, rerun the pipeline, and observe exactly how incremental ingestion works in practice.

## Learning Objectives
- Understand why CDC is the preferred ingestion approach for transactional source data compared to full load or incremental load
- Configure a Postgres source database to support logical replication and incremental change tracking

## Prerequisites
- Basic understanding of SQL and relational databases
- Familiarity with data ingestion concepts
- Connect a Postgres source to Databricks using Lakeflow Connect and verify source tables in the Catalog Explorer
- Create and run an Ingestion Pipeline to land data into a Delta Streaming Table in Unity Catalog
- Observe how the pipeline detects and applies only changed rows using an incremental cursor

## Duration of Completion
60 minutes

## Level
Intermediate

## Industries
- retail-and-cpg

## Tags
- data-storage (skill)
- batch-etl (skill)
- data-engineering (skill)
- databricks (tool)
- data-understanding (skill)
- sql (tool)

## Scenarios
### Creating the Ingestion Pipeline
#### Overview
Understand why the Ingestion Pipeline is the key step that makes CDC work, and create one using your Lakeflow Connect connection to land orders data into a Delta Streaming Table in your Unity Catalog.

#### Level
beginner

#### Industries
- retail-and-cpg

#### Tags
- data-storage (skill)
- batch-etl (skill)
- data-engineering (skill)
- databricks (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

### Why Does the Ingestion Pipeline Come Into the Picture?

In the previous activity, you created a **Lakeflow Connect** connection. You could see `orders_practice` in the Catalog Explorer, but if you tried to query it or run a transformation on it, you'd quickly realise something is missing.

**The data is still in Postgres.**

Lakeflow Connect created a live window into your source database. Think of it as a door between Postgres and Databricks, the door exists, but nothing has walked through it yet. The **Ingestion Pipeline** is what actually moves the data through that door.

**The Two-Step Model**

| Step | What it does | Where data lives after |
|---|---|---|
| **Lakeflow Connect** | Creates the connection, reads the Postgres WAL for CDC events | Still in Postgres |
| **Ingestion Pipeline** | Pulls CDC events through the connection, applies them into Delta | In your catalog's `raw_schema` (Delta Streaming Table) |

CDC only becomes useful when the changes land somewhere, and landing them correctly into Delta is exactly what the Ingestion Pipeline does. Every INSERT, UPDATE, and DELETE that happens in Postgres gets captured by Lakeflow Connect and applied to the Delta table by the pipeline.

**SCD1 & SCD2 - Built In**

The Ingestion Pipeline doesn't just dump data into a table. It supports two standard strategies for handling changes:

- **SCD Type 1 (History tracking: Off)** - The latest value wins. When a row is updated in Postgres, the corresponding row in Delta is overwritten. No history is kept. Simple and efficient.
- **SCD Type 2 (History tracking: On)** - Full history is preserved. When a row is updated, the old version is closed out with an end date and a new version is inserted. This is how you track *how* a record changed over time, for example, tracking every status an order went through from Placed to Delivered.

You configure this at the pipeline level via the **History tracking** setting, Databricks handles the MERGE logic for you.

**"Streaming Table sounds expensive,  is it always running?"**

> This is a common concern worth addressing upfront.

The Ingestion Pipeline creates a **Delta Streaming Table**, and "streaming" often sounds like it means a 24/7 running process. It does not.

- **Streaming Table** refers to the *table type* - designed to receive incremental updates efficiently. It is not continuously executing.
- The pipeline runs **only when triggered** - on a schedule or manually. When idle, there is zero compute cost.
- It uses **Serverless compute** - you pay only for the seconds it is actively processing changes.
- Because it uses CDC, each run processes **only what changed** since the last run,  not the full table.

Compare this to reloading 10 million orders every night just to pick up 500 new or updated rows. Full load is far more expensive at scale. The Streaming Table + CDC approach is actually the cost-efficient choice.

**Tags**


##### Input 2
**Type:** Text

### Step 1 — Create the Target Schema

Before creating the pipeline, you need a schema in your catalog where the ingested data will land.

> 📌 **Note:** Your catalog has already been created for you in Unity Catalog — you do not need to create it. You only need to create the schema inside it.

You have two options — choose whichever is convenient:

**Option A — Create the schema upfront using SQL**

Open a Databricks notebook or SQL Editor and run:

```sql
-- Replace <your-catalog> with your catalog name
CREATE SCHEMA IF NOT EXISTS <your-catalog>.raw_schema;
```

Verify it was created:

```sql
SHOW SCHEMAS IN <your-catalog>;
```

You should see `raw_schema` listed.

**Option B — Create the schema directly inside the pipeline wizard**

When you reach Step 2 of the pipeline setup (Event log location), click **+ Create schema** from the schema dropdown and type `raw_schema`. Databricks will create it for you without leaving the wizard.

Either option works — proceed with whichever is easier.

**Tags**


##### Input 3
**Type:** Text

### Step 2 — Create the Ingestion Pipeline

Watch the video below. It walks through the full pipeline setup in Databricks — selecting the connection, configuring the source table, and seeing the orders data land in `raw_schema`.

- [Ingestion-pipeline-creation](https://cdn.enqurious.com/videos/563da684-2650-487b-b928-728aa937643b_ingestionpipeline.mp4)

Once you have watched the video, follow the steps below to create your own pipeline.

**Navigate to Ingestion Pipeline**

In the Databricks sidebar → **Jobs & Pipelines** → under **Create new** → click **Ingestion pipeline**

**Step 1 of 5 — Connection**

Select your PostgreSQL connection from the list (the one you created in the Lakeflow Connect activity).

> If you do not see your connection, click **+ Create connection** to set it up before continuing.

**Step 2 of 5 — Ingestion setup**

| Field | Value |
|---|---|
| **Pipeline name** | `ingestion-orders-practice-<your-name>` |
| **Event log location — Catalog** | Select your catalog |
| **Event log location — Schema** | Select `raw_schema` (or click **+ Create schema** to create it now) |
| **Compute type** | Serverless |

Click **Create pipeline and continue**.

**Step 3 of 5 — Source**

- In the **Database name** field, type `postgres` and click the **+** button to load the source tree.
- Expand **`public`** → select **`orders_practice`** (checkbox on the left).
- In the settings panel on the right, configure:

| Field | Value |
|---|---|
| **Cursor column** | `updated_at` |
| **Primary key(s)** | `order_id` |
| **History tracking** | Off *(SCD Type 1 — latest value wins)* |

> **Why `updated_at` as cursor?** The cursor column tells the pipeline where to resume from on each run. It must be a column that increases monotonically with every change — `updated_at` is set automatically by our trigger function, making it a reliable cursor for incremental ingestion.

> **Why History tracking Off?** For this practice activity, we use SCD Type 1 — each pipeline run overwrites the existing row with the latest values. No historical versions are kept. If you needed to track the full history of changes (e.g. every status transition an order goes through), you would switch History tracking On (SCD Type 2).

Click **Next**.

**Step 4 of 5 — Destination**

Select `raw_schema` under your catalog. This is where the Delta Streaming Table `orders_practice` will be created.

Click **Next**.

**Step 5 of 5 — Schedules and notifications**

For this activity, **skip the schedule** — do not add one. Click **Save and run pipeline**.

> 💡 **Why no schedule?** In production, a schedule ensures the pipeline runs at regular intervals (e.g., every hour) to keep the Delta table continuously in sync with the source. For this practice run, we trigger it manually so you can observe exactly what happens during each pipeline execution. You can always add a schedule later from the pipeline settings.

**What to expect after the pipeline runs**

Once the pipeline completes, you should see:

- A **Streaming Table** node named `orders_practice` with a green checkmark
- **Upserted: 22** rows — the full initial load from Postgres

**Tags**


##### Input 4
**Type:** File Upload

**Question:** Upload a screenshot of your Ingestion Pipeline after the initial run has completed successfully. The screenshot should clearly show the pipeline name, the `orders_practice` Streaming Table node with a green checkmark, and the "Upserted: 22" row count.

**Max No. of Files:** 2

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- batch-etl / batch-pipeline-orchestration (skill)

##### Input 5
**Type:** Text

### Step 3 — Verify Data in Unity Catalog

Now confirm that the data has landed correctly in your catalog's `raw_schema`.

Open a **Databricks notebook or SQL Editor** and run:

```sql
-- Replace <your-catalog> with your catalog name
-- Check the row count
SELECT COUNT(*) AS total_orders
FROM <your-catalog>.raw_schema.orders_practice;
```

Expected result: **22 rows**

```sql
-- Preview the data
SELECT * FROM <your-catalog>.raw_schema.orders_practice
ORDER BY order_id;
```

Finally, confirm it was created as a Streaming Table:

```sql
DESCRIBE EXTENDED <your-catalog>.raw_schema.orders_practice;
```

Look for `Type: STREAMING_TABLE` in the output — this confirms the pipeline has correctly created a governed, incrementally-updatable Delta table in Unity Catalog.

**Tags**


##### Input 6
**Type:** File Upload

**Question:** Run the `SELECT COUNT(*) AS total_orders` query against your catalog's `raw_schema.orders_practice` and upload a screenshot showing the result. Expected count: 22.

**Max No. of Files:** 2

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- data-storage / delta-lakehouse / delta-lake-architecture (skill)

##### Input 7
**Type:** Choice

**Question:** You created a Lakeflow Connect connection in the previous activity and can already see `orders_practice` in the Catalog Explorer. Why is the Ingestion Pipeline still needed?

**Options:** 
- The Catalog Explorer view is read-only and cannot be queried; the Ingestion Pipeline makes the data queryable

- Lakeflow Connect only creates the connection to Postgres — the data is still in Postgres. The Ingestion Pipeline applies CDC events into a Delta table in Unity Catalog, making the data part of the Lakehouse

- The Ingestion Pipeline is needed to create the Lakeflow Connect connection before data can be read

- Without the Ingestion Pipeline, the Catalog Explorer cannot display the Postgres tables

**Correct Options:** 
- Lakeflow Connect only creates the connection to Postgres — the data is still in Postgres. The Ingestion Pipeline applies CDC events into a Delta table in Unity Catalog, making the data part of the Lakehouse

**Solution:** 
Lakeflow Connect establishes the **connection** to the Postgres source and reads the WAL — but the data remains in Postgres. The Catalog Explorer shows a live mirror of the source schema, not a copy of the data. The **Ingestion Pipeline** is the step that actually moves data — pulling CDC events through the connection and applying them (INSERT, UPDATE, DELETE) into a Delta Streaming Table in Unity Catalog. Only after the Ingestion Pipeline runs does the data exist in `raw_schema` as a queryable Delta table.

**Tags**
- databricks / lakehouse-federation (tool)

##### Input 8
**Type:** Choice

**Question:** The Ingestion Pipeline creates a Delta **Streaming Table** in Unity Catalog. A colleague says this must be very expensive since streaming runs continuously. What is the correct response?

**Options:** 
- They are right — Streaming Tables run 24/7 and are always consuming compute

- Streaming Table refers to the table type designed for incremental updates, not continuous execution. The pipeline runs only when triggered and uses Serverless compute, so you pay only for active processing time

- Streaming Tables are cheaper because they use a smaller cluster than batch pipelines

- The pipeline can be converted to a batch table to reduce costs

**Correct Options:** 
- Streaming Table refers to the table type designed for incremental updates, not continuous execution. The pipeline runs only when triggered and uses Serverless compute, so you pay only for active processing time

**Solution:** 
"Streaming Table" describes the **table design pattern** — built to receive incremental, CDC-driven updates efficiently. It does not mean the pipeline runs continuously. The Ingestion Pipeline executes only when triggered (on a schedule or manually) and uses Serverless compute, meaning you pay only for active compute seconds. Because it applies only the changes since the last run (not a full reload), each execution is fast and cost-efficient. At scale, this approach is significantly cheaper than a full load that re-reads the entire source table every run.

**Tags**
- databricks / lakehouse-federation (tool)

### CDC in Action
#### Overview
Make live changes to your Postgres source in Supabase, update an existing order and insert a new one, rerun the Ingestion Pipeline, and observe exactly how those changes are reflected in your Delta Streaming Table in Unity Catalog.

#### Level
beginner

#### Industries
- retail-and-cpg

#### Tags
- data-storage (skill)
- batch-etl (skill)
- data-engineering (skill)
- databricks (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

### What You Will Do in This Activity

You have built the pipeline. Now you will put it to the test.

So far, the Ingestion Pipeline ran once and loaded the initial 22 orders from Postgres into your Delta Streaming Table. But the real value of a CDC-driven pipeline is what happens *after* the initial load, when your source data keeps changing and your Delta table needs to stay in sync.

In this activity, you will:

1. **Update** an existing order in Supabase, change its status
2. **Insert** a brand new order into Supabase
3. **Rerun** the Ingestion Pipeline manually
4. **Query** the Delta table to confirm the changes landed

The goal is to see, firsthand, how the pipeline detects what changed and applies only those rows, without re-reading the entire table.

**How does the pipeline know what changed?**

The `updated_at` column is the key. Every time a row is inserted or updated in `orders_practice`, the trigger function sets `updated_at = NOW()`. The Ingestion Pipeline stores the highest `updated_at` value it saw in the previous run. On the next run, it only pulls rows where `updated_at` is greater than that checkpoint, meaning only the rows that changed since last time.

This is query-based incremental ingestion, efficient, targeted, and cost-effective.

**Tags**


##### Input 2
**Type:** Text

### Task 1 — Update an Existing Order in Supabase

Go to your Supabase project → **SQL Editor** → **New query**. Run the following:

```sql
-- ORD-P010 was 'Shipped' — update it to 'Delivered'
UPDATE public.orders_practice
SET    status     = 'Delivered',
       updated_at = NOW()
WHERE  order_id   = 'ORD-P010';
```

Verify the change was applied:

```sql
SELECT order_id, status, updated_at
FROM   public.orders_practice
WHERE  order_id = 'ORD-P010';
```

You should see `status = 'Delivered'` with a fresh `updated_at` timestamp.

**Tags**


##### Input 3
**Type:** Text

### Task 2 — Insert a New Order in Supabase

Still in the Supabase SQL Editor, run:

```sql
-- Add a brand new order that did not exist in the original 22
INSERT INTO public.orders_practice
    (order_id, customer_id, order_date, status, total_amount, channel, updated_at)
VALUES
    ('ORD-P023', 'CUST-121', NOW(), 'Placed', 999.00, 'Online', NOW());
```

Verify the new row was inserted:

```sql
SELECT order_id, customer_id, status, total_amount, updated_at
FROM   public.orders_practice
WHERE  order_id = 'ORD-P023';
```

You should see `ORD-P023` with status `Placed`.

Now Supabase has **23 rows** — 22 original + 1 new — and `ORD-P010` has a new status. Your Delta table still shows the old state, time to sync.

**Tags**


##### Input 4
**Type:** Text

### Task 3 — Rerun the Ingestion Pipeline

Go to your Databricks workspace → **Jobs & Pipelines** → open your `ingestion-orders-practice-<your-name>` pipeline.

Click **Run** (or **Start**) to trigger a manual run.

> The pipeline will compare the current `updated_at` checkpoint against the source. It will find exactly **2 rows** that changed since the last run:
> - `ORD-P010` — updated_at is newer (status changed)
> - `ORD-P023` — new row, did not exist in the previous run

Wait for the run to complete. You should see **Upserted: 2** in the pipeline output — not 23. This confirms the pipeline processed only the rows that changed, not the full table.

**Tags**


##### Input 5
**Type:** Text

### Task 4 — Verify Changes in the Delta Table

Open a Databricks notebook or SQL Editor and run:

```sql
-- Confirm the total row count is now 23
SELECT COUNT(*) AS total_orders
FROM <your-catalog>.raw_schema.orders_practice;
```

Expected result: **23 rows**

```sql
-- Confirm ORD-P010 now shows 'Delivered'
SELECT order_id, status, updated_at
FROM   <your-catalog>.raw_schema.orders_practice
WHERE  order_id = 'ORD-P010';
```

```sql
-- Confirm ORD-P023 exists in the Delta table
SELECT order_id, customer_id, status, total_amount
FROM   <your-catalog>.raw_schema.orders_practice
WHERE  order_id = 'ORD-P023';
```

Both rows should reflect the changes you made in Supabase — the pipeline detected them via `updated_at` and upserted them into the Delta table without touching the other 21 rows.


**Tags**


##### Input 6
**Type:** Short Answer

**Question:** Look at the two rows that changed,`ORD-P010` and `ORD-P023`. In your own words, explain: how did the Ingestion Pipeline know to pick up exactly these two rows and not the other 21? What role did the `updated_at` column play?

**Template:** null

**Tags**
- data-engineering / cdc / de-change-data-capture (skill)

##### Input 7
**Type:** File Upload

**Question:** Run the query below and upload a screenshot showing `ORD-P010` with `status = 'Delivered'` and `ORD-P023` with `status = 'Placed'`, both visible in your Delta table.

**Max No. of Files:** 2

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- data-engineering / cdc / de-change-data-capture (skill)

##### Input 8
**Type:** Choice

**Question:** After successfully observing that UPDATEs and INSERTs are captured by the pipeline, a participant tries something different — they DELETE `ORD-P004` from Supabase and rerun the pipeline. They expect the row to disappear from the Delta table. What will actually happen?

**Options:** 
- `ORD-P004` will be deleted from the Delta table — the pipeline captures all changes including deletes

- `ORD-P004` will remain in the Delta table — query-based capture uses the `updated_at` cursor and cannot detect a deleted row since it no longer exists in the source

- The pipeline will fail with an error because a deleted row causes a primary key conflict

- `ORD-P004` will be marked as deleted with a null value but not removed from the table

**Correct Options:** 
- `ORD-P004` will remain in the Delta table — query-based capture uses the `updated_at` cursor and cannot detect a deleted row since it no longer exists in the source

**Solution:** 
The Ingestion Pipeline in this activity uses **query-based capture** — it detects changes by comparing the `updated_at` cursor to its last checkpoint and pulling rows that are newer. When a row is deleted from Postgres, it simply disappears — there is no `updated_at` update, no trace left in the source table. The pipeline has nothing to read, so the deletion is invisible to it.

This is exactly the gap that the Problem Statement in Activity 1 described — *"2 orders were cancelled and deleted from the system. Your pipeline will never know they existed."*

True **Change Data Capture** (WAL-based) solves this by reading every event from the Postgres transaction log — including DELETE events — before they are lost. In Databricks, this is the **Change data capture** mode in the Ingestion Pipeline, which requires the source to support logical replication (which is why we set up `REPLICA IDENTITY FULL` and a publication in Supabase). When CDC mode is available and enabled, hard deletes are captured and the corresponding rows are removed from the Delta table on the next pipeline run.

**Tags**
- data-engineering / cdc / de-change-data-capture (skill)

### Creating Lakeflow Connect
#### Overview
Set up a live Postgres source on Supabase, prepare the orders_practice table with sample data, and create a Lakeflow Connect ingestion pipeline in Databricks to ingest change data from Postgres into a Delta Streaming Table in Unity Catalog.

#### Level
beginner

#### Industries
- retail-and-cpg

#### Tags
- data-understanding (skill)
- batch-etl (skill)
- databricks (tool)
- sql (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

### The Problem We Are Solving
<br/>

It is 11:00 AM at GlobalMart. In the last hour alone:

- A customer updated their delivery address after placing an order
- 3 new orders arrived from the mobile app
- 2 orders were cancelled and deleted from the system
- 1 order moved from *Processing* to *Shipped*

Your pipeline runs at midnight, **13 hours later**. It loads the entire `orders` table. But the two cancelled orders are already gone from Postgres. Your pipeline will never know they existed.

**Why common approaches fall short:**

| Approach | The gap |
|---|---|
| **Full Load** | Reloads everything every run, misses hard deletes, wastes compute |
| **Incremental Load** | Picks up new/updated rows via `updated_at`, still misses hard deletes |
| **CDC** | Reads every INSERT, UPDATE, DELETE directly from the Postgres transaction log — nothing missed |
<br/>

**Lakeflow Connect is Databricks' managed CDC pipeline.** No code. No custom WAL readers. You configure the source, set a cursor column and primary key, Databricks handles the rest and lands data into a Delta Streaming Table in Unity Catalog.

In this activity, you will set up the Postgres source on Supabase and create your first Lakeflow Connect pipeline.

**Tags**


##### Input 2
**Type:** Text

### Step 1 — Set Up Supabase
<br/>

**Supabase** is a hosted Postgres platform. In this training, it plays the role of GlobalMart's transactional database, the source that Lakeflow Connect will read from.

> 💡 **In a real production environment**, you would never manually insert rows into the orders table. Data flows in automatically the moment a customer places, updates, or cancels an order through the application. We are simulating that source state here by running a script,so you can experience the full CDC pipeline without needing a running application behind it.

---

**1.1 — Create your Supabase account**

1. Go to [supabase.com](https://supabase.com) and click **Start your project**
2. Sign up with your email or GitHub account
3. Verify your email if prompted

---

**1.2 — Create an Organisation**

Once signed in, you will be asked to create an organisation. This is a workspace that groups your projects.

- **Organisation name:** `GlobalMart Training` (or any name you prefer)
- **Type:** Personal

Click **Create organisation**.

---

**1.3 — Create a Project**

Inside your organisation, click **New project** and fill in:

| Field | Value |
|---|---|
| **Project name** | `globalmart-practice` |
| **Database password** | Choose a strong password and **save it immediately** — you will need it when setting up Lakeflow Connect |
| **Region** | Choose the region closest to you (e.g. South Asia (Mumbai)) |
| **Pricing plan** | Free |
<br/>

Click **Create new project**. Supabase will take about **1–2 minutes** to provision your database. Wait for the status to show **Project is ready** before proceeding.

---

**1.4 — Find Your Connection Details**

Once the project is ready, you need your database credentials for the Lakeflow Connect setup later.

Navigate to: **connect -> direct connection string**
![Image-image.png](https://cdn.enqurious.com/images/8f0370bb-1dd3-4d15-a996-d220e58a1761_image.webp)

![Image-image.png](https://cdn.enqurious.com/images/8f9ab3e0-cf60-42ac-987b-135cb477d03f_image.webp)

![Image-image.png](https://cdn.enqurious.com/images/e4819926-5a26-4c7c-ac8e-101719d48a97_image.webp)

Note down the following:

| Field | Where to find it |
|---|---|
| **Host** | Listed as *Host* — looks like `db.xxxxxxxxxxxx.supabase.co` |
| **Port** | `5432` |
| **Database name** | `postgres` |
| **Username** | `postgres` |
| **Password** | The password you set when creating the project or you can reset the password as well |

> ⚠️ The **database name is always `postgres`** in Supabase, this is the actual Postgres database. You will need to enter this exactly when creating the Lakeflow connection in Databricks. Do not confuse it with `public`, which is the schema name.

**Tags**


##### Input 3
**Type:** Text

### Step 2 — Create the orders_practice Table

Watch the video below to see the full setup being done in Supabase — table creation, data insertion, and publication. Then follow the scripts below to do it yourself.

- [Video](https://cdn.enqurious.com/videos/62836c22-fc23-469f-a84b-1ae121fffdaa_supabasetablecreation.mp4)

Navigate to your Supabase project → **SQL Editor** → **New query**. Run the scripts below one section at a time.

---

#### Part A — Create the Table and Audit Trigger

```sql
-- ─────────────────────────────────────────────────
-- Create orders_practice table
-- ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.orders_practice (
    order_id       VARCHAR(20)     PRIMARY KEY,
    customer_id    VARCHAR(20)     NOT NULL,
    order_date     TIMESTAMP       NOT NULL,
    status         VARCHAR(50)     NOT NULL,
    total_amount   DECIMAL(10, 2)  NOT NULL,
    channel        VARCHAR(20)     NOT NULL DEFAULT 'Online',
    updated_at     TIMESTAMP       NOT NULL DEFAULT NOW()
);

-- ─────────────────────────────────────────────────
-- Enable REPLICA IDENTITY FULL
-- Required for CDC to capture the complete row
-- on UPDATE and DELETE events (not just the PK)
-- ─────────────────────────────────────────────────
ALTER TABLE public.orders_practice
    REPLICA IDENTITY FULL;

-- ─────────────────────────────────────────────────
-- Auto-update updated_at whenever a row changes
-- Lakeflow uses this column as the CDC cursor
-- ─────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_orders_practice_updated_at
    BEFORE UPDATE ON public.orders_practice
    FOR EACH ROW
    EXECUTE FUNCTION public.set_updated_at();
```

> **Why `REPLICA IDENTITY FULL`?**
> By default, Postgres only writes the primary key column to the WAL for UPDATE and DELETE events. This means Lakeflow would only know *which row* changed — not *what it changed to*. Setting `REPLICA IDENTITY FULL` tells Postgres to write the entire before-and-after row into the WAL for every change. This gives Lakeflow Connect the complete picture it needs to apply updates correctly into Delta.

Run this query and confirm you see a **Success** message in the Results pane before moving on.

---

#### Part B — Insert Sample Orders (22 rows)

Open a **new SQL Editor tab** and run:

```sql
-- ─────────────────────────────────────────────────
-- Insert 22 sample orders into orders_practice
-- Mix of statuses and channels to simulate
-- a realistic GlobalMart orders dataset
-- ─────────────────────────────────────────────────
INSERT INTO public.orders_practice
    (order_id, customer_id, order_date, status, total_amount, channel, updated_at)
VALUES
    ('ORD-P001', 'CUST-101', '2024-01-05 09:15:00', 'Delivered',   1250.00, 'Online',     NOW()),
    ('ORD-P002', 'CUST-102', '2024-01-08 14:30:00', 'Delivered',    875.50, 'Retail-PoS', NOW()),
    ('ORD-P003', 'CUST-103', '2024-01-10 11:00:00', 'Delivered',   3200.00, 'Online',     NOW()),
    ('ORD-P004', 'CUST-104', '2024-01-12 16:45:00', 'Cancelled',    420.00, 'Online',     NOW()),
    ('ORD-P005', 'CUST-105', '2024-01-15 10:20:00', 'Delivered',   1875.25, 'Retail-PoS', NOW()),
    ('ORD-P006', 'CUST-106', '2024-01-18 09:50:00', 'Delivered',    630.00, 'Online',     NOW()),
    ('ORD-P007', 'CUST-107', '2024-01-20 13:10:00', 'Delivered',   2100.75, 'Online',     NOW()),
    ('ORD-P008', 'CUST-108', '2024-01-22 15:30:00', 'Cancelled',    955.00, 'Retail-PoS', NOW()),
    ('ORD-P009', 'CUST-109', '2024-01-25 10:00:00', 'Delivered',   4500.00, 'Online',     NOW()),
    ('ORD-P010', 'CUST-110', '2024-01-28 11:30:00', 'Shipped',     1320.50, 'Online',     NOW()),
    ('ORD-P011', 'CUST-111', '2024-02-01 09:00:00', 'Shipped',      780.00, 'Retail-PoS', NOW()),
    ('ORD-P012', 'CUST-112', '2024-02-03 14:15:00', 'Shipped',     2250.00, 'Online',     NOW()),
    ('ORD-P013', 'CUST-113', '2024-02-06 10:45:00', 'Shipped',      560.25, 'Online',     NOW()),
    ('ORD-P014', 'CUST-114', '2024-02-08 16:00:00', 'Processing',  1890.00, 'Retail-PoS', NOW()),
    ('ORD-P015', 'CUST-115', '2024-02-10 11:20:00', 'Processing',  3450.00, 'Online',     NOW()),
    ('ORD-P016', 'CUST-116', '2024-02-13 09:30:00', 'Processing',   675.50, 'Online',     NOW()),
    ('ORD-P017', 'CUST-117', '2024-02-15 14:00:00', 'Processing',  1125.00, 'Retail-PoS', NOW()),
    ('ORD-P018', 'CUST-118', '2024-02-18 10:10:00', 'Placed',       890.00, 'Online',     NOW()),
    ('ORD-P019', 'CUST-119', '2024-02-20 13:45:00', 'Placed',      2780.75, 'Online',     NOW()),
    ('ORD-P020', 'CUST-120', '2024-02-22 15:15:00', 'Placed',       445.00, 'Retail-PoS', NOW()),
    ('ORD-P021', 'CUST-101', '2024-02-25 09:45:00', 'Placed',      1560.00, 'Online',     NOW()),
    ('ORD-P022', 'CUST-103', '2024-02-28 11:00:00', 'Placed',       320.50, 'Online',     NOW());
```

**Verify the data was inserted.** Open a new tab and run:

```sql
SELECT * FROM public.orders_practice ORDER BY order_id;
```

You should see **22 rows** with a mix of statuses — Delivered, Shipped, Processing, Placed, and Cancelled.

---

#### Part C — Create a Publication

Open a **new SQL Editor tab** and run:

```sql
-- ─────────────────────────────────────────────────
-- Create a publication for logical replication
-- This is what Lakeflow Connect reads from
-- ─────────────────────────────────────────────────
CREATE PUBLICATION orders_practice_pub
    FOR TABLE public.orders_practice;
```

> **What is a Publication?**
>
> In Postgres, a **publication** is a named object that defines *which tables' changes should be included in the logical replication stream*. Think of it as a subscription list — you tell Postgres "these are the tables I want to broadcast changes for", and any replication tool that connects can subscribe to that broadcast.
>
> Lakeflow Connect uses Postgres logical replication to receive change events (INSERT, UPDATE, DELETE) from your source database. For this to work, a publication must exist for the tables being ingested. Without it, there is no stream to read from.
>
> In production, a single publication can cover multiple tables. Here, we are creating one specifically for `orders_practice` to keep things focused.


**Tags**


##### Input 4
**Type:** File Upload

**Question:** Run `SELECT * FROM public.orders_practice ORDER BY order_id;` in the Supabase SQL Editor and upload a screenshot showing all 22 rows returned. Make sure the column names and row count are visible.

**Max No. of Files:** 2

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- sql (tool)

##### Input 5
**Type:** Text

### Step 3 — Create Lakeflow Connect & Verify in Catalog

Watch the video below. It shows how to create the Lakeflow Connect connection in Databricks using your Supabase credentials.

- [Watch this video](https://cdn.enqurious.com/videos/70d8b5f6-ee7f-4873-b379-d1731968b3b1_lakeflowconnect.mp4)

Once Lakeflow Connect is created, Databricks automatically reflects your Postgres source in the **Catalog Explorer**, you will see a new catalog named after your connection (e.g. `postgres-connection_catalog`) with your Postgres schemas and tables listed inside it.

Navigate to: **Catalog Explorer → `postgres-connection_catalog` → `public`**

You should see `orders_practice` listed as a table, exactly as it exists in your Supabase database.

> This is Lakeflow Connect showing you a live mirror of your Postgres source. The data is not yet in a Delta table, that happens in the next activity when we create the Ingestion Pipeline.

**Tags**


##### Input 6
**Type:** File Upload

**Question:** Upload a screenshot of the Databricks Catalog Explorer showing `orders_practice` listed under your Lakeflow connection catalog (similar to: `postgres-connection_catalog → public → orders_practice`).

**Max No. of Files:** 5

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- databricks / lakehouse-federation (tool)

##### Input 7
**Type:** Short Answer

**Question:** After creating the Lakeflow Connect connection, navigate to the Catalog Explorer in Databricks. Under your connection catalog, which schemas can you see listed alongside `public`? 

**Template:** null

**Tags**
- databricks / lakehouse-federation (tool)

##### Input 8
**Type:** Choice

**Question:** You created a publication using `CREATE PUBLICATION orders_practice_pub FOR TABLE public.orders_practice`. A colleague asks why this step was necessary, can't Lakeflow Connect just read the table directly? What is the correct explanation?

**Options:** 
- A publication is required because Lakeflow Connect cannot connect to Postgres without one

- A publication defines which tables are included in the logical replication stream; without it, there is no change stream for Lakeflow Connect to subscribe to

- A publication improves query performance by caching the table data in memory

- A publication replaces the primary key and is needed for Lakeflow to identify unique rows

**Correct Options:** 
- A publication defines which tables are included in the logical replication stream; without it, there is no change stream for Lakeflow Connect to subscribe to

**Solution:** 
Lakeflow Connect uses **Postgres logical replication** to receive change events, not direct table queries. Logical replication requires a **publication** to be defined, which tells Postgres which tables' changes to include in the replication stream. Without a publication, Postgres does not broadcast changes for that table, and Lakeflow Connect has no stream to subscribe to. A publication is a standard Postgres concept, independent of Databricks, it is the same mechanism used by any Postgres replication tool (e.g. Debezium, AWS DMS).

**Tags**
- databricks / lakehouse-federation (tool)

