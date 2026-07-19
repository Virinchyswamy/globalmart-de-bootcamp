"""
Generate a realistic ~1GB retail sales CSV dataset for the Day 4 learning lab
(Storage Formats / Partitioning / Performance Levers).

Usage:
    python generate_retail_sales_dataset.py

Output:
    retail_sales_dataset.csv  (written next to this script)

Design notes:
- Uses only the stdlib `csv`/`random`/`datetime` modules — no pandas, no faker
  (faker isn't installed on this machine; stdlib is guaranteed available).
- Streams rows to disk via a generator + csv.writer instead of building
  everything in memory first, so this comfortably handles millions of rows.
- Calibrates row count from a real measured bytes-per-row instead of guessing:
  writes a small sample batch, measures its actual size on disk, then computes
  how many rows are needed to land in the target byte range.
- OrderID is a zero-padded sequential counter (not random+dedupe) — the
  simplest way to *guarantee* zero duplicates at multi-million-row scale.
"""

import csv
import os
import random
import time
from datetime import date, timedelta

# ─── Tunable target ────────────────────────────────────────────────────────
TARGET_BYTES = 1_000_000_000          # ~1 GB (decimal)
TARGET_MIN_BYTES = 900_000_000        # 900 MB floor
TARGET_MAX_BYTES = 1_100_000_000      # 1.1 GB ceiling
MIN_ROWS = 3_000_000
MAX_ROWS = 5_000_000
CALIBRATION_ROWS = 50_000

OUTPUT_FILENAME = "retail_sales_dataset.csv"
CALIBRATION_FILENAME = "_calibration_sample.csv"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(SCRIPT_DIR, OUTPUT_FILENAME)
CALIBRATION_PATH = os.path.join(SCRIPT_DIR, CALIBRATION_FILENAME)

random.seed(42)  # reproducible dataset across re-runs

# ─── Reference data: countries -> states -> cities ─────────────────────────
COUNTRIES = {
    "India": {
        "region": "APAC",
        "states": {
            "Maharashtra": ["Mumbai", "Pune", "Nagpur"],
            "Karnataka": ["Bangalore", "Mysore"],
            "Delhi": ["New Delhi"],
            "Tamil Nadu": ["Chennai", "Coimbatore"],
            "West Bengal": ["Kolkata", "Howrah"],
        },
    },
    "USA": {
        "region": "North America",
        "states": {
            "California": ["Los Angeles", "San Francisco", "San Diego"],
            "New York": ["New York City", "Buffalo"],
            "Texas": ["Houston", "Austin", "Dallas"],
            "Florida": ["Miami", "Orlando"],
            "Illinois": ["Chicago"],
        },
    },
    "UK": {
        "region": "Europe",
        "states": {
            "England": ["London", "Manchester", "Birmingham"],
            "Scotland": ["Edinburgh", "Glasgow"],
            "Wales": ["Cardiff"],
        },
    },
    "Germany": {
        "region": "Europe",
        "states": {
            "Bavaria": ["Munich", "Nuremberg"],
            "Berlin": ["Berlin"],
            "Hesse": ["Frankfurt"],
            "North Rhine-Westphalia": ["Cologne", "Dusseldorf"],
        },
    },
    "Canada": {
        "region": "North America",
        "states": {
            "Ontario": ["Toronto", "Ottawa"],
            "Quebec": ["Montreal", "Quebec City"],
            "British Columbia": ["Vancouver"],
        },
    },
    "Australia": {
        "region": "APAC",
        "states": {
            "New South Wales": ["Sydney", "Newcastle"],
            "Victoria": ["Melbourne"],
            "Queensland": ["Brisbane"],
        },
    },
}
COUNTRY_NAMES = list(COUNTRIES.keys())

