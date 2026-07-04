I Assumed All CDC Was Log-Based. I Was Wrong.

For weeks, whenever someone said "CDC" (Change Data Capture), I pictured one thing: reading a database's write-ahead log (WAL), the same stream the database itself uses for replication.

Then I looked closely at a real managed CDC pipeline built on Lakeflow Connect.

It wasn't reading the WAL at all.

It was query-based — polling the source table on a cursor column (updated_at), pulling only rows changed since the last run.

What that trade-off actually means:
• No need for logical replication slots or WAL-level access on the source database
• Much simpler to set up and reason about
• But it CANNOT see hard deletes — if a row is physically deleted at the source, a cursor query never notices, because the row simply isn't there anymore to be "changed"

Key Takeaways
• "CDC" is not one technique — log-based and query/cursor-based solve the same problem very differently
• A managed connector's default behavior is a design decision, not a limitation to work around blindly
• If your source data can be hard-deleted, ask your CDC tool how (or whether) it handles that — don't assume

The interesting part?
The gap isn't a bug. It's a documented, deliberate trade-off — simplicity and lower operational overhead, in exchange for giving up delete visibility.

Now I read every ingestion tool's docs with one extra question in mind: what does this NOT see?

#DataEngineering #Databricks #CDC #DeltaLake #LakeflowConnect #ETL #DataPipeline #Postgres #BigData #LearningInPublic
