# Building a Supply Chain Data Pipeline for GlobalMart
## Content Type
Scenario

## Overview
<p style="text-align:justify;">
Build a complete Medallion Data Pipeline for GlobalMart's supply chain domain, ingesting from multiple source types, applying data quality decisions across four tables, and delivering a reporting-ready Star Schema through Bronze, Silver, and Gold layers.

## Learning Objectives
- Ingest structured data from ADLS Gen2 and Postgres using the correct ingestion method for each source
- Identify and resolve data quality issues across four source tables without step-by-step guidance
- Apply quarantine vs flag decisions based on the downstream impact of each defect
- Design a dimensional model from a business problem statement and build it as a Star Schema in the Gold layer

## Prerequisites
- Familiarity with Medallion Architecture
- Familiarity with Pyspark

## Duration of Completion
120 minutes

## Level
Intermediate

## Industries
- e-commerce

## Tags
- approach (skill)
- quality (skill)
- data-understanding (skill)
- data-storage (skill)
- data-modelling (skill)
- data-quality (skill)
- data-wrangling (skill)
- batch-etl (skill)
- databricks (tool)

#### Overview
<p style="text-align:justify;">
Build a complete Medallion Data Pipeline for GlobalMart's supply chain domain, ingesting from multiple source types, applying data quality decisions across four tables, and delivering a reporting-ready Star Schema through Bronze, Silver, and Gold layers.

#### Level
intermediate

#### Industries
- e-commerce

