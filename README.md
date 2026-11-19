# DataFix — Autonomous Data Engine

A Streamlit application for CSV data profiling, quality analysis, cleaning, repair, quarantine and export.

## Run locally or in GitHub Codespaces

```bash
pip install -r requirements.txt
streamlit run app.py --server.address 0.0.0.0
```

Open port 8501 in Codespaces.

## Features
- CSV upload and demo dataset
- Data quality profiling
- Missing value and duplicate detection
- Text standardization
- Missing value imputation
- Email and age validation
- Optional statistical outlier quarantine
- Cleaned data, quarantine and report downloads
- Audit log