# ─── Reference data: categories -> subcategories -> products, brands, price ─
CATEGORIES = {
    "Electronics": {
        "subcats": {
            "Mobile Phones": ["Galaxy Pro X", "Pixel Ultra", "iPhone Standard"],
            "Laptops": ["UltraBook 14", "ProBook 15", "GameBook X"],
            "Headphones": ["SoundMax Pro", "AudioClear Buds"],
        },
        "brands": ["Samsung", "Apple", "Sony", "Dell", "HP", "Logitech"],
        "price_range": (50, 1500),
    },
    "Furniture": {
        "subcats": {
            "Chairs": ["ErgoChair Deluxe", "ClassicWood Chair"],
            "Tables": ["OakWood Table", "GlassTop Table"],
            "Sofas": ["Comfy 3-Seater", "Leather Recliner"],
        },
        "brands": ["IKEA", "Herman Miller", "Ashley", "Wayfair"],
        "price_range": (40, 1200),
    },
    "Clothing": {
        "subcats": {
            "Men": ["Cotton T-Shirt", "Slim Fit Jeans"],
            "Women": ["Floral Dress", "Yoga Pants"],
            "Kids": ["Graphic Tee", "Denim Shorts"],
        },
        "brands": ["Nike", "Zara", "H&M", "Levis"],
        "price_range": (5, 150),
    },
    "Sports": {
        "subcats": {
            "Fitness": ["Yoga Mat", "Dumbbell Set"],
            "Outdoor": ["Camping Tent", "Hiking Backpack"],
            "Team Sports": ["Soccer Ball", "Basketball"],
        },
        "brands": ["Nike", "Adidas", "Under Armour", "Decathlon"],
        "price_range": (10, 400),
    },
    "Books": {
        "subcats": {
            "Fiction": ["Mystery Novel", "Fantasy Saga"],
            "Non-Fiction": ["Self Help Guide", "History Chronicles"],
            "Children": ["Picture Book", "Activity Book"],
        },
        "brands": ["Penguin", "HarperCollins", "Scholastic"],
        "price_range": (5, 60),
    },
    "Home": {
        "subcats": {
            "Kitchen": ["Non-Stick Pan Set", "Blender Pro"],
            "Decor": ["Wall Art Canvas", "Table Lamp"],
            "Bedding": ["Cotton Bedsheet Set", "Memory Foam Pillow"],
        },
        "brands": ["Prestige", "Philips", "IKEA"],
        "price_range": (10, 300),
    },
    "Beauty": {
        "subcats": {
            "Skincare": ["Vitamin C Serum", "Moisturizer Cream"],
            "Makeup": ["Matte Lipstick", "Foundation Kit"],
            "Haircare": ["Argan Oil Shampoo", "Hair Straightener"],
        },
        "brands": ["Lakme", "L'Oreal", "Nivea", "Maybelline"],
        "price_range": (5, 120),
    },
    "Grocery": {
        "subcats": {
            "Snacks": ["Mixed Nuts Pack", "Potato Chips"],
            "Beverages": ["Green Tea Box", "Coffee Beans"],
            "Staples": ["Basmati Rice 5kg", "Olive Oil 1L"],
        },
        "brands": ["Nestle", "Tata", "Cargill"],
        "price_range": (2, 40),
    },
}
CATEGORY_NAMES = list(CATEGORIES.keys())

PAYMENT_METHODS = ["Credit Card", "Debit Card", "UPI", "PayPal", "Net Banking", "Cash on Delivery"]
ORDER_PRIORITIES = ["Low", "Medium", "High", "Critical"]
SHIPPING_MODES = ["Standard", "Express", "Same Day", "Economy"]
CUSTOMER_SEGMENTS = ["Consumer", "Corporate", "Home Office", "Small Business"]

COLUMNS = [
    "OrderID", "CustomerID", "OrderDate", "ShipDate", "Year", "Month", "Day",
    "Country", "State", "City", "Region", "Category", "SubCategory",
    "ProductName", "Brand", "Quantity", "UnitPrice", "Discount", "Sales",
    "Profit", "PaymentMethod", "OrderPriority", "ShippingMode",
    "CustomerSegment", "Returned",
]

ORDER_DATE_START = date(2022, 1, 1)
ORDER_DATE_END = date(2026, 12, 31)
DATE_RANGE_DAYS = (ORDER_DATE_END - ORDER_DATE_START).days
CUSTOMER_POOL_SIZE = 500_000  # repeat-purchase realism: fewer customers than orders


