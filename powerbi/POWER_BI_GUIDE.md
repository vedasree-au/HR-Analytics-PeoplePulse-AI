# Power BI build guide

A `.pbix` is a proprietary Power BI Desktop project file and cannot be reliably authored in this Python environment. This folder provides the exact measures, theme and build specification; create and save the report as `hr_analytics_dashboard.pbix` in Power BI Desktop after importing the cleaned CSV.

## Import and model
1. Open Power BI Desktop → Get Data → Text/CSV → `dataset/cleaned_data.csv`.
2. In Power Query, confirm numeric types for Age, MonthlySalary, YearsExperience, YearsAtCompany, JobSatisfaction, PerformanceRating, HireYear and ExitYear. Set EmployeeID to Whole Number; other descriptors to Text.
3. Apply changes. One employee row per EmployeeID; no relationship is required for this single-table model.
4. View → Themes → Browse for `hr_theme.json`.
5. Add measures from `measures.dax`. Format rate measures as Percentage (2 decimals).

## Page 1 — HR Overview
- KPI cards: Total Employees, Active Employees, Employees Left, Attrition Rate, Average Age, Average Monthly Salary.
- Clustered bar: headcount by Department.
- Line/column chart: hires by HireYear. Do not call this an attrition trend; exit dates are synthetic approximations and the data is not a true monthly event history.
- Donut: active vs left.
- Slicers: Department, Gender, JobRole, AgeGroup, Education.

## Page 2 — Attrition Analysis
- Bar: Attrition Rate by Department.
- Bar: Attrition Rate by JobRole.
- Column: Attrition Rate by AgeGroup.
- 100% stacked bar: Attrition by Gender.
- Bar: Attrition Rate by SalaryBand.
- Column: Attrition Rate by Overtime.
- Matrix: JobSatisfaction by Attrition status.
- Slicers: Department, AgeGroup, SalaryBand, Overtime, JobSatisfaction.

For rate charts, use `Attrition Rate` and ensure the category is on the axis. Include employee count in tooltip to show group size.

## Page 3 — Workforce
- Treemap: employee distribution by Department and JobRole.
- Histogram/column: employee count by ExperienceBand.
- Box plot custom visual (optional) or histogram: MonthlySalary distribution.
- Column: PerformanceRating distribution.
- Column: JobSatisfaction distribution.
- Donut: Education distribution.
- Slicers: Department, JobRole, Gender, Education.

## Interactivity and polish
- Add report-page tooltip with Total Employees, Employees Left and Attrition Rate.
- Add drill-through page `Role Detail` using JobRole as drill-through field; include role KPIs and salary/satisfaction visuals.
- Use consistent page titles, aligned visuals, concise labels, accessible contrast and consistent number formatting.
- Add a footer: “Synthetic portfolio dataset — not real employee records.”
- Save as `powerbi/hr_analytics_dashboard.pbix` and export page screenshots to `screenshots/`.
