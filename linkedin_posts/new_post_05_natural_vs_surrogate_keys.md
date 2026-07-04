Every Dimension I Built Had a Perfect Surrogate Key. Then I Learned My Fact Table Might Not Even Use Them.

I'd internalized the rule: dimension tables get a surrogate key, fact tables join to dimensions on THAT key, never the natural/business key. It's the Kimball-standard default, and it's cert material for a reason.

Then I looked at a real, production-style fact table design that intentionally joins every dimension by natural key instead.

Why would anyone do that on purpose?
Simplicity, mainly — every dimension gets the exact same join treatment, no special-casing. But it has a real, specific cost:

If a customer's email changes today, and their dimension row versions with a new surrogate key (SCD Type 2), a fact table joined on the SURROGATE key would still resolve last year's sales to the exact dimension version that was true back then.

A fact table joined on the NATURAL key instead just resolves every join — past and present — to whichever row currently has that key. Point-in-time accuracy, quietly gone.

Key Takeaways
• The surrogate-key rule exists specifically to protect point-in-time accuracy under SCD Type 2
• Skipping it isn't automatically wrong — it's a real, documented trade-off some teams make for simplicity
• The important part is knowing you're making that trade-off, not stumbling into it

The interesting part?
This is exactly the kind of "shortcut" that looks like a mistake in a code review until someone explains the reasoning behind it. Now I always ask why before assuming a deviation from the textbook pattern is an error.

#DataEngineering #Databricks #DimensionalModeling #DataWarehouse #KimballMethodology #SCD #DataModeling #BigData #LearningInPublic
