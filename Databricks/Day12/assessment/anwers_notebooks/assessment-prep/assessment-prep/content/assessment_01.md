---
name: "Assessment 1 — GlobalMart: Building a Supply Chain Medallion Pipeline"
overview: "Build a complete Medallion Data Pipeline for GlobalMart's supply chain domain — ingesting from multiple source types, applying data quality decisions across four tables, and delivering a reporting-ready Star Schema through Bronze, Silver, and Gold layers."
learning_objectives:
  - "Ingest structured data from ADLS Gen2 and Postgres using the correct ingestion method for each source"
  - "Identify and resolve data quality issues across four source tables without step-by-step guidance"
  - "Apply quarantine vs flag decisions based on the downstream impact of each defect"
  - "Design a dimensional model from a business problem statement and build it as a Star Schema in the Gold layer"
prerequisites:
  - "Days 1–9 of the Tredence Databricks DE+AI Advanced program completed"
  - "Access to Databricks workspace with Unity Catalog enabled"
  - "gbmart catalog with bronze_as, silver_as, gold_as schemas already created"
duration_minutes: 120
level: advanced
credit: 50
industries:
  - supply-chain
  - e-commerce
tags:
  - autoloader
  - lakeflow-connect
  - data-quality
  - medallion-architecture
  - dimensional-modelling
  - delta-lake
  - databricks
---

## Input 1

**Type:** Text

>[!IMPORTANT]
> All tables must follow the three-level namespace: `gbmart.<schema>.<table_name>`
> Use `bronze_as` for Bronze, `silver_as` for Silver, `gold_as` for Gold.

GlobalMart has built a trusted pipeline for its core order and product data. The next expansion is the **logistics domain** — tracking which suppliers ship what, via which carrier, at what delivery tier, and whether shipments arrive on time.

The supply chain team needs answers the current Gold layer cannot provide:

- Which carriers miss SLA targets most often?
- Which shipping tier has the highest cost variance against contracted rates?
- Which suppliers have the highest volume of delayed deliveries?

Your task is to build the complete Medallion pipeline for 4 new source tables — from raw ingestion to a reporting layer that can answer these questions.

**Tags:**

- batch-etl / medallion-architecture

---

## Input 2

**Type:** Text

**Goal**

Build the GlobalMart supply chain Medallion pipeline — Bronze → Silver → Gold — for 4 source tables across two ingestion methods.

**Outcomes**

By completing this assessment, you will have:

- Ingested all 4 source tables into `gbmart.bronze_as`
- Cleaned and validated all 4 Silver tables with the appropriate fix, quarantine, or flag decision for each issue found
- Designed a dimensional model for the supply chain domain and documented it
- Built a Star Schema in `gbmart.gold_as` — 3 dimension tables, 1 fact table, 2 pre-aggregated tables
- Verified row counts at every layer transition

**Tags:**

- batch-etl / medallion-architecture

---

## Input 3

**Type:** Text

### Data Package

>[!NOTE]
> Download all resources before starting. Read the **Data Dictionary** and **Data Model** before writing any code.

| Resource | Description | Download |
|---|---|---|
| `suppliers.csv` | 10 supplier records — ADLS source | [Download](PLACEHOLDER_SUPPLIERS_CSV) |
| `shipping_tier.csv` | 5 shipping tier records — ADLS source | [Download](PLACEHOLDER_SHIPPING_TIER_CSV) |
| `carriers.csv` | 10 carrier records — ADLS source | [Download](PLACEHOLDER_CARRIERS_CSV) |
| `01_shipments_setup.sql` | Postgres setup script — run in Supabase SQL Editor to seed the `shipments` table | [Download](PLACEHOLDER_SHIPMENTS_SQL) |
| Data Dictionary | Column definitions, data types, and business rules for all 4 tables | [Download](PLACEHOLDER_DATA_DICTIONARY) |
| Source Data Model | Entity relationships and grain definition for the 4 source tables | [Download](PLACEHOLDER_DATA_MODEL) |
| Star Schema | Gold layer dimensional model — dimension tables, fact table, surrogate keys, and grain | [Download](PLACEHOLDER_STAR_SCHEMA) |

