import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd
def kpi_summary(d):
 n=len(d); exits=(d.Attrition=='Yes').sum() if n else 0
 return {'employees':n,'attrition_rate':exits/n if n else 0.,'average_age':d.Age.mean() if n else 0.,'average_salary':d.MonthlySalary.mean() if n else 0.,'average_tenure':d.YearsAtCompany.mean() if n else 0.}
def attrition_by(d,g):
 if d.empty: return pd.DataFrame(columns=[g,'employees','attrition_count','attrition_rate'])
 o=d.groupby(g,dropna=False).agg(employees=('EmployeeID','count'),attrition_count=('Attrition',lambda s:(s=='Yes').sum())).reset_index(); o['attrition_rate']=o.attrition_count/o.employees.replace(0,np.nan); return o
def retention_cohorts(d):
 if d.empty: return pd.DataFrame()
 o=d.groupby('HireYear').agg(employees=('EmployeeID','count'),exits=('Attrition',lambda s:(s=='Yes').sum())).reset_index(); o['retained']=o.employees-o.exits; o['retention_rate']=o.retained/o.employees.replace(0,np.nan); return o.sort_values('HireYear')
def workforce_segments(d,col,bins,labels):
 t=d.copy(); t['segment']=pd.cut(t[col],bins=bins,labels=labels,right=False,include_lowest=True)
 o=t.groupby('segment',observed=False).agg(employees=('EmployeeID','count'),attrition_count=('Attrition',lambda s:(s=='Yes').sum())).reset_index(); o['attrition_rate']=o.attrition_count/o.employees.replace(0,np.nan); return o
def run_sql_query(path,query):
 q=query.strip().lower()
 if not(q.startswith('select') or q.startswith('with')): raise ValueError('Only SELECT/WITH queries are allowed.')
 uri=Path(path).resolve().as_uri()+'?mode=ro'
 with sqlite3.connect(uri,uri=True) as c: return pd.read_sql_query(query,c)
