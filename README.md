# 🛠️ DataFix: Autonomous Data Quality & Repair Engine

## Problem Statement
Data analysts and organizations waste up to 80% of their time manually cleaning corrupted datasets. Duplicate entries, missing values, inconsistent formatting, and invalid records break downstream analytics and machine learning models.

## Our Solution
**DataFix** is an autonomous data quality and repair engine built in Python. Users upload any raw CSV file through an interactive Gradio web interface to automatically scan, repair, quarantine, and audit their data in seconds.

## Key Features
- **Automated Quality Scoring:** Calculates real-time Before and After Data Quality Scores.
- **Deduplication & Standardization:** Removes exact duplicate rows and fixes inconsistent text capitalization.
- **Outlier Detection & Smart Imputation:** Flags impossible numeric values and replaces missing or corrupted numbers using statistical medians.
- **Safe Quarantining:** Isolates unfixable records into a separate Quarantined CSV with clear reasons rather than guessing or deleting data.
- **Transparent Audit Log:** Records every automated modification step-by-step.

## Tech Stack
- **Language:** Python
- **Data Processing:** Pandas, NumPy, Regular Expressions (Regex)
- **Web Interface:** Gradio
- **Environment:** Google Colab
-