**Tags:**

- batch-etl / medallion-architecture

---

## Input 4

**Type:** Text

### Task 1 — Bronze Layer

**Goals**

- Ingest `suppliers`, `shipping_tier`, and `carriers` into `gbmart.bronze_as` — upload the CSV datasets to ADLS at `/mnt/assessment-raw-data/` and use an ingestion method that handles new files arriving incrementally without manual triggers and adapts to schema changes over time
- Ingest `shipments` into `gbmart.bronze_as` — run the provided SQL script in your Supabase SQL Editor to seed the `shipments` table in Postgres, ensure the data is visible in Unity Catalog, and create a pipeline that handles both the initial load and any new or updated records that arrive over time

**Outcomes**

- All 4 tables created and queryable in `gbmart.bronze_as`

**Tags:**

- autoloader
- lakeflow-connect
- batch-etl / medallion-architecture

---

## Input 5

**Type:** Short Answer

**Question:** GlobalMart's `bronze_as.shipments` table grows by approximately 800 rows per day and currently holds 120 rows. The analytics team always filters by `dispatch_date` when running reconciliation queries and occasionally also filters by `carrier_id`.

Your teammate suggests partitioning the table by `dispatch_date`. What trade-off should they consider before applying this approach, and what alternative would you recommend for this dataset size and query pattern?

**Tags:**

- databricks / delta-lake
- batch-etl / performance-optimisation

---

## Input 6

**Type:** Code

**Question:** The data team wants the Autoloader pipeline to immediately fail and alert if the source team adds a new column to the CSV — rather than silently evolving the schema. Replace `"??"` in the code below with the correct `schemaEvolutionMode` value.

**Language:** python

**Snippet:**

```python
df = (spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "csv")
    .option("cloudFiles.schemaLocation", schema_location)
    .option("cloudFiles.schemaEvolutionMode", "??")
    .option("header", "true")
    .option("inferSchema", "true")
    .load(source_path)
)

df.writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", checkpoint_path) \
    .toTable("gbmart.bronze_as.suppliers")
```

**Tags:**

- autoloader
- batch-etl / schema-evolution

---

## Input 7

**Type:** Short Answer

**Question:** When writing `shipping_tier` to a Delta table, the pipeline fails with:

```
AnalysisException: Attribute name 'Cost (Rs)' contains invalid character(s).
Please use backticks to escape.
```

What caused this error and how did you resolve it in the ingestion code?

**Tags:**

- autoloader
- databricks / delta-lake

---

## Input 8

**Type:** File Upload

**Question:** Submit the following:

- **suppliers, shipping_tier, carriers:** Upload your Bronze ingestion notebook(s)
- **shipments:** Upload screenshots showing —
  - Postgres data is reflected in Unity Catalog
  - Initial load completed with row count confirmed
  - `bronze_as.shipments` table visible and queryable in Unity Catalog
- **Verification:** Upload a screenshot showing all 4 tables queryable in `gbmart.bronze_as`

**Max No. of Files:** 4

**Max File Size:** 10

**Allowed File Types:** ANY

**Tags:**

- autoloader
- lakeflow-connect
- batch-etl / medallion-architecture

---

## Input 9

**Type:** Text

### Task 2 — Silver Layer

Each source table contains data quality issues. Your job is to find them, understand them, and decide how to handle each one.

Do not assume an issue is a defect without investigating it first. Some patterns that look wrong are valid business rules. Some that look clean are silently broken.

For each table, run a DQ scan, investigate each flagged category, and apply one of three decisions:
- **Fix** — correctable programmatically
- **Flag** — keep the row in the clean table, add `_data_note` with a reason
- **Quarantine** — move to a `_quarantine` table only when the defect makes the entire row unusable for downstream