def make_row(order_index):
    """Build one CSV row (as a list) for the given sequential order index."""
    order_id = f"ORD-{order_index:08d}"
    customer_id = f"CUST-{random.randint(1, CUSTOMER_POOL_SIZE):06d}"

    order_date = ORDER_DATE_START + timedelta(days=random.randint(0, DATE_RANGE_DAYS))
    ship_date = order_date + timedelta(days=random.randint(1, 10))

    country = random.choice(COUNTRY_NAMES)
    country_info = COUNTRIES[country]
    state = random.choice(list(country_info["states"].keys()))
    city = random.choice(country_info["states"][state])
    region = country_info["region"]

    category = random.choice(CATEGORY_NAMES)
    cat_info = CATEGORIES[category]
    subcategory = random.choice(list(cat_info["subcats"].keys()))
    product_name = random.choice(cat_info["subcats"][subcategory])
    brand = random.choice(cat_info["brands"])

    quantity = random.randint(1, 10)
    unit_price = round(random.uniform(*cat_info["price_range"]), 2)
    # Mostly no discount, occasionally a promo discount
    discount = random.choice([0, 0, 0, 0, 0.05, 0.1, 0.15, 0.2, 0.25])
    sales = round(quantity * unit_price * (1 - discount), 2)
    # Profit margin usually positive, occasionally a loss (clearance / high shipping cost)
    profit_margin = random.uniform(-0.10, 0.35)
    profit = round(sales * profit_margin, 2)

    payment_method = random.choice(PAYMENT_METHODS)
    order_priority = random.choice(ORDER_PRIORITIES)
    shipping_mode = random.choice(SHIPPING_MODES)
    customer_segment = random.choice(CUSTOMER_SEGMENTS)
    returned = random.choices(["No", "Yes"], weights=[92, 8])[0]

    return [
        order_id, customer_id,
        order_date.isoformat(), ship_date.isoformat(),
        order_date.year, order_date.month, order_date.day,
        country, state, city, region,
        category, subcategory, product_name, brand,
        quantity, unit_price, discount, sales, profit,
        payment_method, order_priority, shipping_mode,
        customer_segment, returned,
    ]


def write_csv(path, num_rows, progress_every=500_000):
    """Stream `num_rows` generated rows to `path`. Returns elapsed seconds."""
    start = time.time()
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNS)
        for i in range(1, num_rows + 1):
            writer.writerow(make_row(i))
            if progress_every and i % progress_every == 0:
                elapsed = time.time() - start
                print(f"  ... {i:,} / {num_rows:,} rows written ({elapsed:.1f}s elapsed)")
    return time.time() - start


def main():
    print("Step 1/2 — Calibration: measuring real bytes-per-row")
    print(f"  Writing {CALIBRATION_ROWS:,} sample rows to {CALIBRATION_PATH} ...")
    write_csv(CALIBRATION_PATH, CALIBRATION_ROWS, progress_every=0)

    calibration_size = os.path.getsize(CALIBRATION_PATH)
    bytes_per_row = calibration_size / CALIBRATION_ROWS
    print(f"  Calibration file size: {calibration_size:,} bytes")
    print(f"  Measured bytes/row:    {bytes_per_row:.2f}")

    target_rows = int(TARGET_BYTES / bytes_per_row)
    if target_rows < MIN_ROWS:
        print(f"  NOTE: byte-target implies {target_rows:,} rows, below the "
              f"{MIN_ROWS:,} row floor — using {MIN_ROWS:,} rows instead "
              f"(final file will likely exceed {TARGET_MAX_BYTES/1e6:.0f}MB).")
        target_rows = MIN_ROWS
    elif target_rows > MAX_ROWS:
        print(f"  NOTE: byte-target implies {target_rows:,} rows, above the "
              f"{MAX_ROWS:,} row ceiling — using {MAX_ROWS:,} rows instead "
              f"(final file will likely be under {TARGET_MIN_BYTES/1e6:.0f}MB).")
        target_rows = MAX_ROWS

    os.remove(CALIBRATION_PATH)

    print(f"\nStep 2/2 — Generating full dataset: {target_rows:,} rows")
    print(f"  Writing to {OUTPUT_PATH} ...")
    elapsed = write_csv(OUTPUT_PATH, target_rows)

    final_size = os.path.getsize(OUTPUT_PATH)
    final_size_mb = final_size / 1_000_000
    final_size_gb = final_size / 1_000_000_000

    print("\n" + "=" * 60)
    print("DONE")
    print(f"  Rows written : {target_rows:,}")
    print(f"  File size    : {final_size:,} bytes  (~{final_size_mb:.1f} MB / ~{final_size_gb:.2f} GB)")
    print(f"  Time taken   : {elapsed:.1f}s")
    in_range = TARGET_MIN_BYTES <= final_size <= TARGET_MAX_BYTES
    print(f"  In target range (900MB-1.1GB)? {'YES' if in_range else 'NO — see NOTE above if row count was clamped'}")
    print(f"  Output path  : {OUTPUT_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
