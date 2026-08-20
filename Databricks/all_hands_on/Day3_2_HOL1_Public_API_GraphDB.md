---
name: Day 3 HOL 1 — Public API + GraphDB Exploration
content_type: Scenario
overview: This hands-on is a side-exploration, not part of GlobalMart's real Bronze/Silver/Gold pipeline (which only ever ingests via Postgres CDC and ADLS Autoloader). Here you practice two ingestion patterns you will meet on other projects — pulling from a public REST API across multiple parameters, and building/querying a small graph database — using GlobalMart-shaped data as a familiar backdrop. You will extend a REST API call to handle multiple currencies and historical dates, create a free Neo4j AuraDB graph database and import a small Customer→Order→Product→Supplier graph into it, then connect to that graph from Databricks and land query results as Delta tables.
learning_objectives:
  - Extend a REST API ingestion pattern to handle multiple parameters (multiple base currencies) and historical/incremental pulls
  - Choose the correct Delta write mode (overwrite vs. append) for a snapshot table versus an accumulating history table
  - Create a free Neo4j AuraDB graph database instance and import data into it from CSV files
  - Write Cypher queries to traverse relationships in a graph database
  - Connect to an external graph database from a Databricks notebook and land query results as a Delta table
prerequisites:
  - A Databricks workspace with a working Unity Catalog External Location (Day 2 HOL 1)
  - Completed Day 3 ILT 1 — API Ingestion Mechanics (REST/HTTP) & Intro to GraphDB/Cypher Basics
duration: 120 minutes
level: Intermediate
industries:
  - e-commerce
tags:
  - databricks (tool)
  - spark (tool)
  - data-ingestion / api (skill)
  - data-ingestion / graph-database (skill)
---

---

## Scenario 1 — REST API: Beyond a Single Call

**Overview:** This is a side-exploration, not part of GlobalMart's real pipeline — GlobalMart's actual Bronze layer only ever ingests via Postgres CDC and ADLS Autoloader, never a live REST API. ILT 1 called `https://api.frankfurter.app/latest` once, for a single default base currency, and saved the result to a sandbox Delta table. Here you extend that same pattern two realistic ways: pulling rates for multiple base currencies GlobalMart actually sells in (USD, EUR, GBP), and pulling historical rates for specific past dates instead of only "right now."

**Outcome:** Two sandbox Delta tables — `fx_rates_multi_base` (one row set per base currency) and `fx_rates_historical` (rates for two specific past dates, accumulated with append mode).

---

## Input 1

**Type:** Text

### Setup

>[!IMPORTANT]
>Nothing in this hands-on feeds Bronze, Silver, or Gold, or `fact_sales`. You are practicing two ingestion *patterns* (REST API, graph database) that show up on other projects — GlobalMart is just a familiar backdrop.

In your notebook, set up the same Unity Catalog External Location path from ILT 1 — no storage key needed, since your cluster already has access via the External Location's Managed Identity (set up in Day 2 HOL 1):

```python
# ─── Setup: same Unity Catalog External Location as ILT 1 ─────────────────────
# HOW TO GET THIS VALUE: the External Location you created in Day 2 HOL 1 —
# Catalog (left sidebar) → External Locations → your location → copy its path.
EXTERNAL_LOCATION = "abfss://YOUR_CONTAINER@YOUR_STORAGE_ACCOUNT.dfs.core.windows.net"  # ← replace
sandbox_path = f"{EXTERNAL_LOCATION}/sandbox/api_graphdb"
print(f"Sandbox path: {sandbox_path}")
```

Now pull FX rates for the three currencies GlobalMart actually sells in — one API call per currency, combined into a single DataFrame:

```python
import requests
from pyspark.sql import Row
from datetime import datetime

base_currencies = ["USD", "EUR", "GBP"]  # GlobalMart's three storefront currencies
all_rows = []

for base in base_currencies:
    response = requests.get("https://api.frankfurter.app/latest", params={"base": base})
    if response.status_code != 200:
        # Don't silently skip a failed call — a DE pipeline should always know
        # when a source didn't return what was expected.
        raise RuntimeError(f"API call failed for base={base}: {response.status_code}")

    data = response.json()
    for currency, rate in data["rates"].items():
        all_rows.append(Row(
            base_currency   = data["base"],
            target_currency = currency,
            exchange_rate   = float(rate),
            rate_date       = data["date"],
            ingested_at     = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        ))

multi_base_df = spark.createDataFrame(all_rows)
print(f"Total rows across {len(base_currencies)} base currencies: {multi_base_df.count()}")
```

