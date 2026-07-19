"""
Step 5: Insert day2_orders_sample.csv (50 rows) into the LIVE Supabase orders table.
This simulates "Day 2 business activity" and is what shows up in the WAL / replication slot.

Note: day2_orders_sample.csv has lowercase column headers AND dates in DD-MM-YYYY HH:MM
format (vs. the ISO timestamps in orders_sample.csv) -- this format drift is intentional
and mirrors how data really arrives from different batches/systems.

Setup:
    pip install psycopg2-binary pandas python-dotenv
    Uses the same .env file as 02_load_orders_sample.py (in this folder).

Run locally:
    python 05_simulate_day2_changes.py
"""

import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))

conn = psycopg2.connect(
    host=os.environ["SUPABASE_HOST"],
    port=os.environ.get("SUPABASE_PORT", "5432"),
    dbname=os.environ.get("SUPABASE_DB", "postgres"),
    user=os.environ["SUPABASE_USER"],
    password=os.environ["SUPABASE_PASSWORD"],
    sslmode="require",
)

df = pd.read_csv(os.path.join(SCRIPT_DIR, "day2_orders_sample.csv"))

date_cols = ["orderdate", "shippingdate", "expecteddeliverydate", "actualdeliverydate"]
for col in date_cols:
    df[col] = pd.to_datetime(df[col], dayfirst=True)

df.columns = [
    "order_id", "customer_id", "order_date", "shipping_date",
    "expected_delivery_date", "actual_delivery_date",
    "shipping_tier_id", "supplier_id", "order_channel",
]

rows = list(df.itertuples(index=False, name=None))

with conn:
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO public.poc_orders
                (order_id, customer_id, order_date, shipping_date,
                 expected_delivery_date, actual_delivery_date,
                 shipping_tier_id, supplier_id, order_channel)
            VALUES %s
            ON CONFLICT (order_id) DO NOTHING
            """,
            rows,
        )

print(f"Inserted {len(rows)} 'Day 2' rows into public.poc_orders (live table now has 200 + {len(rows)} rows)")
conn.close()
