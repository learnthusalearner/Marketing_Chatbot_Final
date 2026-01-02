import pandas as pd

# Path to your Excel file
excel_file = r"C:\Users\KIIT\Desktop\sales rag-final\data_changement\Sponsored_Products_Search_term_report (1).xlsx"

# Path for the new CSV file
csv_file = r"C:\Users\KIIT\Desktop\sales rag-final\data_changement\Sponsored_Products_Search_term_report_clean.csv"

# Read the Excel file
df = pd.read_excel(excel_file)

# Convert 'Date' column to YYYY-MM-DD format (remove time part)
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')

# Save as CSV
df.to_csv(csv_file, index=False)

print(f"Excel file has been converted to CSV with Date fixed and saved at {csv_file}")
