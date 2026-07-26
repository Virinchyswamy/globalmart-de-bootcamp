# Assessment 1 — CLAUDE.md
## GlobalMart: Building a Supply Chain Medallion Pipeline

---

## What This Assessment Is

- **Name:** Assessment 1 — Building a Supply Chain Data Pipeline for GlobalMart
- **Scheduled:** Thursday, July 16, 2026 | 2 hours
- **Platform:** Enqurious
- **Program:** Tredence Databricks DE+AI Advanced (15-day)
- **Covers:** Days 1–9 concepts (Bronze → Silver → Gold, Autoloader, Lakeflow Connect, DQ, Star Schema)
- **Working file:** `assessment/content/assessment_01.md`
- **Final exported file:** `assessment/final_buildingasupplychaindatapipelineforglobalmart.md`

---

## Assessment Design Principles (DO NOT VIOLATE)

| Principle | Rule |
|---|---|
| No spoonfeeding | Never list DQ issues, formulas, or exact column names in task descriptions |
| Goals + Outcomes format | Tasks describe WHAT the business needs, not HOW to achieve it |
| No technique names in tasks | Don't say "Autoloader" or "Lakeflow Connect" in Bronze task — describe behaviour |
| No file paths in tasks | Don't give checkpoint paths, schema paths, mount points in task text |
| Business framing for derived columns | Describe as outcomes ("how many days late") not formulas (`datediff(actual, expected)`) |
| Quarantine hint = spoonfeeding | Don't hint what to quarantine — capture in rubric instead |
| MCQs from actual computed values | Only add MCQs after running Gold notebooks and verifying output |
| Overview text must be tool-agnostic | Don't mention Autoloader/Lakeflow/Delta in the overview — those are revealed by doing |

---

## Source Tables (4)

| # | Table | Source | Ingestion Method |
|---|---|---|---|
| 1 | `suppliers` | ADLS Gen2 | Autoloader |
| 2 | `shipping_tier` | ADLS Gen2 | Autoloader |
| 3 | `carriers` | ADLS Gen2 | Autoloader |
| 4 | `shipments` | Postgres (Supabase) | Lakeflow Connect |

**Catalog:** `gbmart` | **Bronze:** `bronze_as` | **Silver:** `silver_as` | **Gold:** `gold_as`

---

## Intentional DQ Issues — Full Decision Log

### suppliers (ADLS)
| Issue | Decision | Note |
|---|---|---|
| SUP-03 invalid email (`supportthompsonent.com` — missing @) | Fix (hardcode) | Business confirmed correct value |
| SUP-06 blank email | Fix → NULL | Acceptable null |
| City `Bangalore` vs `Bengaluru` | Fix → standardize to `Bengaluru` | |
| SUP-04 phone only 7 digits | Flag | Cannot correct without source |
| IsActive mixed Y/N vs True/False | Fix → cast boolean | |
| SUP-05 `\n` inside OfficeAddress | Fix at read time | `multiLine=True` + `escape='"'` |
| OfficeAddress embeds city+pincode | Fix → strip with regex | |
| SUP-08 city mismatch in address | Keep — business decision | Different district, not an error |

**Key Bronze gotcha:** Without `multiLine=True`, SUP-05 splits into 2 rows → 11 rows instead of 10.
**Special char gotcha:** `Cost (Rs)` column → Delta `AnalysisException` → fix with `.withColumnRenamed("Cost (Rs)", "cost_inr")`.

### shipping_tier (ADLS)
| Issue | Decision |
|---|---|
| TierName casing (`EXPRESS`, `overnight`) | Fix → `initcap()` |
| IsAvailableOnline mixed `Yes`/`No` vs `1`/`0` | Fix → cast boolean |

### carriers (ADLS)
| Issue | Decision |
|---|---|
| CarrierType casing (`road`, `AIR`, `air`) | Fix → `initcap()` |
| ServiceRegion inconsistent (`South`, `west india`) | Fix → map to `South India`, `West India`, `North India` |
| NULL ContactEmail (CAR-04, CAR-10) | Keep — optional field |
| NULL IsActive (CAR-10) | Cast NULL → NULL boolean |

### shipments (Postgres / Lakeflow Connect)
| Issue | Decision | Reason |
|---|---|---|
| Column names lowercased by Lakeflow | Fix → rename to snake_case | Lakeflow lowercases all columns |
| ActualArrival < DispatchDate (5 rows) | **QUARANTINE** → `silver_as.shipments_quarantine` | Physically impossible — corrupts SLA metrics |
| Orphaned CarrierID CAR-99 (3 rows) | **FLAG** → `_data_note = 'ORPHANED_CARRIER_ID'` | Row still useful — carrier join handled downstream |
| ShippingCostINR mismatch vs contracted rate (5 rows) | **FLAG** → `_data_note = 'COST_MISMATCH'` | Row still useful for analysis |
| NULL WeightKg (2 rows, In-store Pickup) | Keep — valid business rule | No parcel moved for In-store Pickup |