Save it — `overwrite` is correct here, since this is a live snapshot, not something to accumulate duplicate-but-stale rows for:

```python
multi_base_df.write.format("delta").mode("overwrite").save(f"{sandbox_path}/fx_rates_multi_base")

saved = spark.read.format("delta").load(f"{sandbox_path}/fx_rates_multi_base")
print(f"Saved {saved.count()} rows to {sandbox_path}/fx_rates_multi_base")
```

---

## Input 2

**Type:** Code

**Question:** GlobalMart also wants to know what a currency's rate was on specific past dates, not just right now — frankfurter.app supports this by accepting a date in place of "latest" in the URL (e.g. `https://api.frankfurter.app/2026-01-01`). Using PySpark, pull EUR-base rates for both `2026-01-01` and `2026-02-01`, and build a table where each row records both the date you requested and the date the API actually returned (the API may adjust to the nearest business day on a weekend/holiday). Append your result into a table that will keep growing every time this runs, rather than replacing it.

**Language:** python

**Snippet:**
```python
historical_dates = ["2026-01-01", "2026-02-01"]
historical_rows  = []

for requested_date in historical_dates:
    # your code here
    pass

historical_df = spark.createDataFrame(historical_rows)
# your write code here
```

**Solution:**
```python
historical_dates = ["2026-01-01", "2026-02-01"]
historical_rows  = []

for requested_date in historical_dates:
    api_url = f"https://api.frankfurter.app/{requested_date}"
    response = requests.get(api_url)

    if response.status_code != 200:
        raise RuntimeError(f"API call failed for {requested_date}: {response.status_code}")

    data = response.json()
    for currency, rate in data["rates"].items():
        historical_rows.append(Row(
            base_currency     = data["base"],
            target_currency   = currency,
            exchange_rate     = float(rate),
            requested_date    = requested_date,     # what we asked for
            api_returned_date = data["date"],        # what we actually got
            ingested_at       = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        ))

historical_df = spark.createDataFrame(historical_rows)

historical_df.write.format("delta").mode("append").save(f"{sandbox_path}/fx_rates_historical")
```
Building the URL with the requested date directly in the path (instead of `"latest"`) is the only change needed to pull historical rates — the rest of the loop-and-collect pattern is identical to Input 1. `append` mode (not `overwrite`) is what makes this table accumulate history across runs instead of replacing it each time. Recording both `requested_date` and `api_returned_date` as separate columns matters because frankfurter.app silently substitutes the nearest earlier business day when the requested date falls on a weekend or holiday — without both columns, that substitution would be invisible.

**Tags**
- spark (tool)
- data-ingestion / api (skill)
- data-storage (skill)

---

## Input 3

**Type:** Choice

**Question:** You want `fx_rates_historical` to keep growing every time this notebook runs, without deleting rates you already pulled on a previous run. Which write mode should the historical table use?

**Options:**
- `df.write.mode("overwrite").format("delta").save(path)`
- `df.write.mode("append").format("delta").save(path)`
- `df.write.mode("replace").format("delta").save(path)`
- `df.write.mode("insert").format("delta").save(path)`

**Correct Options:**
- `df.write.mode("append").format("delta").save(path)`

**Solution:**
`overwrite` deletes everything at the destination path before writing fresh data — correct for `fx_rates_multi_base`, which is always a current snapshot. `append` adds new rows on top of whatever is already there, which is what a growing history table needs. `replace` and `insert` are not real Delta write modes.

**Tags**
- data-storage (skill)
- approach (skill)

---

## Input 4

**Type:** File Upload

**Question:** Take a screenshot of your notebook output showing the row count printed after saving `fx_rates_historical`, across both runs of the loop (both requested dates). Upload it here.

**Max No. of Files:** 1

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- databricks (tool)

---

## Scenario 2 — GraphDB: Build a Small GlobalMart Graph

**Overview:** This is a side-exploration, not part of GlobalMart's real pipeline — nothing here touches Bronze/Silver/Gold or `fact_sales`. Graph databases model data as nodes (entities) and relationships between them, which is a natural fit for questions like "which supplier ultimately fulfilled this customer's order?" — a chain of connections rather than a single flat table. In this scenario you will create a free Neo4j AuraDB instance and load a small GlobalMart-shaped graph into it: 3 customers, 2 suppliers, 3 products, and 3 orders, connected by `PLACED`, `CONTAINS`, and `SUPPLIED_BY` relationships — built from 4 CSV files using Neo4j's no-code Data Importer, the way you would actually receive graph data on a real project.

