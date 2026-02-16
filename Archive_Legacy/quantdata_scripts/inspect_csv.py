
import pandas as pd
import sys

try:
    df = pd.read_csv('Thesis_Dataset_Master.csv')
    print("Columns:", df.columns)
    
    # Search for potential headers
    keywords = ["Item 1A", "Risk Factors", "ITEM 1A", "RISK FACTORS"]
    
    count = 0
    for index, row in df.iterrows():
        sentence = str(row['Sentence'])
        # Check if any keyword matches
        for kw in keywords:
            if kw.lower() in sentence.lower():
                print(f"Line {index+2}: {sentence}")
                count += 1
                break
        if count > 20: 
            break
            
except Exception as e:
    print(f"Error: {e}")