**Quarantine rule:** Quarantine ONLY when the defect makes the entire row unusable downstream.
- Arrival-before-dispatch = SLA metrics corrupted = quarantine
- Orphaned carrier = row still has supplier, tier, cost, dates = flag, handle with LEFT JOIN in Gold

---

## Row Counts (Verified)

| Layer | Table | Rows | Notes |
|---|---|---|---|
| Bronze | shipments | 120 | Raw from Postgres |
| Silver | shipments | 115 | 5 quarantined (ActualArrival < DispatchDate) |
| Silver | shipments_quarantine | 5 | Impossible arrival dates |
| Gold | fact_shipments | 115 | Matches Silver clean count |
| Gold | dim_supplier | 10 | |
| Gold | dim_carrier | 10 | |
| Gold | dim_shipping_tier | 5 | |
| Gold | agg_carrier_performance | 10 | Delivered shipments only, per carrier |
| Gold | agg_tier_analysis | 5 | All shipments, per tier |

---

## Gold Layer — Star Schema

```
fact_shipments (grain: one row per shipment)
├── shipment_key (surrogate PK — sha2)
├── shipment_id (natural key)
├── order_id
├── supplier_key       → dim_supplier   (INNER JOIN — all shipments have valid supplier)
├── carrier_key        → dim_carrier    (LEFT JOIN — 3 CAR-99 rows get NULL carrier_key)
├── shipping_tier_key  → dim_shipping_tier (INNER JOIN)
├── shipment_status
├── warehouse_city
├── tracking_number
├── dispatch_date / expected_arrival / actual_arrival
├── weight_kg
├── shipping_cost_inr  (measure)
├── delivery_delay_days (datediff actual - expected; NULL if not yet delivered)
└── is_on_time         (actual_arrival <= expected_arrival; NULL if not yet delivered)
```

**Why carrier_key allows NULL:** Silver flagged 3 shipments with CAR-99 (non-existent carrier).
LEFT JOIN in Gold preserves these rows. INNER JOIN would silently drop 3 rows — wrong.
This connects Silver DQ decision → Gold design — tested in Input 18 (short answer).

---

## Verified Agg Table Output (run 2026-07-15)

### agg_carrier_performance (Delivered shipments only)
| carrier_id | carrier_name | total_shipments | avg_delay_days | avg_cost_inr | on_time_pct |
|---|---|---|---|---|---|
| null | null (CAR-99) | 3 | 1.33 | 216.67 | 66.7 |
| CAR-09 | Ekart | 9 | 1.11 | 108.89 | 66.7 |
| CAR-03 | Delhivery | 5 | 0.60 | 130.00 | 60.0 |
| CAR-01 | BlueDart | 4 | 1.50 | 50.00 | 50.0 |
| CAR-02 | DTDC | 4 | 1.00 | 62.50 | 50.0 |
| CAR-07 | XpressBees | 14 | 1.29 | 168.57 | 50.0 |
| CAR-10 | Rivigo | 5 | 2.20 | 130.00 | 40.0 |
| CAR-05 | Ecom Express | 8 | 1.63 | 268.75 | 25.0 |
| CAR-04 | FedEx India | 9 | 2.33 | 102.78 | 22.2 |
| CAR-06 | Shadowfax | 8 | 2.38 | 150.00 | 12.5 |
| CAR-08 | Amazon Logistics | 12 | 2.42 | 104.17 | 8.3 |

### agg_tier_analysis (All shipments)
| shipping_tier_id | tier_name | total_shipments | tier_cost_inr | avg_actual_cost_inr | on_time_pct_delivered |
|---|---|---|---|---|---|
| SHP-004 | In-store Pickup | 28 | 0 | 0.00 | 37.5 |
| SHP-001 | Standard | 26 | 100 | 98.46 | 35.3 |
| SHP-002 | Express | 24 | 200 | 200.00 | 50.0 |
| SHP-003 | Overnight | 20 | 450 | 461.25 | 50.0 |
| SHP-005 | Local Delivery | 17 | 50 | 48.82 | 28.6 |

**MCQ answers (do not change options without re-running notebooks):**
- Input 17: XpressBees (14 delivered shipments — highest)
- Input 18: 28 (In-store Pickup total_shipments)

---

## Assessment Input Map (Final — 19 inputs on platform)

