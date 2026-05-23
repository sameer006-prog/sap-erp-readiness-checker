"""
generate_data.py

Generates synthetic legacy data for a fictional German SME:
"Hoffmann & Partner Maschinenbau GmbH"

This simulates the kind of data a company exports from an old system
(think: on-premise ERP, Access database, or just years of Excel sheets)
before moving to SAP S/4HANA Cloud or SAP Business ByDesign.

Four entity types:
    - Customer Master (~180 records)
    - Supplier Master (~70 records)
    - Material Master (~130 records)
    - Open Items / AR+AP (~350 records)

About 22-25% of records have deliberate quality problems --
missing mandatory fields, wrong formats, duplicates, blank emails.
That's realistic. Most SME migrations look exactly like this.
"""

import pandas as pd
import numpy as np
import random
import os

np.random.seed(7)
random.seed(7)

OUT = "data"
os.makedirs(OUT, exist_ok=True)

# German city/postal code pairs (real data)
CITIES = [
    ("10115", "Berlin"),
    ("20095", "Hamburg"),
    ("80331", "München"),
    ("50667", "Köln"),
    ("60311", "Frankfurt am Main"),
    ("70173", "Stuttgart"),
    ("40213", "Düsseldorf"),
    ("04109", "Leipzig"),
    ("28195", "Bremen"),
    ("30159", "Hannover"),
    ("68161", "Mannheim"),
    ("44135", "Dortmund"),
    ("45127", "Essen"),
    ("90402", "Nürnberg"),
    ("01067", "Dresden"),
    ("79098", "Freiburg im Breisgau"),
    ("76133", "Karlsruhe"),
    ("55116", "Mainz"),
    ("53111", "Bonn"),
    ("97070", "Würzburg"),
]

COMPANY_TYPES = ["GmbH", "AG", "KG", "GmbH & Co. KG", "OHG", "e.K."]
INDUSTRIES = ["Maschinenbau", "Handel", "Logistik", "Automotive", "IT", "Chemie", "Bau", "Textil"]
STREETS = ["Hauptstraße", "Industriestraße", "Bahnhofstraße", "Schillerstraße",
           "Goethestraße", "Ringstraße", "Marktplatz", "Gartenstraße"]
PAYMENT_TERMS = ["NET30", "NET14", "NET60", "2/10NET30", "IMMEDIATE"]
CURRENCIES = ["EUR", "EUR", "EUR", "EUR", "USD", "CHF"]  # weighted toward EUR
UNITS = ["ST", "KG", "M", "L", "PCE", "SET", "BOX"]
MAT_GROUPS = ["ROH", "HALB", "FERT", "VERP", "HILF", "DIENSTL"]


def _company_name():
    surnames = ["Müller", "Schmidt", "Hoffmann", "Weber", "Fischer", "Koch",
                "Wagner", "Becker", "Schulz", "Meyer", "Wolf", "Schäfer",
                "Kaiser", "Richter", "Klein", "Lang", "Schwarz", "Braun"]
    s1 = random.choice(surnames)
    s2 = random.choice(surnames)
    ind = random.choice(INDUSTRIES)
    ctype = random.choice(COMPANY_TYPES)

    patterns = [
        f"{s1} {ctype}",
        f"{s1} & {s2} {ctype}",
        f"{s1} {ind} {ctype}",
        f"{ind}betrieb {s1} {ctype}",
    ]
    return random.choice(patterns)


def _street_address():
    return f"{random.choice(STREETS)} {random.randint(1, 150)}"


def _phone():
    area = random.choice(["030", "040", "089", "0221", "069", "0711", "0621", "0231"])
    number = random.randint(1000000, 9999999)
    return f"+49 {area} {number}"


def _email(company_name):
    domain_base = company_name.lower().split()[0]
    domain_base = "".join(c for c in domain_base if c.isalpha())
    tld = random.choice(["de", "com", "net"])
    return f"info@{domain_base}.{tld}"