**Outcomes**

- Clean Silver tables written to `gbmart.silver_as` for all 4 sources
- DQ findings documented in each notebook with investigation notes and decision rationale

**Tags:**

- data-quality
- batch-etl / medallion-architecture

---

## Input 10

**Type:** Short Answer

**Question:** List all data quality issues you found across all 4 tables. For each issue, state what you found and what decision you made.

>[!NOTE]
> Things worth checking across any dataset: data type consistency, value formatting, null handling, referential integrity, and logically impossible values. Not all will apply to every table.

Use this template:

```
suppliers:
- Issue:
  Decision (Fix / Flag / Quarantine):

shipping_tier:
- Issue:
  Decision:

carriers:
- Issue:
  Decision:

shipments:
- Issue:
  Decision:
  Quarantined rows:
  Flagged rows:
```

**Tags:**

- data-quality / conformity
- data-quality / missing-values
- data-quality / integrity
- data-quality / data-consistency

---

## Input 11

**Type:** Code

**Question:** After writing your cleaned data to `silver_as.shipments`, you discover that your update script accidentally set `carrier_id = NULL` for all 115 rows — instead of only the 3 orphaned records.

You need to restore the correct `carrier_id` values for the 112 wrongly overwritten rows, but you cannot do a full table restore — it would erase the `_data_note` column you already added.

Write the SQL to:

1. Identify the table version before the bad write
2. Restore only the 112 affected rows using Delta Time Travel — without overwriting the rest of the table

**Language:** sql

**Snippet:**

**Tags:**

- databricks / delta-lake / time-travel

---

## Input 12

**Type:** Short Answer

**Question:** While investigating the `order_items` dataset, you find records where `line_total` is negative. A teammate immediately marks all such rows as data quality errors and sends them to quarantine.

Is this the right call? What would your approach be before making that decision?

**Tags:**

- data-quality / data-consistency
- data-quality / data-validation

---

## Input 13

**Type:** File Upload

**Question:** Upload all Silver layer notebooks (one per table recommended) and a screenshot confirming row counts for each Silver table.

**Max No. of Files:** 7

**Max File Size:** 10

**Allowed File Types:** ANY

**Tags:**

- data-quality / conformity
- data-quality / missing-values
- data-quality / integrity
- data-quality / data-consistency
- batch-etl / medallion-architecture

---

## Input 14

**Type:** Text

### Task 3 — Dimensional Model

The star schema for this domain has been provided in the data package. Download it and study it before answering the questions below or building the Gold layer.

Pay attention to:
- The grain of the fact table — what one row represents
- Which columns are surrogate keys vs natural keys, and why
- How the fact table joins to each dimension
- Which foreign keys allow NULL and why

The questions that follow assess your understanding of why the model is designed the way it is.

**Tags:**

- dimensional-modelling

---

## Input 15

**Type:** Short Answer

**Question:** The ecommerce team shares the `order_items` table with you. It has these columns:

`order_item_id`, `order_id`, `product_id`, `quantity_purchased`, `unit_price`, `discount_amount`, `line_total`

A teammate suggests building `dim_order_items` from this data and adding it to the supply chain star schema. Explain why this would be the wrong modelling decision — and where these columns should actually go.

**Tags:**

- dimensional-modelling / dimension-table-design

---

## Input 16

**Type:** Choice

**Question:** GlobalMart's data team must build the supply chain analytics platform with a 6-month delivery timeline. The logistics team needs to filter by carrier, tier, and supplier. Ten business analysts will query the data primarily through SQL. The source schemas are well-understood and stable. The engineering team has 3 data engineers.

Which data modelling approach best fits this project?

**Options:**

- Kimball star schema — delivers fast, analyst-friendly queries for a well-defined business domain within the project timeline

- Inmon 3NF enterprise warehouse — builds a normalised integration layer first, then query-optimised data marts on top

- Data Vault 2.0 — maximises auditability and handles schema changes through a hub-satellite-link architecture

