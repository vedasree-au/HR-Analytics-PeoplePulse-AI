
from pathlib import Path
import os
import json

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from src.data import (
    load_employee_data,
    validate_employee_data,
    build_data_quality_report,
)
from src.analytics import (
    kpi_summary,
    attrition_by,
    retention_cohorts,
    workforce_segments,
    run_sql_query,
)
from src.database import initialize_database
from src.modeling import train_attrition_model, model_report


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

load_dotenv()

ROOT = Path(__file__).parent
DATA = Path(os.getenv("DATA_PATH", ROOT / "data" / "cleaned_data.csv"))

st.set_page_config(
    page_title="PeoplePulse AI | HR Intelligence",
    page_icon="🧭",
    layout="wide",
)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>

.stApp {
    background: radial-gradient(
        circle at 10% 0%,
        #1c3559 0%,
        #0b1424 44%,
        #08111f 100%
    );
}

[data-testid="stSidebar"] {
    background: #0d192b;
    border-right: 1px solid #263957;
}

.block-container {
    padding-top: 1.1rem;
    max-width: 1600px;
}

[data-testid="stMetric"] {
    background: linear-gradient(145deg, #152744, #101c31);
    border: 1px solid #2a4164;
    padding: 14px;
    border-radius: 14px;
}

.hero {
    padding: 20px 24px;
    border: 1px solid #2c456b;
    border-radius: 18px;
    background: linear-gradient(110deg, #224069, #111e34);
    margin: 8px 0 18px;
}

.muted {
    color: #b5c5df;
}

div[data-testid="stRadio"] > div {
    gap: 7px;
}

div[data-testid="stRadio"] label {
    background: #14243b;
    border: 1px solid #2b4262;
    border-radius: 9px;
    padding: 8px 11px;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# NAVIGATION
# --------------------------------------------------

PAGES = [
    "Executive Overview",
    "Workforce Explorer",
    "Attrition Intelligence",
    "Retention & Cohorts",
    "Predictive Analytics",
    "SQL Analytics",
    "Data Quality & Governance",
    "Project Notes",
]


# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------

@st.cache_data(show_spinner=False)
def get_data(path, modified):
    return load_employee_data(path)


if not DATA.exists():
    st.error(
        f"Dataset not found: {DATA}. "
        "Check DATA_PATH or restore data/cleaned_data.csv."
    )
    st.stop()

try:
    df = get_data(str(DATA), DATA.stat().st_mtime)

except Exception as exc:
    st.error("Unable to load employee dataset.")
    st.exception(exc)
    st.stop()


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def heading(title, subtitle):
    st.markdown(
        f"""
        <div class="hero">
            <h1 style="margin:0">{title}</h1>
            <div class="muted">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpis(data):
    k = kpi_summary(data)

    items = [
        ("Employees", f'{k["employees"]:,}'),
        ("Attrition rate", f'{k["attrition_rate"]:.1%}'),
        ("Average age", f'{k["average_age"]:.1f}'),
        ("Avg. monthly salary", f'{k["average_salary"]:,.0f}'),
        ("Average tenure", f'{k["average_tenure"]:.1f} yrs'),
    ]

    cols = st.columns(5)

    for col, (label, value) in zip(cols, items):
        col.metric(label, value)


def csv_download(
    data,
    label="Download CSV",
    filename="peoplepulse_export.csv",
):
    st.download_button(
        label=label,
        data=data.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
        width="content",
    )


def rule_based_insights(data):
    """
    Transparent descriptive observations.
    These are not generative AI predictions or causal findings.
    """

    notes = []

    if data.empty:
        return ["No rows match the current filters."]

    if "Overtime" in data and "Attrition" in data:

        rates = data.groupby("Overtime")["Attrition"].apply(
            lambda x: (x == "Yes").mean()
        )

        if len(rates) > 1:
            high = rates.idxmax()

            notes.append(
                f"Overtime group '{high}' has the highest observed "
                f"attrition rate ({rates[high]:.1%}) "
                "in the filtered data."
            )

    if "Department" in data:

        rates = attrition_by(data, "Department")

        if not rates.empty:

            top = rates.sort_values(
                "attrition_rate",
                ascending=False,
            ).iloc[0]

            notes.append(
                f"{top['Department']} has the highest observed "
                f"department attrition rate "
                f"({top['attrition_rate']:.1%}); "
                "check group size before interpreting."
            )

    if "JobSatisfaction" in data:

        low = data[
            data["JobSatisfaction"]
            == data["JobSatisfaction"].min()
        ]

        if len(low):

            rate = (low["Attrition"] == "Yes").mean()

            notes.append(
                f"The lowest satisfaction score group has an "
                f"observed attrition rate of {rate:.1%}. "
                "This is an association, not evidence of cause."
            )

    return notes or [
        "Not enough variation in the filtered data "
        "to produce descriptive observations."
    ]


# --------------------------------------------------
# DATA VALIDATION
# --------------------------------------------------

issues = validate_employee_data(df)


# --------------------------------------------------
# APPLICATION HEADER
# --------------------------------------------------

st.markdown("## 🧭 PeoplePulse AI")

st.caption(
    "Advanced HR analytics portfolio platform "
    "· Synthetic demonstration dataset"
)


# --------------------------------------------------
# TOP NAVIGATION
# --------------------------------------------------

page = st.radio(
    "Explore all 8 sections",
    PAGES,
    horizontal=True,
    label_visibility="visible",
)


# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

with st.sidebar:

    st.markdown("### Global filters")

    departments = (
        sorted(df["Department"].dropna().astype(str).unique())
        if "Department" in df
        else []
    )

    genders = (
        sorted(df["Gender"].dropna().astype(str).unique())
        if "Gender" in df
        else []
    )

    outcomes = (
        sorted(df["Attrition"].dropna().astype(str).unique())
        if "Attrition" in df
        else []
    )

    selected_departments = st.multiselect(
        "Department",
        departments,
        default=departments,
    )

    selected_genders = st.multiselect(
        "Gender",
        genders,
        default=genders,
    )

    selected_outcomes = st.multiselect(
        "Employment outcome",
        outcomes,
        default=outcomes,
    )

    st.divider()

    st.caption(f"Source rows: {len(df):,}")


# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------

filtered = df[
    df["Department"].astype(str).isin(selected_departments)
    & df["Gender"].astype(str).isin(selected_genders)
    & df["Attrition"].astype(str).isin(selected_outcomes)
].copy()

with st.sidebar:
    st.caption(f"Filtered rows: {len(filtered):,}")


# --------------------------------------------------
# EMPTY FILTER CHECK
# --------------------------------------------------

if filtered.empty and page not in [
    "Data Quality & Governance",
    "Project Notes",
]:

    st.warning(
        "No employees match your selected filters. "
        "Please change the sidebar filters."
    )
    st.stop()


# ==================================================
# 1. EXECUTIVE OVERVIEW
# ==================================================

if page == "Executive Overview":

    heading(
        "Executive Overview",
        "A decision-support overview of workforce composition, "
        "retention patterns and business-facing signals.",
    )

    kpis(filtered)

    a, b = st.columns(2)

    with a:

        department_count = (
            filtered.groupby("Department")
            .size()
            .reset_index(name="employees")
        )

        st.plotly_chart(
            px.bar(
                department_count,
                x="Department",
                y="employees",
                color="Department",
                title="Workforce by Department",
            ),
            width="stretch",
        )

    with b:

        st.plotly_chart(
            px.bar(
                attrition_by(filtered, "Department"),
                x="Department",
                y="attrition_rate",
                color="attrition_rate",
                title="Observed Attrition Rate by Department",
            ),
            width="stretch",
        )

    a, b = st.columns(2)

    with a:

        st.plotly_chart(
            px.histogram(
                filtered,
                x="Age",
                color="Attrition",
                barmode="overlay",
                title="Age Profile by Employment Outcome",
            ),
            width="stretch",
        )

    with b:

        st.plotly_chart(
            px.bar(
                attrition_by(filtered, "Overtime"),
                x="Overtime",
                y="attrition_rate",
                color="Overtime",
                title="Observed Attrition by Overtime",
            ),
            width="stretch",
        )

    st.subheader("Automated Descriptive Observations")

    st.caption(
        "Transparent rule-based observations, "
        "not generative AI or causal findings."
    )

    for note in rule_based_insights(filtered):
        st.info(note)

    csv_download(filtered)


# ==================================================
# 2. WORKFORCE EXPLORER
# ==================================================

elif page == "Workforce Explorer":

    heading(
        "Workforce Explorer",
        "Explore employee mix, compensation, experience and satisfaction.",
    )

    kpis(filtered)

    a, b = st.columns(2)

    with a:

        st.plotly_chart(
            px.sunburst(
                filtered,
                path=["Department", "JobRole"],
                title="Department and Job Role Composition",
            ),
            width="stretch",
        )

    with b:

        st.plotly_chart(
            px.box(
                filtered,
                x="Department",
                y="MonthlySalary",
                color="Department",
                title="Monthly Salary Distribution",
            ),
            width="stretch",
        )

    a, b = st.columns(2)

    with a:

        st.plotly_chart(
            px.histogram(
                filtered,
                x="YearsAtCompany",
                color="Attrition",
                barmode="overlay",
                title="Tenure Distribution",
            ),
            width="stretch",
        )

    with b:

        satisfaction = (
            filtered.groupby("JobSatisfaction")
            .agg(
                employees=("EmployeeID", "count"),
                attrition_rate=(
                    "Attrition",
                    lambda x: (x == "Yes").mean(),
                ),
            )
            .reset_index()
        )

        st.plotly_chart(
            px.bar(
                satisfaction,
                x="JobSatisfaction",
                y="attrition_rate",
                title="Observed Attrition by Satisfaction Score",
            ),
            width="stretch",
        )

    st.subheader("Employee Search")

    search = st.text_input(
        "Search employee ID, department or job role"
    )

    view = filtered.copy()

    if search:

        view = view[
            view.astype(str)
            .apply(
                lambda col: col.str.contains(
                    search,
                    case=False,
                    na=False,
                )
            )
            .any(axis=1)
        ]

    columns = [
        c for c in [
            "EmployeeID",
            "Age",
            "Gender",
            "Department",
            "JobRole",
            "MonthlySalary",
            "YearsAtCompany",
            "JobSatisfaction",
            "Overtime",
            "Attrition",
        ]
        if c in view.columns
    ]

    st.dataframe(
        view[columns],
        width="stretch",
        hide_index=True,
    )

    csv_download(view)


# ==================================================
# 3. ATTRITION INTELLIGENCE
# ==================================================

elif page == "Attrition Intelligence":

    heading(
        "Attrition Intelligence",
        "Segment exits, compare rates and inspect where attrition is concentrated.",
    )

    kpis(filtered)

    segment = st.selectbox(
        "Analyze attrition by",
        [
            "Department",
            "JobRole",
            "AgeGroup",
            "SalaryBand",
            "ExperienceBand",
            "Overtime",
            "Education",
            "Gender",
            "JobSatisfaction",
        ],
    )

    result = attrition_by(
        filtered,
        segment,
    ).sort_values(
        "attrition_rate",
        ascending=False,
    )

    st.plotly_chart(
        px.bar(
            result,
            x=segment,
            y="attrition_rate",
            color="attrition_rate",
            color_continuous_scale="Reds",
            hover_data=["employees", "attrition_count"],
            title=f"Attrition Rate by {segment}",
        ),
        width="stretch",
    )

    st.subheader("Segment Analysis")

    st.dataframe(
        result,
        width="stretch",
        hide_index=True,
    )

    st.caption(
        "Always inspect denominator/group size. "
        "Small segments can have unstable rates; "
        "these are descriptive associations."
    )

    csv_download(
        result,
        filename="attrition_segment_analysis.csv",
    )


# ==================================================
# 4. RETENTION & COHORTS
# ==================================================

elif page == "Retention & Cohorts":

    heading(
        "Retention & Cohorts",
        "Compare observed retention across hire-year cohorts "
        "and tenure segments.",
    )

    cohort = retention_cohorts(filtered)

    if not cohort.empty:

        st.plotly_chart(
            px.line(
                cohort,
                x="HireYear",
                y="retention_rate",
                markers=True,
                title="Observed Retention by Hire Cohort",
            ),
            width="stretch",
        )

        st.dataframe(
            cohort,
            width="stretch",
            hide_index=True,
        )

    else:

        st.warning(
            "No cohort data is available under the current filters."
        )

    segments = workforce_segments(
        filtered,
        "YearsAtCompany",
        [0, 1, 3, 5, 10, 100],
        [
            "<1 year",
            "1–2 years",
            "3–4 years",
            "5–9 years",
            "10+ years",
        ],
    )

    st.plotly_chart(
        px.bar(
            segments,
            x="segment",
            y="attrition_rate",
            color="attrition_rate",
            title="Observed Attrition by Tenure Segment",
        ),
        width="stretch",
    )

    st.dataframe(
        segments,
        width="stretch",
        hide_index=True,
    )

    st.caption(
        "This is a cross-sectional cohort comparison, "
        "not Kaplan–Meier survival analysis; "
        "complete event-time histories are unavailable."
    )

    csv_download(
        cohort,
        filename="retention_cohorts.csv",
    )


# ==================================================
# 5. PREDICTIVE ANALYTICS
# ==================================================

elif page == "Predictive Analytics":

    heading(
        "Predictive Analytics",
        "Train, validate and explain an educational attrition classification model.",
    )

    st.warning(
        "Synthetic data only. This is not a validated HR risk model. "
        "Do not use for hiring, firing, promotion, pay, "
        "or individual employment decisions."
    )

    features = [
        c for c in [
            "Age",
            "Gender",
            "Department",
            "JobRole",
            "MonthlySalary",
            "Education",
            "YearsExperience",
            "YearsAtCompany",
            "JobSatisfaction",
            "Overtime",
            "PerformanceRating",
            "AgeGroup",
            "SalaryBand",
            "ExperienceBand",
        ]
        if c in df.columns
    ]

    chosen = st.multiselect(
        "Predictor Features",
        features,
        default=features,
    )

    algorithm = st.selectbox(
        "Algorithm",
        [
            "Random Forest",
            "Logistic Regression",
            "HistGradientBoosting",
        ],
    )

    test_size = st.slider(
        "Holdout Test Proportion",
        0.20,
        0.40,
        0.25,
        0.05,
    )

    if st.button(
        "Train and Evaluate Model",
        type="primary",
        disabled=not chosen,
    ):

        try:

            st.session_state["pp_model"] = train_attrition_model(
                df,
                chosen,
                algorithm,
                test_size,
            )

        except Exception as exc:

            st.error(f"Model training failed: {exc}")

    artifact = st.session_state.get("pp_model")

    if artifact:

        report = model_report(artifact)

        st.subheader("Holdout Evaluation")

        cols = st.columns(5)

        for col, key in zip(
            cols,
            ["accuracy", "precision", "recall", "f1", "roc_auc"],
        ):

            value = report["metrics"].get(key)

            col.metric(
                key.upper(),
                f"{value:.3f}" if value is not None else "N/A",
            )

        a, b = st.columns(2)

        with a:

            st.plotly_chart(
                px.imshow(
                    report["confusion_matrix"],
                    text_auto=True,
                    x=["Predicted stay", "Predicted exit"],
                    y=["Actual stay", "Actual exit"],
                    title="Confusion Matrix",
                    color_continuous_scale="Blues",
                ),
                width="stretch",
            )

        with b:

            st.plotly_chart(
                px.bar(
                    report["importance"].head(15),
                    x="importance",
                    y="feature",
                    orientation="h",
                    title="Permutation Importance (Holdout)",
                ),
                width="stretch",
            )

        st.subheader("Classification Report")

        st.code(report["classification_report"])

        st.caption(
            f"Holdout rows: {report['test_rows']:,}; "
            "positive class: Attrition = Yes. "
            "Metrics may vary by environment and split."
        )

        st.download_button(
            "Download Model Metrics",
            json.dumps(report["metrics"], indent=2),
            "model_metrics.json",
            "application/json",
        )

    else:

        st.info(
            "Choose features and train a model "
            "to view holdout evaluation."
        )


# ==================================================
# 6. SQL ANALYTICS
# ==================================================

elif page == "SQL Analytics":

    heading(
        "SQL Analytics Lab",
        "Run read-only SQL against the local SQLite analytical database.",
    )

    db_path = ROOT / "data" / "peoplepulse.db"

    if not db_path.exists():

        initialize_database(
            df,
            db_path,
        )

    examples = {

        "Department attrition": """
        SELECT
            Department,
            COUNT(*) employees,
            SUM(
                CASE
                    WHEN Attrition = 'Yes' THEN 1
                    ELSE 0
                END
            ) exits,
            ROUND(
                1.0 * SUM(
                    CASE
                        WHEN Attrition = 'Yes' THEN 1
                        ELSE 0
                    END
                ) / COUNT(*),
                4
            ) attrition_rate
        FROM employees
        GROUP BY Department
        ORDER BY attrition_rate DESC;
        """,

        "Salary by role": """
        SELECT
            JobRole,
            ROUND(AVG(MonthlySalary), 2) avg_salary,
            COUNT(*) employees
        FROM employees
        GROUP BY JobRole
        ORDER BY avg_salary DESC;
        """,

        "Overtime comparison": """
        SELECT
            Overtime,
            COUNT(*) employees,
            ROUND(
                AVG(
                    CASE
                        WHEN Attrition = 'Yes' THEN 1.0
                        ELSE 0.0
                    END
                ),
                4
            ) attrition_rate
        FROM employees
        GROUP BY Overtime;
        """,
    }

    selected_example = st.selectbox(
        "Example Query",
        list(examples),
    )

    query = st.text_area(
        "SQL Query",
        examples[selected_example],
        height=200,
    )

    if st.button(
        "Run SQL Query",
        type="primary",
    ):

        try:

            output = run_sql_query(
                db_path,
                query,
            )

            st.subheader("Query Results")

            st.dataframe(
                output,
                width="stretch",
                hide_index=True,
            )

            csv_download(
                output,
                filename="sql_query_result.csv",
            )

        except Exception as exc:

            st.error(f"SQL error: {exc}")

    st.caption(
        "SQLite is the configured zero-setup database. "
        "MySQL is not connected in this release. "
        "Only read-only SELECT/WITH queries are allowed."
    )


# ==================================================
# 7. DATA QUALITY & GOVERNANCE
# ==================================================

elif page == "Data Quality & Governance":

    heading(
        "Data Quality & Governance",
        "Inspect completeness, duplicate identifiers, schema "
        "and responsible-use constraints.",
    )

    report = build_data_quality_report(df)

    a, b, c = st.columns(3)

    a.metric(
        "Rows",
        f'{report["rows"]:,}',
    )

    b.metric(
        "Columns",
        report["columns"],
    )

    c.metric(
        "Duplicate IDs",
        report["duplicate_ids"],
    )

    # Pandas compatibility fix:
    # Avoid reset_index(names="column")
    missing = (
        df.isna()
        .sum()
        .rename("missing")
        .reset_index()
    )

    missing.columns = [
        "column",
        "missing",
    ]

    missing["missing_pct"] = (
        missing["missing"] / len(df)
        if len(df) > 0
        else 0
    )

    st.subheader("Missing-Value Profile")

    st.dataframe(
        missing.sort_values(
            "missing",
            ascending=False,
        ),
        width="stretch",
        hide_index=True,
    )

    st.plotly_chart(
        px.bar(
            missing.sort_values(
                "missing",
                ascending=False,
            ).head(15),
            x="column",
            y="missing_pct",
            title="Top Missing-Value Rates",
        ),
        width="stretch",
    )

    if issues:

        for issue in issues:
            st.error(issue)

    else:

        st.success(
            "Core schema and domain checks passed."
        )

    schema = pd.DataFrame(
        {
            "column": df.columns,
            "dtype": [
                str(x)
                for x in df.dtypes
            ],
            "non_null": [
                int(df[c].notna().sum())
                for c in df.columns
            ],
        }
    )

    st.subheader("Schema Profile")

    st.dataframe(
        schema,
        width="stretch",
        hide_index=True,
    )

    st.markdown(
        "**Responsible use:** synthetic data; "
        "association is not causation; "
        "this demonstration must not be used "
        "for individual employment decisions."
    )

    csv_download(
        missing,
        filename="data_quality_missing_values.csv",
    )


# ==================================================
# 8. PROJECT NOTES
# ==================================================

elif page == "Project Notes":

    heading(
        "Project Notes & Architecture",
        "Technical documentation, project scope and reviewer guide.",
    )

    st.markdown("""
### Eight-Section Application Map

1. **Executive Overview** — KPIs, workforce distribution and descriptive observations.
2. **Workforce Explorer** — workforce composition, salary, tenure and employee-level filtering.
3. **Attrition Intelligence** — segment-level attrition rates and denominator counts.
4. **Retention & Cohorts** — hire-year cohorts and tenure-segment comparison.
5. **Predictive Analytics** — train/test evaluation, confusion matrix and permutation importance.
6. **SQL Analytics** — read-only SQL lab backed by SQLite.
7. **Data Quality & Governance** — missingness, schema, duplicate IDs and responsible-use notes.
8. **Project Notes** — architecture, limitations and deployment information.

### Architecture

`CSV → validation → analytics → SQLite query layer → Streamlit UI`

`CSV → preprocessing pipeline → classifier → holdout evaluation + permutation importance`

### Engineering Choices

- Analytics, data loading, database access and modeling are separated into `src/`.
- SQLite is created locally from the included CSV; no database server is required.
- Preprocessing is fitted inside the model pipeline after the stratified train/test split.
- EmployeeID and ExitYear are excluded from the predictor list.
- Evaluation includes accuracy, precision, recall, F1, ROC-AUC and confusion matrix.

### Known Limitations

- Dataset is synthetic demonstration data, not a real employer dataset.
- Predictive metrics are educational and may be weak; no production validation is claimed.
- MySQL integration, SHAP, authentication/RBAC, cloud database, CI/CD, production monitoring and survival analysis are not implemented.
- No individual employee risk scoring is provided by design.

### Run Locally

```bash
py -3.11 -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```
""")

    readme_path = ROOT / "README.md"

    if readme_path.exists():

        st.download_button(
            "Download Project README",
            readme_path.read_text(encoding="utf-8"),
            "README.md",
            "text/markdown",
        )

    else:

        st.info(
            "README.md is not present in the project folder."
        )
