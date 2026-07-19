-- ============================================================
-- GlobalMart — Incremental Data Script
-- Schema  : public
-- Tables  : public.orders, public.order_items
-- Purpose : Simulate 2 new orders + 3 delivery updates
--           for the incremental pipeline exercise (Day 11)
-- Run in  : Supabase SQL Editor
-- ============================================================


-- ── Step 1: Insert 2 new orders ──────────────────────────────
-- High ID range (OR-9000xx) — safely above existing ~126k orders
INSERT INTO public.orders
    ("OrderID", "CustomerID", "OrderDate", "ShippingDate",
     "ExpectedDeliveryDate", "ActualDeliveryDate",
     "ShippingTierID", "SupplierID", "OrderChannel")
VALUES
    ('OR-900001', 'CUST-08966', '2026-06-06 10:15:00+00', NULL, NULL, NULL, 'SHP-002', 'SUP-05', 'Online'),
    ('OR-900002', 'CUST-14479', '2026-06-06 14:30:00+00', NULL, NULL, NULL, 'SHP-003', 'SUP-07', 'Mobile App');


-- ── Step 2: Insert order items for the new orders ─────────────
-- Item IDs use OR-INC-9000xx — avoids collision with ~283k existing items
INSERT INTO public.order_items
    ("OrderItemID", "OrderID", "ProductID", "Quantity")
VALUES
    ('OR-INC-900001', 'OR-900001', 'PRD-00410', 2),
    ('OR-INC-900002', 'OR-900001', 'PRD-00107', 1),
    ('OR-INC-900003', 'OR-900002', 'PRD-00437', 3);


-- ── Step 3: Update 3 existing orders ─────────────────────────
-- Corrects ActualDeliveryDate on 3 orders — trigger auto-bumps updated_at
-- which is the cursor Lakeflow Connect uses to detect the change
UPDATE public.orders SET "ActualDeliveryDate" = '2026-06-07 09:00:00+00' WHERE "OrderID" = 'OR-000001';
UPDATE public.orders SET "ActualDeliveryDate" = '2026-06-07 11:30:00+00' WHERE "OrderID" = 'OR-000002';
UPDATE public.orders SET "ActualDeliveryDate" = '2026-06-08 08:45:00+00' WHERE "OrderID" = 'OR-000003';


-- ── Step 4: Verify ────────────────────────────────────────────
-- New orders
SELECT "OrderID", "CustomerID", "OrderDate", "OrderChannel", updated_at
FROM public.orders
WHERE "OrderID" IN ('OR-900001', 'OR-900002');

-- New items
SELECT "OrderItemID", "OrderID", "ProductID", "Quantity"
FROM public.order_items
WHERE "OrderItemID" LIKE 'OR-INC-9000%';

-- Updated rows — confirm updated_at has advanced beyond 2026-07-16
SELECT "OrderID", "ActualDeliveryDate", updated_at
FROM public.orders
WHERE "OrderID" IN ('OR-000001', 'OR-000002', 'OR-000003');
