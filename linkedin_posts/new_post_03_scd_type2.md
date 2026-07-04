The 3 Extra Columns That Make "Slowly Changing Dimensions" Possible

I used to think tracking history for a customer or product dimension meant something complicated.

It's actually just 3 columns, applied consistently:

is_current — is this the version of the row that's true right now?
effective_start_date — when did this version become true?
effective_end_date — when did it stop being true? (NULL if it's still current)

This is SCD Type 2 (Slowly Changing Dimension, Type 2) — instead of overwriting a customer's old email when it changes (that's Type 1), you close out the old row and insert a new one, keeping both.

Why go to the trouble?
Without it, if a customer's address changes today, EVERY past order they ever placed would silently start showing their new address — even orders that shipped to the old one. History would quietly rewrite itself.

Key Takeaways
• SCD Type 1 = overwrite (simple, but no history)
• SCD Type 2 = version + track (more setup, but point-in-time accuracy)
• The decision isn't "which is better" — it's "does anyone need to know what this looked like in the past?"
• Implemented with a MERGE: close the old row (set is_current = false, stamp effective_end_date), insert the new one

The interesting part?
Not every dimension needs Type 2. A ~5-row payment method lookup table almost never needs history. A customer or product table, where price and contact details genuinely change over time and past transactions must stay accurate — that's exactly where it earns its complexity.

#DataEngineering #Databricks #DeltaLake #SCD #DimensionalModeling #DataWarehouse #ETL #KimballMethodology #BigData #LearningInPublic