**Outcome:** A running Neo4j AuraDB Free instance containing 11 nodes and 9 relationships, verified by running Cypher queries directly in the Neo4j Browser.

---

## Input 5

**Type:** Text

### Step 1 — Create your free Neo4j AuraDB account and instance

You don't have a GraphDB account yet — here is exactly how to get one and end up with real, usable credentials.

1. Go to **neo4j.com/cloud/aura** and click **Start Free** — sign up with email or Google/GitHub (no credit card required for the Free tier).
2. Once logged in, you land on the **Aura Console**. Click **Create instance** (or **New Instance**).
3. Choose **AuraDB Free**.
4. Give it a name, e.g. `globalmart-graph-demo`.
5. Click **Create instance**. A dialog immediately shows you three values — **this is the only time the password is ever shown**:
   ```
   Connection URI : neo4j+s://xxxxxxxx.databases.neo4j.io
   Username       : neo4j
   Password       : <a long generated string>
   ```
   Click **Download credentials** or copy all three into a notes file right now. If you lose the password, you cannot recover it — you would have to reset it from the instance's **...** menu → **Reset password**.
6. Wait ~1–2 minutes for the instance status to go from "Creating" to **Running**.
7. Click **Open** on the instance card — this launches the **Neo4j Browser**, a web UI where you can run Cypher directly. Keep this tab open; you will come back to it.

>[!IMPORTANT]
>These 3 values are real, per-account credentials. Never paste them into a shared document, a Slack message, or this hands-on. You will use them locally in your own notebook in Scenario 3 — and you must swap them back to placeholders before submitting anything.

---

## Input 6

**Type:** Text

### Step 2 — Prepare the 4 CSV files you'll upload

Instead of typing Cypher `CREATE` statements by hand, you'll build this graph the way you'd actually do it with real data: **upload CSV files** and let Neo4j's import tool turn them into nodes and relationships.

Create these 4 files on your own machine (Notepad / Excel / any text editor — save as plain `.csv`):

**`customers.csv`**
```
customer_id,name,city
CUST-001,Raj Patel,Mumbai
CUST-002,Priya Singh,Bangalore
CUST-003,Arjun Mehta,Delhi
```

**`suppliers.csv`**
```
supplier_id,name
SUP-001,TechDistributors Inc
SUP-002,HomeOffice Supplies
```

**`products.csv`** — note the `supplier_id` column; that's what lets the importer wire up `SUPPLIED_BY` automatically
```
product_id,name,category,supplier_id
PRD-001,Wireless Mouse,Electronics,SUP-001
PRD-002,Office Chair,Furniture,SUP-002
PRD-003,Desk Lamp,Furniture,SUP-002
```

**`orders.csv`** — note the `customer_id` and `product_id` columns; those drive `PLACED` and `CONTAINS`
```
order_id,order_date,customer_id,product_id
ORD-001,2026-06-01,CUST-001,PRD-001
ORD-002,2026-06-03,CUST-002,PRD-002
ORD-003,2026-06-05,CUST-001,PRD-003
```

---

## Input 7

**Type:** Text

### Step 3 — Upload the files and build the graph with Neo4j Data Importer

Neo4j's **Data Importer** is a no-code tool that turns CSV files into a graph by letting you map columns to node labels/properties and draw relationships between them.

