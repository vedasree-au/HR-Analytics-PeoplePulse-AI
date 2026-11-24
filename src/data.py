import pandas as pd
REQUIRED={'EmployeeID','Age','Gender','Department','JobRole','MonthlySalary','YearsExperience','YearsAtCompany','JobSatisfaction','Overtime','PerformanceRating','Attrition','HireYear'}
def load_employee_data(path):
 d=pd.read_csv(path)
 for c in ['Gender','Department','JobRole','Education','Overtime','Attrition','AgeGroup','SalaryBand','ExperienceBand']:
  if c in d: d[c]=d[c].astype('string').str.strip()
 for c in ['EmployeeID','Age','MonthlySalary','YearsExperience','YearsAtCompany','JobSatisfaction','PerformanceRating','HireYear','ExitYear']:
  if c in d: d[c]=pd.to_numeric(d[c],errors='coerce')
 return d
def validate_employee_data(d):
 issues=[]; missing=REQUIRED-set(d.columns)
 if missing: issues.append('Missing required columns: '+', '.join(sorted(missing)))
 if 'EmployeeID' in d and d.EmployeeID.duplicated().any(): issues.append('EmployeeID contains duplicate values.')
 if 'Attrition' in d and not set(d.Attrition.dropna().unique()).issubset({'Yes','No'}): issues.append('Attrition contains values other than Yes/No.')
 if 'MonthlySalary' in d and (d.MonthlySalary.dropna()<0).any(): issues.append('MonthlySalary contains negative values.')
 if 'Age' in d and not d.Age.dropna().between(16,100).all(): issues.append('Age contains values outside 16–100.')
 return issues
def build_data_quality_report(d): return {'rows':len(d),'columns':len(d.columns),'duplicate_ids':int(d.EmployeeID.duplicated().sum()) if 'EmployeeID' in d else 0,'missing_cells':int(d.isna().sum().sum())}
