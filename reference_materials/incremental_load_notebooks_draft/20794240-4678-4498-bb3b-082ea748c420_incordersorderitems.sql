-- ============================================================
-- GlobalMart — Incremental Data Script
-- Source : Supabase (Postgres)
-- Tables : orders, order_items
-- Purpose: Simulate new orders + status updates for Day 11-12
--          incremental pipeline exercise
-- Run in : Supabase SQL Editor
-- ============================================================


-- ── New Orders ───────────────────────────────────────────────
INSERT INTO orders (order_id, customer_id, order_date, status, total_amount, updated_at)
VALUES
  ('ORD-1005', 'CUST-00101', '2026-06-06', 'Placed',   3200.00, NOW()),
  ('ORD-1006', 'CUST-00202', '2026-06-06', 'Placed',   5400.00, NOW()),
  ('ORD-1007', 'CUST-00303', '2026-06-07', 'Placed',   1800.00, NOW()),
  ('ORD-1008', 'CUST-00404', '2026-06-07', 'Placed',   7600.00, NOW()),
  ('ORD-1009', 'CUST-00505', '2026-06-08', 'Placed',   2900.00, NOW()),
  ('ORD-1010', 'CUST-00606', '2026-06-08', 'Placed',   4100.00, NOW());


-- ── Status Updates on Existing Orders ────────────────────────
UPDATE orders SET status = 'Shipped',   updated_at = NOW() WHERE order_id = 'ORD-1001';
UPDATE orders SET status = 'Delivered', updated_at = NOW() WHERE order_id = 'ORD-1002';
UPDATE orders SET status = 'Shipped',   updated_at = NOW() WHERE order_id = 'ORD-1003';


-- ── New Order Items (linked to new orders above) ─────────────
INSERT INTO order_items (order_item_id, order_id, product_id, quantity, unit_price, updated_at)
VALUES
  ('OI-3001', 'ORD-1005', 'PRD-00012', 2,  800.00, NOW()),
  ('OI-3002', 'ORD-1005', 'PRD-00034', 1, 1600.00, NOW()),
  ('OI-3003', 'ORD-1006', 'PRD-00056', 3, 1800.00, NOW()),
  ('OI-3004', 'ORD-1007', 'PRD-00078', 1, 1800.00, NOW()),
  ('OI-3005', 'ORD-1008', 'PRD-00090', 2, 3800.00, NOW()),
  ('OI-3006', 'ORD-1009', 'PRD-00023', 1, 2900.00, NOW()),
  ('OI-3007', 'ORD-1010', 'PRD-00045', 2, 2050.00, NOW()),
  ('OI-3008', 'ORD-1010', 'PRD-00067', 1, 2050.00, NOW());


-- ── Verify ───────────────────────────────────────────────────
SELECT order_id, status, updated_at FROM orders ORDER BY updated_at DESC LIMIT 10;
SELECT order_item_id, order_id, product_id FROM order_items ORDER BY order_item_id DESC LIMIT 10;