def _vat_id(broken=False):
    if broken:
        # Common mistakes: wrong length, missing DE prefix, all zeros
        bad = [
            f"{random.randint(100000000, 999999999)}",   # missing DE
            f"DE{random.randint(10000000, 99999999)}",   # only 8 digits
            "DE000000000",                               # zero padding
            "",                                          # blank
        ]
        return random.choice(bad)
    return f"DE{random.randint(100000000, 999999999)}"


def _iban(broken=False):
    if broken:
        bad = [
            f"DE{random.randint(10, 99)}{random.randint(10000000, 99999999)}",  # too short
            f"DE{random.randint(10, 99)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}",  # spaces
            "",
        ]
        return random.choice(bad)

    bank = random.randint(10000000, 99999999)
    account = random.randint(1000000000, 9999999999)
    check = random.randint(10, 99)
    return f"DE{check}{bank}{account}"


# --- 1. CUSTOMER MASTER ---

def generate_customers(n=180):
    rows = []
    seen_names = {}

    for i in range(n):
        city_zip = random.choice(CITIES)
        name = _company_name()

        # ~8% duplicates (same company submitted twice with slight variation)
        is_duplicate = i > 20 and random.random() < 0.08 and seen_names
        if is_duplicate:
            name = random.choice(list(seen_names.keys()))

        seen_names[name] = True

        # Introduce quality issues in ~25% of records
        issue_roll = random.random()

        vat = _vat_id(broken=(issue_roll < 0.18))
        iban = _iban(broken=(issue_roll < 0.12))
        email = _email(name) if issue_roll > 0.10 else ""
        phone = _phone() if issue_roll > 0.07 else ""
        postal = city_zip[0] if issue_roll > 0.05 else ""
        city = city_zip[1] if issue_roll > 0.04 else ""

        rows.append({
            "LEGACY_ID": f"KD-{10000 + i}",
            "COMPANY_NAME": name,
            "STREET": _street_address(),
            "POSTAL_CODE": postal,
            "CITY": city,
            "COUNTRY": "DE",
            "PHONE": phone,
            "EMAIL": email,
            "VAT_ID": vat,
            "IBAN": iban,
            "PAYMENT_TERMS": random.choice(PAYMENT_TERMS),
            "CREDIT_LIMIT": round(random.uniform(5000, 200000), 2),
            "CURRENCY": "EUR",
        })

    return pd.DataFrame(rows)


# --- 2. SUPPLIER MASTER ---

def generate_suppliers(n=70):
    rows = []
    seen = {}

    for i in range(n):
        city_zip = random.choice(CITIES)
        name = _company_name()

        is_dup = i > 10 and random.random() < 0.07 and seen
        if is_dup:
            name = random.choice(list(seen.keys()))
        seen[name] = True

        issue_roll = random.random()

        rows.append({
            "LEGACY_ID": f"LF-{20000 + i}",
            "COMPANY_NAME": name,
            "STREET": _street_address(),
            "POSTAL_CODE": city_zip[0] if issue_roll > 0.06 else "",
            "CITY": city_zip[1] if issue_roll > 0.05 else "",
            "COUNTRY": "DE",
            "PHONE": _phone() if issue_roll > 0.08 else "",
            "EMAIL": _email(name) if issue_roll > 0.09 else "",
            "VAT_ID": _vat_id(broken=(issue_roll < 0.15)),
            "IBAN": _iban(broken=(issue_roll < 0.10)),
            "PAYMENT_TERMS": random.choice(PAYMENT_TERMS),
            "CURRENCY": "EUR",
        })

    return pd.DataFrame(rows)


# --- 3. MATERIAL MASTER ---

MATERIAL_PREFIXES = ["Schraube", "Ventil", "Rohr", "Flansch", "Dichtung",
                     "Lager", "Gehäuse", "Pumpe", "Sensor", "Kabel",
                     "Platte", "Profil", "Buchse", "Feder", "Zylinder"]