- Lambda Architecture — processes batch and real-time data simultaneously using separate speed and batch layers

**Correct Options:**

- Kimball star schema — delivers fast, analyst-friendly queries for a well-defined business domain within the project timeline

**Tags:**

- dimensional-modelling / modelling-approaches

---

## Input 17

**Type:** Short Answer

**Question:** The supply chain team informs you that a single shipment can involve multiple carriers — for example, BlueDart handles warehouse-to-hub and Shadowfax handles last-mile delivery. Currently `fact_shipments` has a single `carrier_key` column, which can only reference one carrier per shipment.

How would you redesign the model to handle this many-to-many relationship? Describe: (1) the bridge table you would create and its columns, and (2) how `fact_shipments` would change.

**Tags:**

- dimensional-modelling / bridge-tables

---

## Input 18

**Type:** Short Answer

**Question:** In the star schema provided, `fact_shipments.carrier_key` is designed to allow NULL — while `supplier_key` and `shipping_tier_key` are NOT NULL.

What decision made during the Silver data quality work explains why `carrier_key` must allow NULL in the fact table? What would happen to those shipment rows if you used an INNER JOIN instead?

**Tags:**

- dimensional-modelling

---

## Input 19

**Type:** Text

### Task 4 — Gold Layer

Implement the dimensional model you designed in Task 3 in `gbmart.gold_as`.

- Build all dimension tables using `sha2` for stable surrogate keys, sourced from their corresponding Silver tables
- Build the fact table by joining Silver shipments to your dimensions — use surrogate keys as foreign keys, never the raw operational IDs
- Build two pre-aggregated **Delta tables** (not views) that allow the logistics team to answer the business questions from the problem statement without writing complex joins every time:
  - `agg_carrier_performance` — carrier-level delivery performance, Delivered shipments only
  - `agg_tier_analysis` — tier-level cost and delivery analysis, all shipments

>[!NOTE]
> The fact table requires two derived metrics related to delivery timeliness — how many days a shipment arrived ahead of or behind its committed date, and whether it was considered on time. Both should be NULL for shipments that have not yet been delivered.
> One joining edge case: a small number of shipments reference a carrier that does not exist in the dimension — keep these rows in the fact table with a NULL carrier key rather than dropping them.

**Outcomes**

- All dimension tables, fact table, and both agg tables queryable in `gbmart.gold_as`
- `fact_shipments` contains exactly **115 rows**

**Tags:**

- dimensional-modelling
- batch-etl / medallion-architecture
- data-wrangling / join

---

## Input 20

**Type:** File Upload

**Question:** Upload your completed Gold layer notebooks and a screenshot confirming `fact_shipments` row count and both agg tables in `gbmart.gold_as`.

**Max No. of Files:** 3

**Max File Size:** 10

**Allowed File Types:** ANY

**Tags:**

- dimensional-modelling
- data-wrangling / join
- data-wrangling / data-transformation
- batch-etl / medallion-architecture

---

## Input 21

**Type:** Choice

**Question:** Query `gbmart.gold_as.agg_carrier_performance`. Which carrier handled the highest number of delivered shipments?

**Options:**

- XpressBees

- Amazon Logistics

- Ekart

- Ecom Express

**Correct Options:**

- XpressBees

**Tags:**

- dimensional-modelling
- data-wrangling / group

---

## Input 22

**Type:** Choice

**Question:** Query `gbmart.gold_as.agg_tier_analysis`. How many shipments were assigned to the In-store Pickup shipping tier?

**Options:**

- 28

- 26

- 24

- 20

**Correct Options:**

- 28

**Tags:**

- dimensional-modelling
- data-wrangling / group
- data-wrangling / filter

---

## Input 23

**Type:** Text

>[!CAUTION]
> Please ensure all Gold layer tables are verified and row counts confirmed before submitting. `fact_shipments` must contain exactly 115 rows.

**Tags:**

- batch-etl / medallion-architecture
