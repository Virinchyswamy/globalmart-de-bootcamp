Auto Loader Has 4 Ways to Handle a New Column Showing Up. I Only Knew One.

I knew Auto Loader could "handle schema evolution automatically." I assumed that meant one fixed behavior.

It's actually a config you choose — cloudFiles.schemaEvolutionMode — with four real options:

addNewColumns — adds the new column automatically, updates the stored schema, restarts the stream. The production default for most cases.
rescue — keeps the existing schema strict, but captures anything unexpected into a special _rescued_data JSON column instead of losing it.
failOnNewColumns — the stream stops entirely the moment a new column appears. Useful when every schema change legally needs human review first.
none — new columns are silently dropped. Rarely what you actually want.

Key Learning
"rescue" mode was the one that changed how I think about ingestion. Instead of choosing between "auto-add the column" and "break on it," you get a third option: capture everything, decide later. Nothing is lost while you figure out whether that new field is real or a fluke.

I also explored:
Why the schema is stored in a separate schemaLocation folder, not re-inferred from scratch on every restart
Why "Bronze should never drop a column" and "rescue mode" are really the same underlying philosophy

The interesting part?
The failure mode I was most worried about — a new column silently corrupting downstream logic — turned out to already have a named, documented setting built specifically to prevent it. I just hadn't gone looking for it yet.

#DataEngineering #Databricks #AutoLoader #StructuredStreaming #DeltaLake #SchemaEvolution #ETL #ApacheSpark #LearningInPublic
