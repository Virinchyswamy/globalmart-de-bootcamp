-- Run this in the Supabase SQL editor AFTER step 2 (table has 200 rows)

-- 1. Confirm logical replication is on (Supabase enables this by default)
SHOW wal_level;

-- 2. Declare which table(s) we want to track changes for
CREATE PUBLICATION poc_orders_pub FOR TABLE public.poc_orders;

-- 3. Create a replication slot — this is the "bookmark" Databricks will read from.
--    test_decoding is a built-in plugin that outputs human-readable text,
--    good enough to prove CDC is working for this POC.
SELECT pg_create_logical_replication_slot('poc_orders_slot', 'test_decoding');

-- Sanity check: list active slots
SELECT slot_name, plugin, slot_type, active FROM pg_replication_slots;
