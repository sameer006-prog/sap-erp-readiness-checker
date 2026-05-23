"""
main.py

Run this to execute the full pipeline:
    1. Generate synthetic legacy data
    2. Run SAP migration readiness checks
    3. Export color-coded Excel report

Usage:
    pip install pandas openpyxl
    python main.py
"""

import os
from generate_data import generate_customers, generate_suppliers, generate_materials, generate_open_items
from analyzer import run_analysis

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs("output", exist_ok=True)

print("-" * 50)
print("SAP Cloud ERP Migration Readiness Checker")
print("Client: Hoffmann & Partner Maschinenbau GmbH")
print("Target: SAP S/4HANA Cloud / SAP Business ByDesign")
print("-" * 50)

# step 1: generate data
print("\n[1/2] Generating legacy data export...")
customers = generate_customers(180)
suppliers = generate_suppliers(70)
materials = generate_materials(130)
open_items = generate_open_items(customers, suppliers, 350)

customers.to_csv(f"{DATA_DIR}/customers.csv", index=False)
suppliers.to_csv(f"{DATA_DIR}/suppliers.csv", index=False)
materials.to_csv(f"{DATA_DIR}/materials.csv", index=False)
open_items.to_csv(f"{DATA_DIR}/open_items.csv", index=False)

total = len(customers) + len(suppliers) + len(materials) + len(open_items)
print(f"  -> {total} records across 4 entity types loaded.")

# step 2 & 3: analyze and export report
print("\n[2/2] Running SAP field validation...")
results, avg_score = run_analysis()

print("\nDone. Open output/Migration_Readiness_Report.xlsx to review.")