def generate_materials(n=130):
    rows = []
    seen_mats = set()

    for i in range(n):
        prefix = random.choice(MATERIAL_PREFIXES)
        suffix = f"{random.randint(10, 99)}-{random.randint(100, 999)}"
        desc = f"{prefix} {suffix}"

        # ~ 6% duplicate material descriptions
        is_dup = i > 20 and random.random() < 0.06 and seen_mats
        if is_dup:
            desc = random.choice(list(seen_mats))
        seen_mats.add(desc)

        issue_roll = random.random()

        rows.append({
            "MATERIAL_NUMBER": f"MAT-{30000 + i}",
            "DESCRIPTION": desc,
            "UNIT": random.choice(UNITS) if issue_roll > 0.08 else "",
            "MATERIAL_GROUP": random.choice(MAT_GROUPS) if issue_roll > 0.06 else "",
            "LIST_PRICE": round(random.uniform(0.50, 4500.00), 2),
            "CURRENCY": "EUR",
            "WEIGHT_KG": round(random.uniform(0.01, 150.0), 3) if issue_roll > 0.12 else None,
            "ACTIVE": "Y" if random.random() > 0.05 else "",  # 5% missing active flag
        })

    return pd.DataFrame(rows)


# --- 4. OPEN ITEMS (AR + AP) ---

def generate_open_items(customers, suppliers, n=350):
    rows = []
    cust_ids = customers["LEGACY_ID"].tolist()
    supp_ids = suppliers["LEGACY_ID"].tolist()

    for i in range(n):
        is_ar = random.random() > 0.4   # 60% AR, 40% AP
        partner_id = random.choice(cust_ids) if is_ar else random.choice(supp_ids)
        post_year = random.randint(2023, 2024)
        post_month = random.randint(1, 12)
        post_day = random.randint(1, 28)
        posting_date = f"{post_year}-{post_month:02d}-{post_day:02d}"

        due_days = int(random.choice([14, 30, 60, 90]))
        due_year = post_year + (1 if post_month + 1 > 12 else 0)
        due_month = (post_month + 1) % 12 or 12
        due_date = f"{due_year}-{due_month:02d}-{post_day:02d}"

        issue_roll = random.random()

        rows.append({
            "DOCUMENT_NUMBER": f"{'AR' if is_ar else 'AP'}-{40000 + i}",
            "TYPE": "AR" if is_ar else "AP",
            "PARTNER_ID": partner_id,
            "POSTING_DATE": posting_date if issue_roll > 0.05 else "",
            "DUE_DATE": due_date if issue_roll > 0.06 else "",
            "GROSS_AMOUNT": round(random.uniform(150, 85000), 2),
            "CURRENCY": random.choice(CURRENCIES),
            "PAYMENT_TERMS": random.choice(PAYMENT_TERMS) if issue_roll > 0.08 else "",
            "COST_CENTER": f"CC-{random.randint(100, 999)}" if random.random() > 0.3 else "",
            "TAX_CODE": random.choice(["V1", "V2", "A1", ""]),
        })

    return pd.DataFrame(rows)


# --- ENTRY POINT ---

if __name__ == "__main__":
    print("Generating legacy data for Hoffmann & Partner Maschinenbau GmbH...")

    customers = generate_customers(180)
    suppliers = generate_suppliers(70)
    materials = generate_materials(130)
    open_items = generate_open_items(customers, suppliers, 350)

    customers.to_csv(f"{OUT}/customers.csv", index=False)
    suppliers.to_csv(f"{OUT}/suppliers.csv", index=False)
    materials.to_csv(f"{OUT}/materials.csv", index=False)
    open_items.to_csv(f"{OUT}/open_items.csv", index=False)

    print(f"  customers:  {len(customers)} records  -> data/customers.csv")
    print(f"  suppliers:  {len(suppliers)} records  -> data/suppliers.csv")
    print(f"  materials:  {len(materials)} records  -> data/materials.csv")
    print(f"  open items: {len(open_items)} records  -> data/open_items.csv")
    print("Done.")