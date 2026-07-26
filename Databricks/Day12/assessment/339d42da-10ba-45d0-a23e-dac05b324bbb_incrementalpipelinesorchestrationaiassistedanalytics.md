# Incremental Pipelines, Orchestration & AI-Assisted Analytics
## Content Type
Project

## Overview
Move the GlobalMart supply chain pipeline from a one-time batch load to a production-grade incremental system. You will load only new and changed records through Bronze, Silver, and Gold using Change Data Feed and MERGE, automate the full pipeline using Databricks Workflows with correct task dependencies, and use Genie Code to answer business questions directly from the curated Gold layer,verifying that AI-generated output matches the underlying data.

## Learning Objectives
- Load only new and changed records through the Medallion architecture using Change Data Feed
- Handle schema evolution in an Autoloader pipeline without modifying the existing pipeline or table definition
- Apply SCD1 and SCD2 MERGE logic to incrementally update Silver tables
- Pass environment configuration as job parameters so the same pipeline runs across workspaces without code changes
- Use Genie Code to generate and execute analytical queries on a curated Gold layer and verify the output

## Prerequisites
- Familiarity with Delta Lake, reading, writing, and querying Delta tables
- Understanding of the Medallion architecture, Bronze, Silver, Gold layer roles
- Experience with Autoloader for incremental file ingestion from cloud storage
- Understanding of Change Data Feed, what it tracks and how to enable it
- Basic awareness of Databricks Workflows, tasks and runs

## Duration of Completion
150 minutes

## Level
Intermediate

## Industries
- e-commerce

## Tags
- approach (skill)
- data-understanding (skill)
- data-storage (skill)
- data-quality (skill)
- data-wrangling (skill)
- batch-etl (skill)
- data-modelling (skill)
- databricks (tool)
- spark (tool)
- azure (tool)
- generative-ai (skill)
- ai-engineering (skill)
- data-engineering (skill)

## Scenarios
### Handling Incremental Data
#### Overview
Upgrade the GlobalMart supply chain pipeline to handle incremental data, loading only new and changed records through Bronze, Silver, and the fact table using Change Data Feed and MERGE.

#### Level
intermediate

#### Industries
- e-commerce

