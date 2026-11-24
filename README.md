# PeoplePulse AI — Advanced HR Analytics Portfolio

A modular, interactive Streamlit portfolio project for descriptive workforce analytics, attrition exploration, retention cohorts, educational model evaluation, SQL analysis, and data-quality governance.

> **Data notice:** The included dataset is synthetic demonstration data. Findings are illustrative associations, not causal conclusions. The classifier is educational and must never be used to make decisions about hiring, firing, promotion, compensation, or individual employees.

## The eight sections

All eight sections are displayed in the top navigation bar:

1. **Executive Overview** — workforce KPIs, department distribution, attrition comparisons, transparent rule-based observations.
2. **Workforce Explorer** — employee composition, salary and tenure distributions, searchable employee table, CSV export.
3. **Attrition Intelligence** — segment-level attrition rates, exit counts, group-size context, exportable results.
4. **Retention & Cohorts** — hire-year retention view and tenure-segment comparisons.
5. **Predictive Analytics** — train/test pipeline, Logistic Regression / Random Forest / HistGradientBoosting, precision, recall, F1, ROC-AUC, confusion matrix, permutation importance, metrics export.
6. **SQL Analytics** — read-only SQL workbench over a local SQLite database with example queries and CSV export.
7. **Data Quality & Governance** — missingness profile, schema inspection, duplicate-ID and domain checks, responsible-use guidance.
8. **Project Notes** — architecture, limitations, and run instructions.

## Project structure

```text
PeoplePulse_AI_Advanced/
├── app.py
├── requirements.txt
├── runtime.txt
├── README.md
├── .env.example
├── .gitignore
├── data/
│   ├── cleaned_data.csv
│   ├── raw_data.csv
│   ├── department_reference.csv
│   └── job_role_reference.csv
├── src/
│   ├── data.py
│   ├── analytics.py
│   ├── database.py
│   └── modeling.py
├── tests/
│   └── test_core.py
├── sql/
├── powerbi/
└── docs/
```

## Run on Windows / VS Code

Open the extracted `PeoplePulse_AI_Advanced` folder in VS Code. Open Terminal and run:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

If PowerShell blocks activation, run this once in the same terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Then open the local URL printed by Streamlit (normally `http://localhost:8501`).

## Run tests

```powershell
python -m pytest -q
```

## Data configuration

By default, the app reads `data/cleaned_data.csv`. You can set `DATA_PATH` in a local `.env` file; use `.env.example` as a reference. Do not commit private data or secrets.

## Database

The SQL lab creates `data/peoplepulse.db` locally from the cleaned CSV on first use. SQLite is included with Python; no MySQL server is configured in this release. The SQL helper restricts execution to read-only SELECT/WITH statements.

## Model methodology

The modeling module uses a stratified holdout split and preprocessing within a scikit-learn pipeline. Employee identifiers and exit-year leakage fields are excluded from the model feature list. Model performance is reported using multiple metrics because accuracy alone can hide poor minority-class recall. Results can vary with package versions and random splits.

## Deployment to Streamlit Community Cloud

1. Create a GitHub repository and upload this project folder.
2. Do **not** upload `.venv/`, `.env`, `data/peoplepulse.db`, `__pycache__/`, or `.pytest_cache/`.
3. In Streamlit Community Cloud, choose the repository and branch.
4. Set the app entrypoint to `app.py`.
5. Add any required environment variables in the deployment secrets/settings only if you use them.
6. Deploy and verify all eight navigation sections.

## Honest scope / not implemented

This is an advanced educational portfolio project, not a production HR information system. This version does **not** implement MySQL connectivity, SHAP, user login/RBAC, cloud-hosted database persistence, CI/CD, model monitoring, PDF report generation, survival analysis, or individual employee risk scoring. Do not describe these as completed features in a resume or interview.

## Suggested portfolio description

**PeoplePulse AI — Advanced HR Analytics Platform:** Built a modular Streamlit analytics application featuring eight interactive sections, workforce and attrition analysis, retention cohort views, a SQLite SQL lab, data-quality governance, and scikit-learn model evaluation with explainability via permutation importance. Used synthetic demonstration data and documented responsible-use limitations.
