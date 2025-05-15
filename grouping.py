import pandas as pd

# Load the Excel data
data = pd.read_excel(
    r"D:\CogniSaaS\AI_Project_Creation\Integrated Standardized Master Plan Excel_Panda.xlsx",
    sheet_name="1. Employer Branding"
)

# Clean column names (remove leading/trailing spaces)
data.columns = data.columns.str.strip()

# Debug: Print actual column names to verify
print("Columns:", data.columns.tolist())

# Define the custom sort order for Major Phase
custom_order = ['Intake', 'Design', 'Setup', 'Operation']

# Apply custom sort order
data['Intake, Design, Setup, Operations'] = pd.Categorical(data['Intake, Design, Setup, Operations'], categories=custom_order, ordered=True)
sorted_data = data.sort_values(by='Intake, Design, Setup, Operations')

# Save to new Excel file
sorted_data.to_excel("grouped.xlsx", index=False)

print("Excel file 'grouped.xlsx' created successfully.")