
import pandas as pd
try:
    df = pd.read_csv('Thesis_Dataset_Master_RiskFactorsOnly.csv')
    print(df['Company'].value_counts())
    print(df['Year'].value_counts())
except:
    pass
