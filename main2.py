import pandas as pd
import json
import numpy as np

# Load the Excel file
df = pd.read_excel(r"D:\CogniSaaS\AI_Project_Creation\grouped.xlsx")

# Clean column names
df.columns = df.columns.str.strip()

# Convert datetime columns to strings
df = df.applymap(lambda x: x.strftime("%Y-%m-%d") if isinstance(x, pd.Timestamp) else x)

# Group and reformat JSON
grouped_json = {}
for phase, group in df.groupby('Intake, Design, Setup, Operations'):
    records = []
    for _, row in group.iterrows():
        row_dict = row.drop('Intake, Design, Setup, Operations').to_dict()
        clean_data = {}
        custom_fields = {}

        for key, value in row_dict.items():
            if pd.isna(value):
                custom_fields[key] = None
            else:
                clean_data[key] = value

        if custom_fields:
            clean_data["custom_fields"] = custom_fields

        records.append(clean_data)

    grouped_json[phase] = records

# Save to JSON file
with open("grouped_by_phase_with_custom_fields.json", "w", encoding='utf-8') as f:
    json.dump(grouped_json, f, indent=4)