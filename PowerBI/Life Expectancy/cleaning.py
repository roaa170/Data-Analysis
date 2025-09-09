import  pandas as pd
import numpy as np
import os
# print(os.listdir('.'))

df = pd.read_csv('Life Expectancy Data.csv')
# print(df.head())

df.columns = df.columns.str.strip().str.lower().str.replace(" ","_")
num_cols = df.select_dtypes(include=[np.number]).columns
cat_cols = df.select_dtypes(include=['object' , 'category']).columns
df[num_cols] = df[num_cols].fillna(df[num_cols].median())
df[cat_cols]=df[cat_cols].fillna(df[cat_cols].mode().iloc[0])

for col in num_cols:
   Q1 = df[col].quantile(0.25)
   Q3 =df[col].quantile(0.75)
   IQR = Q3 -Q1
   outliers = ((df[col] < (Q1- 1.5*IQR))| (df[col] > Q3 + 1.5 *IQR) )
   lower = Q1 - 1.5*IQR
   upper = Q3 +1.5*IQR
   df[col] = np.where(df[col] < lower , lower , df[col]) 
   df[col] = np.where(df[col] > upper , upper , df[col]) 
df['year'] = df['year'].astype(int)
if 'status' in df.columns:
    df['status'] = df['status'].astype('category')
df.to_csv('Life_Expectancy_Cleaned.csv', index=False)