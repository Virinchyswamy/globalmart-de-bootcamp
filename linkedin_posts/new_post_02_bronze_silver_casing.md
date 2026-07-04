Why I Stopped "Cleaning Up" Column Names in My Bronze Layer

My first instinct when ingesting a messy CSV was to fix everything immediately — rename CustomerID to customer_id, lowercase everything, make it "nice" right away.

Turns out, in a proper medallion architecture, that instinct is wrong for the Bronze layer.

The convention I follow now:
✅ Bronze preserves the source's raw casing and structure, exactly as it arrived (CustomerID, OrderDate, ShippingTierID — whatever the source system actually sent)
✅ Silver is where standardization happens — that's the layer's actual job: rename to snake_case, fix types, apply business rules

Why this matters more than it sounds:
If a pipeline bug ever produces a wrong number three layers downstream, Bronze is your ground truth for "what did the source system actually send us?" If you've already renamed and reshaped things in Bronze, you've destroyed the one layer that was supposed to answer that question with certainty.

Key Learning
Standardization isn't just "make it look nice" — it's a specific, single-responsibility transformation that belongs in exactly one layer. Doing it too early quietly removes your own ability to audit what really happened.

I also explored:
Why Bronze tables should never drop a column even if it's not needed downstream
How this same discipline makes debugging schema drift dramatically easier

Sometimes the best data engineering decision is choosing NOT to clean something up yet.

#DataEngineering #Databricks #DeltaLake #MedallionArchitecture #DataModeling #ETL #DataQuality #BigData #LearningInPublic