1. From the **Aura Console**, open your `globalmart-graph-demo` instance, then click **Import Data** (or go to `data-importer.neo4j.io` directly and connect it to your instance using the same URI/username/password from Step 1).
2. **Add data source** → **Upload files** → select all 4 CSVs at once.
3. For each file, create a **node table**:
   - `customers.csv` → node label **Customer**, key property `customer_id`
   - `suppliers.csv` → node label **Supplier**, key property `supplier_id`
   - `products.csv` → node label **Product**, key property `product_id` (map `supplier_id` as a plain property for now — you'll turn it into a relationship next)
   - `orders.csv` → node label **Order**, key property `order_id` (map `customer_id` and `product_id` as plain properties too)
4. Draw the 3 relationships by dragging between node tables in the canvas:
   - **Customer → Order**, type `PLACED`, matched on `orders.customer_id = customers.customer_id`
   - **Order → Product**, type `CONTAINS`, matched on `orders.product_id = products.product_id`
   - **Product → Supplier**, type `SUPPLIED_BY`, matched on `products.supplier_id = suppliers.supplier_id`
5. Click **Run import**. The tool writes every node and relationship into your AuraDB instance in one batch — no Cypher typed by hand.
6. Switch back to the **Neo4j Browser** and run `MATCH (n) RETURN n` to see the graph.

---

## Input 8

**Type:** Short Answer

**Question:** After running the import, how many total nodes and how many total relationships did `MATCH (n) RETURN n` (and the relationship count shown alongside it) confirm in your Neo4j Browser?

**Template:** null

**Tags**
- data-ingestion / graph-database (skill)

---

## Input 9

**Type:** File Upload

**Question:** Take a screenshot of the Neo4j Browser's graph view after running `MATCH (n) RETURN n`, showing your full imported graph. Upload it here.

**Max No. of Files:** 1

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- databricks (tool)

---

## Input 10

**Type:** Text

### Step 4 — Try a Cypher query in the Neo4j Browser

Paste this into the Neo4j Browser and look at the result table:

```cypher
// Which products did each customer buy?
MATCH (c:Customer)-[:PLACED]->(o:Order)-[:CONTAINS]->(p:Product)
RETURN c.name AS customer_name, p.name AS product_name, o.order_id AS order_id
```

---

## Input 11

**Type:** Code

**Question:** In the Neo4j Browser, write and run a Cypher query that counts how many orders each customer placed, sorted from most to least. State which customer appears in your result and how many orders they placed — and explain what happened to any customer who has never placed an order.

**Language:** cypher

**Snippet:**

**Solution:**
```cypher
MATCH (c:Customer)-[:PLACED]->(o:Order)
RETURN c.name AS customer_name, COUNT(o) AS order_count
ORDER BY order_count DESC
```
Given the 3 orders in `orders.csv`, this returns **Raj Patel** with 2 orders (`ORD-001`, `ORD-003`) and **Priya Singh** with 1 order (`ORD-002`). **Arjun Mehta does not appear in the result at all** — a Cypher `MATCH` only returns rows where the pattern actually exists, so a customer with zero `PLACED` relationships is silently excluded, the same way an inner join in SQL would drop a row with no match rather than showing it with a count of zero.

**Tags**
- data-ingestion / graph-database (skill)
- data-wrangling / group-by-aggregate (skill)

---

## Scenario 3 — Read the Graph Into Databricks

**Overview:** This is a side-exploration, not part of GlobalMart's real pipeline. Having built and queried your graph directly in the Neo4j Browser (Scenario 2), you now close the loop the same way the REST API section did: connect to AuraDB from Databricks using the official `neo4j` Python driver, re-run a graph query from inside a notebook, and land the result as a sandbox Delta table.

**Outcome:** Two sandbox Delta tables — `graph_customer_orders` (the customer → product query, run from Databricks) and `graph_product_suppliers` (a supplier-traversal query you write yourself) — plus your completed notebook, submitted with credentials restored to placeholders.

---

## Input 12

**Type:** Text

### Install the driver and connect

Install the official Neo4j Python driver on this cluster:

```python
%pip install neo4j
```

Connect using the 3 values Neo4j showed you when the instance was created in Scenario 2, Input 5:

```python
# ─── Connect to your AuraDB instance ───────────────────────────────────────────
# HOW TO GET THESE VALUES: the connection panel shown once, when you created
# your AuraDB instance in Scenario 2 — or the credentials file you downloaded.
# Never commit real credentials: replace these placeholders locally, then
# swap them back to placeholders before you upload or submit this notebook.

from neo4j import GraphDatabase

NEO4J_URI      = "neo4j+s://YOUR_INSTANCE_ID.databases.neo4j.io"  # ← replace locally only
NEO4J_USER     = "neo4j"
NEO4J_PASSWORD = "YOUR_AURADB_PASSWORD"  # ← replace locally only

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def run_cypher(query, params=None):
    """Run one Cypher query against AuraDB and return a list of plain dicts."""
    with driver.session() as session:
        result = session.run(query, params or {})
        return [dict(record) for record in result]

node_count = run_cypher("MATCH (n) RETURN count(n) AS total")[0]["total"]
print(f"Connected! Total nodes in the graph: {node_count}")
```

---

## Input 13

**Type:** Text

### Run the same query from Databricks, and save it

```python
customer_product_query = """
MATCH (c:Customer)-[:PLACED]->(o:Order)-[:CONTAINS]->(p:Product)
RETURN c.customer_id AS customer_id, c.name AS customer_name,
       p.product_id  AS product_id,  p.name AS product_name,
       o.order_id    AS order_id,    o.order_date AS order_date
"""

rows = run_cypher(customer_product_query)
graph_df = spark.createDataFrame(rows)

graph_df.write.format("delta").mode("overwrite").save(f"{sandbox_path}/graph_customer_orders")
print(f"Saved to: {sandbox_path}/graph_customer_orders")
```

Same pattern as the API section: this lands in `sandbox/`, never `bronze/` — it's exploration output, not a GlobalMart pipeline table.

---

## Input 14

**Type:** Code

**Question:** Write a Cypher query, as a Python string in the same shape as `customer_product_query` above, that returns — for every order — which product it contained and which supplier that product comes from (a 2-hop traversal: `Order` → `Product` → `Supplier`). Run it through `run_cypher(...)`, convert the result to a DataFrame, and save it to `sandbox_path/graph_product_suppliers`.

**Language:** python

**Snippet:**
```python
product_supplier_query = """
# your Cypher query here
"""

# run it, convert to a DataFrame, and save it
```

**Solution:**
```python
product_supplier_query = """
MATCH (o:Order)-[:CONTAINS]->(p:Product)-[:SUPPLIED_BY]->(s:Supplier)
RETURN o.order_id AS order_id, p.name AS product_name, s.name AS supplier_name
"""

supplier_rows = run_cypher(product_supplier_query)
supplier_df = spark.createDataFrame(supplier_rows)

supplier_df.write.format("delta").mode("overwrite").save(f"{sandbox_path}/graph_product_suppliers")
```
This chains two relationship hops in one `MATCH` pattern — `Order-[:CONTAINS]->Product` then `Product-[:SUPPLIED_BY]->Supplier` — the same traversal idea as the customer→product query in Input 13, just one hop longer. Given the fixed graph from Scenario 2, this returns 3 rows: `ORD-001` / Wireless Mouse / TechDistributors Inc, `ORD-002` / Office Chair / HomeOffice Supplies, `ORD-003` / Desk Lamp / HomeOffice Supplies.

**Tags**
- data-ingestion / graph-database (skill)
- spark (tool)

---

## Input 15

**Type:** Short Answer

**Question:** Looking at your `graph_product_suppliers` table, one supplier appears twice while the other appears only once. Which supplier appears twice, and why?

**Template:** null

**Tags**
- data-ingestion / graph-database (skill)

---

## Input 16

**Type:** File Upload

**Question:** Take a screenshot of your Databricks notebook output showing both `graph_customer_orders` and `graph_product_suppliers` after saving, with their row counts visible. Upload it here.

**Max No. of Files:** 1

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- databricks (tool)

---

## Input 17

**Type:** Text

### Close the connection and review the checklist

```python
driver.close()
print("Neo4j driver closed.")
```

An open driver holds a connection pool open on AuraDB's side — closing it is good hygiene, not optional cleanup.

```
Submission Checklist
─────────────────────────────────────────────────────────
✅ Multi-base-currency FX table saved  → sandbox/fx_rates_multi_base
✅ Historical FX table saved (append mode) → sandbox/fx_rates_historical
✅ Neo4j AuraDB Free account + instance created, credentials saved
✅ 4 CSV files prepared (customers, suppliers, products, orders)
✅ Files uploaded and imported via Neo4j Data Importer (11 nodes, 9 relationships)
✅ Customer -> Order -> Product query run in Neo4j Browser
✅ Same query run from Databricks via the neo4j Python driver
✅ Result saved → sandbox/graph_customer_orders
✅ Supplier traversal exercise completed → sandbox/graph_product_suppliers
✅ Before submitting: replaced NEO4J_URI/PASSWORD with placeholders again
─────────────────────────────────────────────────────────
```

>[!IMPORTANT]
>Reminder: none of this feeds `fact_sales`. You practiced two ingestion patterns — REST API and graph traversal — that show up in other projects, using GlobalMart as a familiar backdrop.

---

## Input 18

**Type:** File Upload

**Question:** Upload your completed Databricks notebook (.ipynb file). Before uploading, confirm you have replaced `NEO4J_URI` and `NEO4J_PASSWORD` with placeholders — your notebook should contain no real credential when submitted.

**Max No. of Files:** 1

**Max File Size:** 10

**Allowed File Types:** ANY, JUPYTER_NOTEBOOK

**Tags**
- databricks (tool)