#### Tags
- approach (skill)
- quality (skill)
- data-understanding (skill)
- data-storage (skill)
- data-modelling (skill)
- data-quality (skill)
- data-wrangling (skill)
- batch-etl (skill)
- databricks (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

>[!IMPORTANT]
> All tables must follow the three-level namespace: 

- <your_catalog_name>.<your_schema>.<table_name>
- Use these schemas: `bronze_as` for Bronze, `silver_as` for Silver, `gold_as` for Gold.

GlobalMart has built a trusted pipeline for its core order and product data. The next expansion is the **logistics domain**, tracking which suppliers ship what, via which carrier, at what delivery tier, and whether shipments arrive on time.

The supply chain team needs answers the current Gold layer cannot provide:

- Which carriers miss SLA targets most often?
- Which shipping tier has the highest cost variance against contracted rates?
- Which suppliers have the highest volume of delayed deliveries?

Your task is to build the complete Medallion pipeline for 4 new source tables, from raw ingestion to a reporting layer that can answer these questions.

**Tags**


##### Input 2
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

**Tags**


##### Input 3
**Type:** Text

### Data Package
<br/>

>[!NOTE]
> Download all resources before starting. Read the Data Dictionary and Data Model before writing any code.

| Resource | Description | Download |
|---|---|---|
| `suppliers.csv` | 10 supplier records — ADLS source | [Download](https://cdn.enqurious.com/documents/9d3356af-37fd-4341-aa02-ba76c9bdf443_suppliers.csv) |
| `shipping_tier.csv` | 5 shipping tier records — ADLS source | [Download](https://cdn.enqurious.com/documents/d19ba259-10b2-43b3-b93b-052e3d0a3bec_shippingtier.csv) |
| `carriers.csv` | 10 carrier records — ADLS source | [Download](https://cdn.enqurious.com/documents/4ff3d751-7a1a-47ce-9f95-d6b80b049a85_carriers.csv) |
| `01_shipments_setup.sql` | Postgres setup script — run in Supabase SQL Editor to seed the `shipments` table | [Download](https://cdn.enqurious.com/others/947385fb-d506-4226-897b-2ecc1e818a1c_01shipmentssetup.sql) |
| Data Dictionary | Column definitions, data types, and business rules for all 4 tables | [Download](https://cdn.enqurious.com/others/65cc8754-fde5-40d1-bb18-3c2c2120549c_datadictionary.xlsx) |
| Data Model | Supply chain star schema — entity relationships and grain definition | [Download](https://cdn.enqurious.com/images/87d78fb9-ba3b-43c9-be7b-8f898490e480_Globalmart_OLTP.webp) |
| Star Schema | Gold layer dimensional model — dimension tables, fact table, surrogate keys, and grain | [Download](https://cdn.enqurious.com/others/3a358982-8e40-4eef-a3a4-7f8cf5391d59_goldstarschema.xlsx) |


**Tags**


##### Input 4
**Type:** Text

### Task 1 — Bronze Layer
<br/>

**Goals**

- Ingest `suppliers`, `shipping_tier`, and `carriers` into `gbmart.bronze_as`, upload the CSV datasets to ADLS  
- Use an ingestion method that handles new files arriving incrementally without manual triggers and adapts to schema changes over time
- Ingest `shipments` into `gbmart.bronze_as`, run the provided SQL script in your Supabase SQL Editor to seed the `shipments` table in Postgres, 
- Ensure the data is visible in Unity Catalog, and create a pipeline that handles both the initial load and any new or updated records that arrive over time

**Outcomes**

- All 4 tables created and queryable in `gbmart.bronze_as`

**Tags**


##### Input 5
**Type:** Short Answer

**Question:** The data team wants the Autoloader pipeline to immediately fail and alert if the source team adds a new column to the CSV — rather than silently evolving the schema. Replace `"??"` in the code below with the correct `schemaEvolutionMode` value.

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

**Template:** <p>Write the correct code:</p><pre><code class="language-python">&nbsp;</code></pre>

**Tags**
- data-storage / delta-lakehouse / schema-evolution (skill)

##### Input 6
**Type:** Short Answer

**Question:** When writing `shipping_tier` to a Delta table, the pipeline fails with:
```
AnalysisException: Attribute name 'Cost (Rs)' contains invalid character(s).
Please use backticks to escape.
```

What caused this error and how did you resolve it in the ingestion code?

**Template:** <p>Code:</p><pre><code class="language-python">&nbsp;</code></pre>

**Tags**
- databricks / ingestion-and-parsing (tool)

##### Input 7
**Type:** File Upload

**Question:** 
**Question:** Submit the following:

- **suppliers, shipping_tier, carriers:** Upload your Bronze ingestion notebook(s)
- **shipments:** Upload screenshots showing —
  - Postgres data is reflected in Unity Catalog
  - Initial load completed with row count confirmed
  - `bronze_as.shipments` table visible and queryable in Unity Catalog
- **Verification:** Upload a screenshot showing all 4 tables in `gbmart.bronze_as`

**Max No. of Files:** 10

**Max File Size:** 10

**Allowed File Types:** ANY

**Tags**
- databricks / autoloaders (tool)
- databricks / ingestion-pipeline (tool)
- databricks / lakeflow-connect (tool)

##### Input 8
**Type:** Text

### Task 2 — Silver Layer
<br/>

Each source table contains data quality issues. Your job is to find them, understand them, and decide how to handle each one.

Do not assume an issue is a defect without investigating it first. Some patterns that look wrong are valid business rules. Some that look clean are silently broken.

For each table, run a DQ scan, investigate each flagged category, and apply one of two decisions:
- **Fix** — correctable programmatically
- **Quarantine** — move to a `_quarantine` table only when the defect makes the entire row unusable for downstream

**Outcomes**

- Clean Silver tables written to `gbmart.silver_as` for all 4 sources
- DQ findings documented in each notebook with investigation notes and decision rationale

**Tags**


##### Input 9
**Type:** Short Answer

**Question:** List all data quality issues you found across all 4 tables. For each issue, state what you found and what decision you made.

>[!NOTE]
> Things worth checking across any dataset: data type consistency, value formatting, null handling, referential integrity, and logically impossible values. Not all will apply to every table.

**Template:** <p><span style="color:#1e293b;">suppliers:</span></p><p><span style="color:#1e293b;">- Issue:</span></p><p><span style="color:#1e293b;">&nbsp; Decision (Fix / Flag / Quarantine):</span></p><p><br>&nbsp;</p><p><span style="color:#1e293b;">shipping_tier:</span></p><p><span style="color:#1e293b;">- Issue:</span></p><p><span style="color:#1e293b;">&nbsp; Decision:</span></p><p><br>&nbsp;</p><p><span style="color:#1e293b;">carriers:</span></p><p><span style="color:#1e293b;">- Issue:</span></p><p><span style="color:#1e293b;">&nbsp; Decision:</span></p><p><br>&nbsp;</p><p><span style="color:#1e293b;">shipments:</span></p><p><span style="color:#1e293b;">- Issue:</span></p><p><span style="color:#1e293b;">&nbsp; Decision:</span></p><p><span style="color:#1e293b;">```</span></p><p>&nbsp;</p><p><span style="color:#1e293b;">Where did you find quarantined rows?</span></p>

**Tags**
- data-quality / missing-values (skill)
- data-quality / conformity (skill)
- data-quality / integrity (skill)
- data-quality / data-consistency (skill)

##### Input 10
**Type:** Code

**Question:** After writing your cleaned data to `silver_as.shipments`, you discover that your update script accidentally set `carrier_id = NULL` for all 115 rows, instead of only the 3 orphaned records.

You need to restore the correct `carrier_id` values for the 112 wrongly overwritten rows, but you cannot do a full table restore; it would erase the `_data_note` column you already added.

Write the SQL to:

1. Identify the table version before the bad write
2. Restore only the 112 affected rows using Delta Time Travel, without overwriting the rest of the table

**Language:** sql

**Snippet:** 

**Tags**
- data-storage / delta-lakehouse / time-travel (skill)

##### Input 11
**Type:** Short Answer

**Question:** While investigating the `order_items` dataset, you find records where `line_total` is negative. A teammate immediately marks all such rows as data quality errors and sends them to quarantine.

Is this the right call? What would your approach be before making that decision?

**Template:** null

**Tags**
- data-quality / data-validation (skill)
- data-quality / data-consistency (skill)

##### Input 12
**Type:** File Upload

**Question:** Upload all Silver layer notebooks (one per table recommended) 

**Max No. of Files:** 10

**Max File Size:** 10

**Allowed File Types:** ANY

**Tags**
- batch-etl / medallion-architecture (skill)

##### Input 13
**Type:** Text

The star schema for this domain has been provided in the data package. Download it and study it before answering the questions below or building the Gold layer.

Pay attention to:
- The grain of the fact table — what one row represents
- Which columns are surrogate keys vs natural keys, and why
- How the fact table joins to each dimension
- Which foreign keys allow NULL and why

The questions that follow assess your understanding of why the model is designed the way it is.

**Tags**


##### Input 14
**Type:** Short Answer

**Question:** The ecommerce team shares the `order_items` table with you. It has these columns:

`order_item_id`, `order_id`, `product_id`, `quantity_purchased`, `unit_price`, `discount_amount`, `line_total`

A teammate suggests building `dim_order_items` from this data and adding it to the supply chain star schema. Explain why this would be the wrong modelling decision, and where these columns should actually go.

**Template:** null

**Tags**
- data-modelling / dimensional-modelling / dimension-table-design (skill)

##### Input 15
**Type:** Choice

**Question:** GlobalMart's data team must build the supply chain analytics platform with a 6-month delivery timeline. The logistics team needs to filter by carrier, tier, and supplier. Ten business analysts will query the data primarily through SQL. The source schemas are well-understood and stable. The engineering team has 3 data engineers.

**Options:** 
- Kimball star schema delivers fast, analyst-friendly queries for a well-defined business domain within the project timeline

- Inmon 3NF enterprise warehouse builds a normalised integration layer first, then query-optimised data marts on top

- Data Vault 2.0 maximises auditability and handles schema changes through a hub-satellite-link architecture

- Lambda Architecture processes batch and real-time data simultaneously using separate speed and batch layers

**Correct Options:** 
- Kimball star schema delivers fast, analyst-friendly queries for a well-defined business domain within the project timeline

**Tags**
- data-modelling / dimensional-modelling / dimension-table-design (skill)

##### Input 16
**Type:** Text

### Task 4 — Gold Layer

Implement the dimensional model you designed in Task 3 in `gbmart.gold_as`.

- Build all dimension tables sourced from their corresponding Silver tables
- Build the fact table by joining Silver shipments to your dimensions
- Build both pre-aggregated facts(**views**)that allow the logistics team to answer the business questions from the problem statement without writing complex joins every time:
  - `agg_carrier_performance` — carrier-level delivery performance, Delivered shipments only
  - `agg_tier_analysis` — tier-level cost and delivery analysis, all shipments

>[!NOTE]
> The fact table requires two derived metrics related to delivery timeliness — how many days a shipment arrived ahead of or behind its committed date, and whether it was considered on time. Both should be NULL for shipments that have not yet been delivered.
> One joining edge case: a small number of shipments reference a carrier that does not exist in the dimension — keep these rows in the fact table with a NULL carrier key rather than dropping them.

**Outcomes**

- All dimension tables, fact table, and both agg tables queryable in `gbmart.gold_as`

**Tags**


##### Input 17
**Type:** Choice

**Question:** Query `gbmart.gold_as.agg_carrier_performance`. Which carrier handled the highest number of delivered shipments?

**Options:** 
- XpressBees

- Ekart

- Ecom Express

- Amazon Logistics

- none of the above

**Correct Options:** 
- XpressBees

**Tags**
- data-wrangling / group (skill)

##### Input 18
**Type:** Choice

**Question:** Query `gbmart.gold_as.agg_tier_analysis`. How many shipments were assigned to the In-store Pickup shipping tier?

**Options:** 
- 28

- 26

- 20

- 24

- none of the above

**Correct Options:** 
- 28

**Tags**
- data-wrangling / group (skill)
- data-wrangling / filter (skill)

##### Input 19
**Type:** File Upload

**Question:** Upload your completed Gold layer notebooks covering`fact_shipments` and both agg views in `gbmart.gold_as`.

**Max No. of Files:** 3

**Max File Size:** 10

**Allowed File Types:** ANY

**Tags**
- data-wrangling / join (skill)
- batch-etl / medallion-architecture (skill)
- data-modelling / dimensional-modelling / fact-table-design (skill)

