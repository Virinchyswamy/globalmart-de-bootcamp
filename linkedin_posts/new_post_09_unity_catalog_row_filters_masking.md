Same Table. Same Query. Three Different Answers. Here's Why.

I ran SELECT * FROM customers three times, same exact query, and got three different results depending on which "role" I was querying as.

No application code changed. No WHERE clause was added anywhere. This is Unity Catalog row filters and column masks, and once I understood the mechanism, it genuinely surprised me how simple it is.

How it actually works:
A row filter is just a SQL function that returns TRUE or FALSE per row. You attach it once, to the table, with ALTER TABLE ... SET ROW FILTER — from that moment, EVERY reader of that table (any notebook, any BI tool, any query) is filtered automatically.

A column mask works the same way, but per-column: a function that returns a transformed value instead of the raw one. Attach it once with ALTER TABLE ... ALTER COLUMN ... SET MASK, and every reader sees the masked version instead of the real one.

Key Learning
Governance implemented this way isn't a suggestion applications have to remember to respect — it's enforced at the table's own metadata level, underneath every possible entry point. No engineer can "forget" to add the filter, because there's nothing to remember to add.

I also explored:
Why this is safest to build and test on a practice table first — attaching a filter to a shared table changes what EVERYONE sees, immediately, with no warning
The difference between DESCRIBE HISTORY (one table's own version log) and cross-table lineage (what fed this table, what consumes it)

The interesting part?
I expected row-level security to require changes in every application querying the data. It requires zero.

#DataEngineering #Databricks #UnityCatalog #DataGovernance #DataSecurity #RowLevelSecurity #BigData #LearningInPublic
