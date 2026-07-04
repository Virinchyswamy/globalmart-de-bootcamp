Running My Pipeline Twice Should Never Double My Data. Here's How I Made Sure of It.

Early on, my mental model for incremental loading was simple: "just load whatever's new since last time." It took a re-run gone wrong to teach me that "new since last time" is doing a lot of hidden work in that sentence.

The failure mode:
If your pipeline appends new rows and something makes you re-run it — a retry, a manual re-trigger, a scheduler hiccup — and it processes the SAME batch of "new" rows twice, you now have duplicates. Nobody notices until a revenue number looks wrong weeks later.

What actually fixes this:
✅ A control table tracking exactly what was already processed (last watermark value, or last Change Data Feed version read)
✅ MERGE instead of blind append — match on the natural key, update if it exists, insert if it doesn't
✅ Advance the control table ONLY after a successful write, never before

Key Learning
Idempotency isn't a nice-to-have property you add later — it has to be designed into the read step (know exactly what "new" means, precisely) AND the write step (MERGE, not append) at the same time. Fixing only one half still leaves you exposed.

I also explored:
Watermark-based incremental loading vs. Change Data Feed (CDF)-based incremental loading — different mechanisms, same underlying idempotency requirement
Why "run it again and confirm you see 0 changed rows" is the actual test that proves a pipeline is safe, not just "run it once and it worked"

The interesting part?
The safest pipelines I've studied aren't the ones that never need a re-run. They're the ones where a re-run is completely boring — same result, every time, on purpose.

#DataEngineering #Databricks #DeltaLake #IncrementalLoading #ChangeDataFeed #ETL #DataPipeline #DataReliability #LearningInPublic