| Input | Type | Content | Key |
|---|---|---|---|
| 1 | Text | Problem statement — 3 business questions | Context |
| 2 | Text | Goal + Outcomes for full assessment | Scope |
| 3 | Text | Data package downloads (6 resources) | Resources |
| 4 | Text | Task 1 — Bronze Layer (Goals + Outcomes) | Bronze task |
| 5 | Short Answer | Autoloader `schemaEvolutionMode` fill-in | Code concept |
| 6 | Short Answer | `Cost (Rs)` special character error fix | Code concept |
| 7 | File Upload | Bronze notebooks + Lakeflow screenshots | Bronze submission |
| 8 | Text | Task 2 — Silver Layer | Silver task |
| 9 | Short Answer | DQ findings template — all 4 tables | Silver findings |
| 10 | Code | Delta Time Travel targeted restore (112 rows) | Delta concept |
| 11 | Short Answer | negative line_total — quarantine vs investigate | DQ reasoning |
| 12 | File Upload | Silver notebooks | Silver submission |
| 13 | Text | Task 3 — Dimensional Model (star schema provided) | Gold context |
| 14 | Short Answer | dim_order_items wrong decision — where should it go? | Modelling concept |
| 15 | Choice | Kimball vs Inmon vs Data Vault vs Lambda | Modelling approach |
| 16 | Text | Task 4 — Gold Layer (implement the model) | Gold task |
| 17 | Choice | MCQ: which carrier had most delivered shipments? | Pipeline validation |
| 18 | Choice | MCQ: how many shipments in In-store Pickup tier? | Pipeline validation |
| 19 | File Upload | Gold notebooks + fact_shipments row count screenshot | Gold submission |

---

## Platform Issues Fixed vs Still Open

### Fixed in this session
| Issue | Fix |
|---|---|
| Overview mentioned tool names (Autoloader, Lakeflow) | Rewritten to be tool-agnostic |
| Gold task said "views" for agg tables | Changed to "Delta tables" (not views) |
| Silver task said only "Fix or Quarantine" — missing Flag | Must still fix on platform (see below) |
| Bronze task listed techniques directly | Rewritten to Goals + Outcomes |
| Gold task listed every fact column explicitly | Removed — learner implements from star schema |
| MCQs had PLACEHOLDER correct answers | Replaced with actual verified values |

### Still needs fixing on platform
| Item | Action needed |
|---|---|
| **Input 8 (Silver task)** — says "Fix or Quarantine" | Add **Flag** as third decision on platform |
| **6 PLACEHOLDER download URLs** | Upload files, replace with real CDN URLs |
| **PLACEHOLDER_STAR_SCHEMA** | Upload `assessment/dataset/gold_star_schema.xlsx` |

---

## Dataset Files

```
assessment/
├── content/
│   └── assessment_01.md          — working source file (22 inputs, full YAML)
├── final_buildingasupply...md    — exported from platform (19 inputs, platform format)
├── dataset/
│   ├── adls/
│   │   ├── suppliers.csv         (10 rows)
│   │   ├── shipping_tier.csv     (5 rows — Cost (Rs) col name issue)
│   │   └── carriers.csv          (10 rows)
│   ├── postgres/
│   │   └── 01_shipments_setup.sql (120 rows with DQ issues)
│   ├── data_dictionary.xlsx      (2 sheets: Source Tables + Gold Schema)
│   ├── supply_chain_data_model.dbml (source tables DBML for dbdiagram.io)
│   └── gold_star_schema.xlsx     (star schema for learner download)
└── notebooks/
    ├── 00_mount_storage.ipynb
    ├── 01_bronze_layer_autoloader.ipynb
    ├── 02_silver_suppliers.ipynb
    ├── 03_silver_shipping_tier.ipynb
    ├── 04_silver_carriers.ipynb
    ├── 05_silver_shipments.ipynb
    ├── 06_gold_dim_tables.ipynb
    └── 07_gold_fact_and_agg.ipynb
```

---

## Assessment Rubric Notes (to build separately)

Key criteria where learner reasoning matters most:

| Criterion | What to look for |
|---|---|
| Quarantine decision | Only `ActualArrival < DispatchDate` rows should be quarantined — not CAR-99, not cost mismatch |
| Flag decision | CAR-99 (3 rows) and cost mismatch (5 rows) should be flagged with `_data_note`, not quarantined |
| NULL WeightKg | Should NOT be treated as a DQ issue — valid for In-store Pickup |
| CarrierID LEFT JOIN | Learner must explain why LEFT JOIN is used — preserves 3 CAR-99 rows in fact table |
| Silver → Gold connection | Input 18 short answer tests whether learner connects Silver flag → Gold NULL carrier_key |
| `delivery_delay_days` sign | Positive = late, negative = early — many learners reverse this |
| SUP-05 multiLine | Without `multiLine=True`, suppliers table has 11 rows not 10 |
