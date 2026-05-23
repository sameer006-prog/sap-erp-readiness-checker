# SAP ERP Migration Readiness Checker

Every SAP implementation hits the same bottleneck: the client hands you a folder of old Excel sheets and says, "Here's our master data." Then someone has to sit down and figure out how much of it is actually usable.

Missing VAT IDs. IBAN numbers with spaces. Postal codes that are four digits instead of five. Customer names duplicated 15 times because nobody cleaned the export. All of this needs to be found and fixed *before* the SAP import — otherwise the migration fails, the timeline gets pushed, and the client is unhappy.

This tool automates that initial quality check. You feed it the legacy CSV exports, and it tells you exactly what's broken, where it is, and how bad it is.

## What it checks

The script validates four entity types against the actual import requirements for SAP S/4HANA Cloud and SAP Business ByDesign:

* **Customer Master (~180 records):** Validates company name, address completeness, German postal codes (must be exactly 5 digits), VAT IDs (must be DE + 9 digits), IBAN format, and email syntax.
* **Supplier Master (~70 records):** Same checks as customers, plus specific vendor bank details.
* **Material Master (~130 records):** Checks material numbers, descriptions, units of measure, and material groups.
* **Open Items (AR/AP) (~350 records):** Validates document numbers, posting dates, due dates, amounts, currencies, and ensures partner references exist.

It flags issues using three severity levels:
* **CRITICAL:** A mandatory field is missing. The SAP import will hard-reject this record.
* **WARNING:** The field is filled but the format is wrong. SAP might misread it or truncate it.
* **INFO:** Potential duplicate detected. Needs a manual look before migration.

## Results on the test dataset

The repo includes a test dataset simulating a real German SME ("Hoffmann & Partner Maschinenbau GmbH") migrating from a legacy on-premise setup. About 25% of the records have deliberate quality problems—which is highly realistic for SME data.

```text
CUSTOMERS    |  180 records | Score:  79.9% | Critical:  16 | Warnings:  36 | Info:  29
SUPPLIERS    |   70 records | Score:  81.4% | Critical:   8 | Warnings:   9 | Info:   7
MATERIALS    |  130 records | Score:  71.1% | Critical:  36 | Warnings:   0 | Info:   8
OPEN_ITEMS   |  350 records | Score:  88.3% | Critical:  41 | Warnings:   0 | Info:   0

Total records checked:   730
Total issues found:      190
Average readiness score: 80.2%
```

A consultant doing this manually in Excel would spend 2-3 hours hunting these down (and would definitely miss a few). The 101 critical issues above would have caused direct SAP import failures. Catching them before go-live is the whole point of this script.

How to run it
No SAP system access needed. Everything runs locally.

Bash
pip install pandas openpyxl
python main.py
The output lands in output/Migration_Readiness_Report.xlsx.

The Output Report
The script generates a color-coded Excel workbook with five sheets:

Summary: A high-level overview with readiness scores per entity (Green = ready, Yellow = needs review, Red = not ready).

Detail Sheets (Customers / Suppliers / Materials / Open Items): Lists every single issue with the legacy record ID, the exact field name, the severity, and a plain-English explanation of what needs to be fixed.

The output is formatted so you can hand it directly to the client as a clean-up checklist.

Project structure
Plaintext
bradler_erp_checker/
├── main.py            - runs the full pipeline end to end
├── generate_data.py   - builds the synthetic SME legacy data
├── analyzer.py        - the validation engine + Excel export logic
├── data/              - CSV files land here (created on run)
└── output/            - Excel report lands here (created on run)

Why I built this
I built this project for my application for an SAP consulting trainee role focused on S/4HANA Cloud and Business ByDesign implementations.

Data migration pre-checks are usually one of the first hands-on tasks a trainee gets involved in. Building this tool was my way of getting familiar with the actual field structures and data constraints SAP expects, which is much more effective than just reading the documentation. It also highlights my approach to consulting: automate the tedious prep work so the team can focus on solving the actual business problems.
