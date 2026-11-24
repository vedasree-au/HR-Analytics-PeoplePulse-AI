from pathlib import Path
from src.data import load_employee_data,validate_employee_data
from src.analytics import kpi_summary,attrition_by,retention_cohorts,run_sql_query
from src.database import initialize_database
DATA=Path(__file__).parents[1]/'data'/'cleaned_data.csv'
def test_schema():
 d=load_employee_data(DATA); assert len(d)==1800; assert validate_employee_data(d)==[]
def test_analytics():
 d=load_employee_data(DATA); assert kpi_summary(d)['employees']==1800; assert not attrition_by(d,'Department').empty; assert not retention_cohorts(d).empty
def test_sqlite(tmp_path):
 d=load_employee_data(DATA); db=tmp_path/'x.db'; initialize_database(d,db); assert int(run_sql_query(db,'SELECT COUNT(*) n FROM employees').iloc[0,0])==len(d)
