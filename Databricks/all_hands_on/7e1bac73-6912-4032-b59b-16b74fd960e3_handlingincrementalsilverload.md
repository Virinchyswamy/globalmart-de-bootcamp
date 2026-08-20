# Handling Incremental Silver Load
## Content Type
Scenario

## Overview
Read only the changed rows from Bronze using Change Data Feed and merge them into Silver, without reprocessing data already curated.

## Learning Objectives
- Use Change Data Feed to read only the rows that changed since the last Silver run.
- Apply the correct SCD strategy (SCD1 or SCD2) when merging incremental data into Silver.
- Verify that Silver tables reflect only the new batch without duplicating existing records.

## Prerequisites
- Bronze incremental load completed — all Bronze tables have a new Delta version
- CDF enabled on all Bronze tables before the incremental Bronze load ran
- LAST_PROCESSED_VERSION noted for each Bronze table from the previous activity
- Silver full load already built, all Silver tables exist with the initial dataset

## Duration of Completion
60 minutes

## Level
Intermediate

## Industries
- e-commerce

## Tags
- approach (skill)
- data-understanding (skill)
- data-storage (skill)
- data-wrangling (skill)
- batch-etl (skill)
- data-modelling (skill)
- databricks (tool)
- spark (tool)

#### Overview
Read only the changed rows from Bronze using Change Data Feed and merge them into Silver, without reprocessing data already curated.

#### Level
intermediate

#### Industries
- e-commerce

#### Tags
- approach (skill)
- data-understanding (skill)
- data-storage (skill)
- data-wrangling (skill)
- batch-etl (skill)
- data-modelling (skill)
- databricks (tool)
- spark (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

>[!IMPORTANT]
> Change Data Feed (CDF) must have been enabled on all Bronze tables **before** the incremental Bronze load ran. If CDF was not enabled at that point, `table_changes()` will not return the new rows, it only captures changes from the version it was enabled on, not retroactively.

Verify CDF is active on each Bronze table before proceeding:
```python
spark.sql("describe history <your-catalog>.bronze.<table>") \
     .display()
 ```

Confirm `delta.enableChangeDataFeed = true` appears in the SettableProperties. If not, go back and enable it before running this activity.

**Tags**


##### Input 2
**Type:** Text

The Bronze layer now has a new Delta version for each source table — the incremental batch has landed. Silver, however, still reflects the state from the initial full load.

Reprocessing all of Bronze from scratch every time data arrives is not scalable. A table with millions of rows should not be fully re-scanned just because a few hundred rows changed. The pipeline needs to read only what is new, apply the same cleaning and transformation logic, and merge the result into Silver precisely — leaving everything already curated untouched.

This is what Change Data Feed makes possible. Every write to a Delta table, insert, update, delete- is recorded as a versioned change. By reading from a specific version onwards, the pipeline sees only the rows that actually changed in this batch, not the full history.

**Tags**


##### Input 3
**Type:** Text

### Task — Incremental Silver Load

For each Bronze table, read only the rows that changed since the last Silver run and merge them into the corresponding Silver table.

**Goals:**
- Read only new and updated rows from Bronze using CDF
- Apply the same cleaning and transformation logic used in the full load
- Merge into Silver without duplicating records already present

**Outcome:**
- Silver tables contain only the new incremental data on top of the full load — no duplicates, no missing rows

The merge strategy differs by table type:
- **SCD2 tables** (`customers`, `products`, `payments`) — close the old version (`is_current = false`, stamp `effective_end_date`) then insert the new version as a fresh row with a new surrogate key
- **SCD1 tables** (`orders`, `order_items`) — a single MERGE: update the row if it already exists, insert if it is new

Run tables with parent-child relationships in the correct order — a child table cannot be merged before its parent exists in Silver.

**Tags**


##### Input 4
**Type:** Short Answer

**Question:** Write the PySpark code to read only new and updated rows from a Bronze Delta table using Change Data Feed, starting from `LAST_PROCESSED_VERSION + 1`. Your code must exclude `update_preimage` rows.

**Template:** <p>Code:</p><pre><code class="language-python">&nbsp;</code></pre>

**Tags**
- data-storage / delta-lakehouse / change-data-feed (skill)

##### Input 5
**Type:** File Upload

**Question:** Upload screenshots showing the CDF output for each Bronze table:
- The result of your `readChangeFeed` read before the merge. 
- Each screenshot must show the dataframe with the row count printed (e.g., `Changed rows via CDF: 1,000`). One screenshot per table is sufficient.

**Max No. of Files:** 10

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**


##### Input 6
**Type:** File Upload

**Question:** Upload all notebooks created for the incremental Silver load, one notebook per table.

**Max No. of Files:** 10

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- batch-etl / medallion-architecture (skill)

##### Input 7
**Type:** Short Answer

**Question:** What is `LAST_PROCESSED_VERSION` and what happens if it is set too low? What happens if it is set too high?

**Template:** null

**Tags**
- data-storage / delta-lakehouse / change-data-feed (skill)

##### Input 8
**Type:** Short Answer

**Question:** Why do some Silver tables use SCD2 while others use SCD1 in the incremental load? What property of the data drives this decision?

**Template:** null

**Tags**
- data-modelling / dimensional-modelling / slowly-changing-dimensions (skill)