#### Tags
- approach (skill)
- data-understanding (skill)
- data-storage (skill)
- data-quality (skill)
- data-wrangling (skill)
- batch-etl (skill)
- data-modelling (skill)
- databricks (tool)
- spark (tool)
- azure (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

**Bold text here**>[!IMPORTANT]
- Your batch pipeline from the previous Assessment must be fully built before starting this activity
- Use the same catalog  and schemas `bronze_as`, `silver_as`, `gold_as`, data loads into the **same tables**, not new ones
- Enable Change Data Feed (CDF) on all Bronze Delta tables **before** uploading the incremental files or triggering the Lakeflow pipeline
- Make your notebooks **parameterized** so the same notebook runs correctly for any batch without hardcoded values

**Tags**


##### Input 2
**Type:** Text

The GlobalMart supply chain pipeline ran successfully for the first batch. Since then:

- The supplier master has grown; new suppliers onboarded, some reactivated
- A new carrier has been added to the network; some reactivated
- New shipments have been dispatched
- 8 existing shipments have progressed in status; 5 that were In Transit are now Delivered, 3 have moved from Dispatched to In Transit
- The source team has also added a new field to the supplier system. This column did not exist in the original batch.

Your task is to load this incremental data through the full pipeline and ensure Bronze, Silver, and the fact table all reflect the latest state.

**Tags**


##### Input 3
**Type:** Text

### Incremental Data Package

>[!NOTE]
> Enable CDF on all Bronze tables before uploading files or triggering the Lakeflow run. Upload the CSV files to the **same ADLS paths** used in Assessment 1. Run the SQL script in Supabase before triggering the Lakeflow pipeline.

| Resource | Description | Download |
|---|---|---|
| `suppliers_inc_02.csv` | 3 supplier records - 2 new, 1 updated. Contains a new column `SupplierRating` not present in the original batch | [Download](https://cdn.enqurious.com/documents/d9225772-ded3-4c9e-92d9-3f45b2e924d2_suppliersinc02.csv) |
| `carriers_inc_02.csv` | 2 carrier records - 1 new, 1 updated | [Download](https://cdn.enqurious.com/documents/b370c751-5e82-45b4-98ab-8eeccec344ee_carriersinc02.csv) |
| `02_shipments_incremental.sql` | Postgres incremental script - 10 new shipments + 8 status updates on existing rows | [Download](https://cdn.enqurious.com/others/04a63d43-7fc3-42bd-8810-f45a055ff894_02shipmentsincremental.sql) |

**Tags**


##### Input 4
**Type:** Text

### Task 1 — Incremental Bronze
<br/>

**Goals**

- Enable Change Data Feed on `bronze_as.suppliers`, `bronze_as.carriers`, and `bronze_as.shipments`
- Upload the supplier and carrier incremental files to ADLS — your existing Autoloader pipeline should detect and ingest only the new files without reprocessing files already loaded
- Run `02_shipments_incremental.sql` in Supabase, then trigger a new Lakeflow pipeline run to pull the new and updated shipment rows into Bronze

**Outcomes**

- CDF enabled on all three Bronze tables
- `bronze_as.suppliers` — 3 new rows added (2 new suppliers + 1 updated record)
- `bronze_as.carriers` — 2 new rows added (1 new carrier + 1 updated record)
- `bronze_as.shipments` — 10 new rows added, 8 existing rows updated


**Tags**


##### Input 5
**Type:** Short Answer

**Question:** You re-run your Autoloader pipeline for suppliers after uploading `suppliers_inc_02.csv` to the same ADLS folder. The pipeline fails immediately with a schema mismatch; the source team added a new column, `SupplierRating`, that did not exist in the original batch.

What single configuration change in your Autoloader notebook resolves this without a manual `ALTER TABLE` or any change to the Bronze table definition?

After applying the fix, describe what `bronze_as.suppliers` looks like; specifically, what value does `SupplierRating` hold for the 10 rows loaded in Assessment 1?

**Template:** null

**Tags**
- data-storage / delta-lakehouse / schema-evolution (skill)

##### Input 6
**Type:** Short Answer

**Question:** Your team's ADLS storage was reorganized overnight. The checkpoint folder and schema location folder for the suppliers Autoloader pipeline were deleted as part of a cleanup job; neither the pipeline nor the notebook was changed.

A teammate re-runs the suppliers Autoloader the next morning without knowing this happened. The ADLS folder now has two files: `suppliers.csv` (original, 10 rows) and `suppliers_inc_02.csv` (3 rows).

Answer the following:

1. What happens to `bronze_as.suppliers` after this run — how many rows does it contain, and why?
2. The schema location was also deleted. `suppliers_inc_02.csv` has a new column `SupplierRating` that `suppliers.csv` does not. What risk does this introduce when Autoloader re-infers the schema from scratch?
3. What is the correct production practice to ensure checkpoint and schema location paths are never accidentally deleted?

**Template:** null

**Tags**
- databricks / autoloaders (tool)
- batch-etl / batch-incremental-load (skill)
- data-storage / delta-lakehouse / schema-evolution (skill)

##### Input 7
**Type:** File Upload

**Question:** Submit the following evidence for Task 1:

- Upload all worked-out notebooks for the bronze layer
- Screenshot of the Lakeflow pipeline run confirming incremental shipments loaded, showing `bronze_as.shipments.`

**Max No. of Files:** 10

**Max File Size:** 10

**Allowed File Types:** ANY

**Tags**
- databricks / autoloaders (tool)
- databricks / lakeflow-connect (tool)
- batch-etl / medallion-architecture (skill)
- data-storage / delta-lakehouse / schema-evolution (skill)

##### Input 8
**Type:** Text

### Task 2 — Incremental Silver
<br/>

**Goals**

- Use CDF to read only the rows that changed in Bronze since your last Silver run — your Silver notebook should not re-scan all of Bronze
- Investigate any new data quality issues in the incremental data and apply the appropriate decision
- MERGE the changed rows into the existing Silver tables: new records insert, updated records overwrite in place along with handling SCD-2

**Outcomes**

- `silver_as.suppliers` — 12 rows (2 new inserted, SUP-04 reactivated record updated)
- `silver_as.carriers` — 11 rows (CAR-11 inserted, CAR-09 reactivated record updated)
- `silver_as.shipments` — 125 rows (10 new inserted, 8 status-changed rows updated)

**Tags**


##### Input 9
**Type:** Short Answer

**Question:** Imagine the CDF output from `bronze_as.suppliers` has 4 rows, but `suppliers_inc_02.csv` only has 3. 

1. What causes this error? Why does MERGE fail when multiple source rows match the same target row?
2. How do you fix it before the MERGE runs? Write the deduplication logic.
3. Which row should you keep when there are duplicates for the same `supplier_id` and why?

**Template:** null

**Tags**
- data-storage / delta-lakehouse / merge-into (skill)

##### Input 10
**Type:** Choice

**Question:** You have already created a Delta table called products to store information about GlobalMart’s product catalog. Now, you want to make changes to the schema definition to enforce a business rule which is:

The column Product_Rating of the table should be between 0 and 5.
Which of the following options would best enforce this business rule in Products table? (Mark all that applies)

**Options:** 
- ALTER TABLE products
ADD CONSTRAINT Product_Rating
CHECK (Product_Rating > 0 AND Product_Rating <= 5);

- ALTER TABLE products
ADD CHECK (Product_Rating >= 0 AND Product_Rating <= 5);

- ALTER TABLE products
ADD CONSTRAINT Product_Rating
CHECK (Product_Rating BETWEEN 0 AND 5);

- ALTER TABLE products
ADD CONSTRAINT Product_Rating
CHECK (Product_Rating >= 0 AND Product_Rating <= 5);

**Correct Options:** 
- ALTER TABLE products
ADD CONSTRAINT Product_Rating
CHECK (Product_Rating BETWEEN 0 AND 5);

- ALTER TABLE products
ADD CONSTRAINT Product_Rating
CHECK (Product_Rating >= 0 AND Product_Rating <= 5);

**Tags**
- data-quality / data-consistency (skill)

##### Input 11
**Type:** Code

**Question:** `carriers_inc_02.csv` reactivates CAR-09 (Ekart) — `IsActive` changes from `N` to `Y`. You used an SCD1 MERGE to update the record in Silver so the latest state always wins.

Now consider a different requirement from the supply chain team: every time a carrier's `ServiceRegion` changes, they need the full history — because shipments are billed based on the region the carrier was assigned to **at the time of dispatch**. A simple overwrite would lose that audit trail.

Write the MERGE code for both scenarios using `gbmart.silver_as.carriers` as the target:

1. **SCD1** — update the carrier record when `IsActive` or any field changes (what you built)
2. **SCD2** — show how the logic changes to preserve history when `ServiceRegion` changes, using `is_current`, `effective_start`, and `effective_end` columns

**Language:** python

**Snippet:** 

**Tags**
- data-storage / delta-lakehouse / merge-into (skill)
- data-modelling / dimensional-modelling / slowly-changing-dimensions (skill)

##### Input 12
**Type:** File Upload

**Question:** Submit the following evidence for Task 2:

- Your updated Silver notebooks for suppliers, carriers, and shipments showing CDF-based incremental reads
- A screenshot showing the CDF output for carriers; confirm only 2 rows were read from Bronze

**Max No. of Files:** 6

**Max File Size:** 10

**Allowed File Types:** ANY

**Tags**
- data-storage / delta-lakehouse / change-data-feed (skill)
- data-quality / data-consistency (skill)
- batch-etl / medallion-architecture (skill)
- data-quality / conformity (skill)

##### Input 13
**Type:** Text

### Task 3 — Refresh Fact Table
<br/>

**Goals**

- Refresh `fact_shipments` to include the 10 new shipments from this batch and reflect the 8 status changes on existing rows
- Verify that `delivery_delay_days` and `is_on_time` are now correctly populated for the 5 shipments that changed from In Transit to Delivered — these metrics were NULL before

**Outcomes**

- 5 rows that previously had NULL delivery metrics now have `delivery_delay_days` and `is_on_time` populated
- `agg_carrier_performance` and `agg_tier_analysis` refreshed

**Tags**


##### Input 14
**Type:** Short Answer

**Question:** SHP-10002 was 'In Transit' in your original `fact_shipments`. Its `delivery_delay_days` and `is_on_time` were NULL because `actual_arrival` had not been filled.

After this incremental run, `silver_as.shipments` shows SHP-10002 as 'Delivered' with `actual_arrival` populated. You re-run your Gold notebook.

Will `delivery_delay_days` and `is_on_time` be correctly updated in `fact_shipments` without any code change? Identify exactly which part of your Gold code causes this to happen automatically.

**Template:** null

**Tags**
- data-storage / delta-lakehouse / merge-into (skill)

##### Input 15
**Type:** File Upload

**Question:** Submit the following evidence for Task 3:

- Your updated Gold notebook showing the fact table refresh
- A screenshot of `fact_shipments` showing rows
- A screenshot showing at least one of the 5 previously-NULL rows now has `delivery_delay_days` and `is_on_time` populated
- Screenshots of refreshed `agg_carrier_performance` and `agg_tier_analysis`

**Max No. of Files:** 5

**Max File Size:** 10

**Allowed File Types:** ANY

**Tags**
- data-wrangling / join (skill)
- data-wrangling / group (skill)
- batch-etl / medallion-architecture (skill)
- data-wrangling / filter (skill)

### Use Genie Code to answer business questions
#### Overview
Use Databricks Genie Code to answer business questions from the GlobalMart supply chain Gold layer, guide the agent to the right tables, verify its output, and understand how context affects the quality of AI-generated analysis.

#### Level
intermediate

#### Industries
- e-commerce

#### Tags
- generative-ai (skill)
- ai-engineering (skill)
- databricks (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

The Gold layer is built, verified, and up to date after batch 03. The logistics team now needs answers from this data, but they do not write SQL.

Rather than handing them a dashboard that requires a SQL Warehouse, you will use **Genie Code**, Databricks' agentic AI that generates and executes code directly in a notebook on your interactive cluster.

Your task is to use Genie Code to answer the logistics team's top business questions from the supply chain Gold layer, verify that its answers are correct, and understand how to guide the agent when it reaches for the wrong table.

**Tags**


##### Input 2
**Type:** Text

### Task — Analyse the Gold Layer with Genie Code

![Image-image.png](https://cdn.enqurious.com/images/edbc11d8-15c2-4536-9aef-da90e5f3c954_image.webp)

**Goals**

- Ask Genie Code to code the three business questions below — reference the correct Gold aggregation table using `@` for each question
- Let Genie Code generate and execute the code, do not write the queries yourself
- After all three questions are answered, ask Genie Code to summarise and interpret the notebook
- Cross-verify at least one answer by writing a manual query in a separate notebook cell

**The three questions to ask Genie Code:**

- Which carrier delivered the most shipments?
- Which carrier has the worst on-time delivery rate?
- How is shipment volume distributed across shipping tiers?

**Outcomes**

- All three questions answered with Genie Code-generated code executed successfully
- Notebook summary generated using the Genie Code summarise command
- At least one answer cross-verified with a manually written query

**Tags**


##### Input 3
**Type:** File Upload

**Question:** Submit the following evidence:
- Screenshot of Genie Code answering one of the three business questions — showing the generated code and the output
- Screenshot of the Genie Code notebook summary (from the summarise command)
- Screenshot of your manual cross-verification query confirming at least one Genie Code answer is correct

**Max No. of Files:** 5

**Max File Size:** 10

**Allowed File Types:** ANY

**Tags**
- databricks / databricks-genie (tool)

### Orchestrating the Pipeline
#### Overview
Automate the GlobalMart supply chain pipeline using Databricks Workflows, wiring task dependencies, passing job parameters, and validating end-to-end execution with a fresh batch of incremental data.

#### Level
intermediate

#### Industries
- e-commerce

#### Tags
- approach (skill)
- batch-etl (skill)
- data-engineering (skill)
- databricks (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

The incremental pipeline works — but it requires running each notebook manually, in the right order, every time new data arrives. That is not production.

GlobalMart's logistics team receives data updates three times a week. The current manual process means a data engineer has to:

- Upload files to ADLS
- Run Bronze notebooks one by one
- Wait for each to finish before starting Silver
- Then run Gold only after all Silver tables are ready

One missed dependency or wrong execution order corrupts the Gold layer silently.

Your task is to automate this entirely using a Databricks Workflow, so the next batch of incremental data flows through Bronze → Silver → Gold in the correct order, without manual intervention.

**Tags**


##### Input 2
**Type:** Text

### Batch 03 Data Package

>[!NOTE]
> Upload the CSV files to the same ADLS paths before triggering the Workflow. Run the SQL script in Supabase first. Once the data is in the source, the Workflow should handle the rest.

| Resource | Description | Download |
|---|---|---|
| `suppliers_inc_03.csv` | 2 supplier records — 1 new, 1 reactivated | [Download](https://cdn.enqurious.com/documents/f9043eb4-f90c-4f29-8fa4-43c805de28bf_suppliersinc03.csv) |
| `carriers_inc_03.csv` | 2 carrier records — 1 new, 1 updated | [Download](https://cdn.enqurious.com/documents/461e5175-9a89-44fe-b98a-4700a73bc0ed_carriersinc03.csv) |
| `03_shipments_incremental.sql` | Postgres incremental script — 5 new shipments + 5 status updates | [Download](https://cdn.enqurious.com/others/725c0303-a1d1-4f52-b72d-d8f637de60f7_03shipmentsincremental.sql) |

**Tags**


##### Input 3
**Type:** Text

### Task — Build and Run the Workflow

**Goals**

- Build a Databricks Workflow that runs all Silver and Gold notebooks in the correct dependency order
- Pass `catalog` and `schema` names as job parameters — no values should be hardcoded inside any notebook
- Upload the batch 03 files to ADLS and run the SQL script in Supabase, then trigger the Workflow
- The Workflow must complete all tasks successfully without manual intervention

**The pipeline dependency order to enforce:**

```
Bronze Suppliers  (Autoloader) ──► Silver Suppliers ──┐
Bronze Carriers   (Autoloader) ──► Silver Carriers  ──┼──► Gold (fact_shipments + agg tables)
Bronze Shipments  (Lakeflow)   ──► Silver Shipments ──┘

```

**Outcomes**

- Databricks Workflow created with all tasks and dependencies correctly wired
- Workflow run completes — all tasks green
- `fact_shipments`, `agg_carrier_performance`, and `agg_tier_analysis` reflect batch 03 data

**Tags**


##### Input 4
**Type:** Choice

**Question:** You are orchestrating a Databricks Job for an ETL pipeline. Why is All-Purpose Compute not recommended?

**Options:** 
- It does not support running scheduled jobs.

- It has lower performance compared to Job Compute.

- It remains active even after job completion, leading to higher costs.

- It does not allow multiple users to collaborate.

**Correct Options:** 
- It remains active even after job completion, leading to higher costs.

**Tags**
- databricks / clusters / all-purpose (tool)

##### Input 5
**Type:** File Upload

**Question:** Submit the following evidence:

- Screenshot of the Workflow DAG view, showing all tasks and their dependencies
- Screenshot of a completed Workflow run, all tasks green
- Screenshot showing job parameters configured on the Workflow (catalog, schema)
- Screenshot of `fact_shipments` row count after the batch 03 run

**Max No. of Files:** 5

**Max File Size:** 10

**Allowed File Types:** ANY

**Tags**
- databricks / workflows (tool)
- data-engineering / orchestration / de-dag-scheduling (skill)

