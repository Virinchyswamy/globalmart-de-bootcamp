"""
Step 2: Bulk-load orders_sample.csv (200 rows) into Supabase Postgres.
This is the "Day 1 / Initial Load" baseline.

Setup:
    pip install psycopg2-binary pandas python-dotenv
    Copy .env.example to .env in this folder and fill in your Supabase values.

Run locally (any of these):
    python 02_load_orders_sample.py
    (or hit Run in VS Code / Code Runner -- it will pick up .env automatically)
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

df = pd.read_csv(os.path.join(SCRIPT_DIR, "orders_sample.csv"))

# orders_sample.csv columns are PascalCase; map to the lowercase table columns
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

print(f"Inserted {len(rows)} rows into public.poc_orders")
conn.close()
