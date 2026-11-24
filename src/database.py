import sqlite3
from pathlib import Path
def initialize_database(df,path):
 p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect(p) as c:
  df.to_sql('employees',c,if_exists='replace',index=False); c.execute('CREATE INDEX IF NOT EXISTS idx_department ON employees(Department)'); c.execute('CREATE INDEX IF NOT EXISTS idx_attrition ON employees(Attrition)'); c.commit()
 return len(df)
