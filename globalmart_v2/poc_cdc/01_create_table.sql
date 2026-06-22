-- Run this in the Supabase SQL editor (or any Postgres client connected to Supabase)

-- Named "poc_orders" (not "orders") to avoid colliding with the existing
-- ShopSphere e-commerce schema already in this Supabase project.
CREATE TABLE IF NOT EXISTS public.poc_orders (
    order_id                TEXT PRIMARY KEY,
    customer_id             TEXT NOT NULL,
    order_date              TIMESTAMPTZ,
    shipping_date           TIMESTAMPTZ,
    expected_delivery_date  TIMESTAMPTZ,
    actual_delivery_date    TIMESTAMPTZ,
    shipping_tier_id        TEXT,
    supplier_id             TEXT,
    order_channel           TEXT
);
