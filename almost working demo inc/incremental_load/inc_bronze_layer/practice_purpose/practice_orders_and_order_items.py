# Databricks notebook source
# MAGIC %sql
# MAGIC -- 1. Did the UPDATE on OR-000478 come through?
# MAGIC SELECT orderid, customerid, shippingdate, actualdeliverydate, orderchannel, updated_at
# MAGIC FROM gbmart.bronze.orders
# MAGIC WHERE orderid = 'OR-000478';
# MAGIC -- Expect: actualdeliverydate populated, updated_at recent

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 2. Did the 2 new orders (OR-900001, OR-900002) land?
# MAGIC SELECT orderid, customerid, orderdate, orderchannel, updated_at
# MAGIC FROM gbmart.bronze.orders
# MAGIC WHERE orderid IN ('OR-900001', 'OR-900002');
# MAGIC -- Expect: 2 rows

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 3. Total row count — should be 126,036 + 2 = 126,038
# MAGIC SELECT COUNT(*) AS total_orders FROM gbmart.bronze.orders;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 4. Did matching order_items for the 2 new orders land?
# MAGIC -- (Only relevant if you uncommented that INSERT in the SQL changes file)
# MAGIC SELECT orderitemid, orderid, productid, quantity
# MAGIC FROM gbmart.bronze.order_items
# MAGIC WHERE orderid IN ('OR-900001', 'OR-900002');
# MAGIC -- Expect: 0 rows if you left that block commented out, 2 rows if you ran it
# MAGIC
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 5. Total row count — should be 377,866 (+2 if order_items were added)
# MAGIC SELECT COUNT(*) AS total_order_items FROM gbmart.bronze.order_items;