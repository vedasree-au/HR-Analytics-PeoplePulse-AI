import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier,HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score,roc_auc_score,confusion_matrix,classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder,StandardScaler
def train_attrition_model(df,features,kind='Random Forest',test_size=.25):
 features=[f for f in features if f not in {'EmployeeID','ExitYear','Attrition'}]
 if not features: raise ValueError('Choose at least one valid predictor.')
 data=df[features+['Attrition']].dropna(subset=['Attrition']); X=data[features]; y=(data.Attrition=='Yes').astype(int)
 if y.nunique()!=2: raise ValueError('Target must contain both Yes and No classes.')
 cats=X.select_dtypes(include=['object','string','category']).columns.tolist(); nums=[c for c in features if c not in cats]; trans=[]
 if nums: trans.append(('num',Pipeline([('impute',SimpleImputer(strategy='median')),('scale',StandardScaler())]),nums))
 if cats: trans.append(('cat',Pipeline([('impute',SimpleImputer(strategy='most_frequent')),('onehot',OneHotEncoder(handle_unknown='ignore'))]),cats))
 prep=ColumnTransformer(trans)
 if kind=='Logistic Regression': model=LogisticRegression(max_iter=2000,class_weight='balanced',random_state=42)
 elif kind=='HistGradientBoosting':
  trans=[]
  if nums: trans.append(('num',Pipeline([('impute',SimpleImputer(strategy='median')),('scale',StandardScaler())]),nums))
  if cats: trans.append(('cat',Pipeline([('impute',SimpleImputer(strategy='most_frequent')),('onehot',OneHotEncoder(handle_unknown='ignore',sparse_output=False))]),cats))
  prep=ColumnTransformer(trans); model=HistGradientBoostingClassifier(max_iter=120,learning_rate=.08,random_state=42)
 else: model=RandomForestClassifier(n_estimators=300,min_samples_leaf=3,class_weight='balanced_subsample',random_state=42,n_jobs=-1)
 Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=test_size,random_state=42,stratify=y); pipe=Pipeline([('prep',prep),('model',model)]); pipe.fit(Xtr,ytr); pred=pipe.predict(Xte); prob=pipe.predict_proba(Xte)[:,1]
 perm=permutation_importance(pipe,Xte,yte,n_repeats=5,random_state=42,scoring='f1',n_jobs=-1)
 imp=pd.DataFrame({'feature':features,'importance':perm.importances_mean}).sort_values('importance',ascending=False)
 metrics={'accuracy':float(accuracy_score(yte,pred)),'precision':float(precision_score(yte,pred,zero_division=0)),'recall':float(recall_score(yte,pred,zero_division=0)),'f1':float(f1_score(yte,pred,zero_division=0)),'roc_auc':float(roc_auc_score(yte,prob))}
 return {'pipeline':pipe,'features':features,'metrics':metrics,'confusion_matrix':confusion_matrix(yte,pred,labels=[0,1]).tolist(),'classification_report':classification_report(yte,pred,target_names=['No attrition','Attrition'],zero_division=0),'importance':imp,'test_rows':len(yte),'model_kind':kind}
def model_report(a): return {k:a[k] for k in ['metrics','confusion_matrix','classification_report','importance','test_rows','model_kind']}
