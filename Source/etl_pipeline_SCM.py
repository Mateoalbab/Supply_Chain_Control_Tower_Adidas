import pandas as pd
import os

# ==========================================
# 0. SETUP PATHS
# ==========================================
script_dir = os.path.dirname(os.path.abspath(__file__))
raw_dir = os.path.join(script_dir, '..', '01_Data_Raw')
processed_dir = os.path.join(script_dir, '..', '02_Data_Processed')

# Ensure processed folder exists
if not os.path.exists(processed_dir):
    os.makedirs(processed_dir)

print("🚀 STARTING ETL PIPELINE...")

# ==========================================
# 1. LOAD DATA (EXTRACT)
# ==========================================
print("   ...Loading Raw Files")
try:
    df_sales = pd.read_csv(os.path.join(raw_dir, 'Adidas_Global_Sales.csv'))
    df_inventory = pd.read_csv(os.path.join(raw_dir, 'Adidas_Inventory_Snapshot.csv'))
except FileNotFoundError:
    print("❌ ERROR: Could not find raw files. Check your folder structure!")
    exit()

# ==========================================
# 2. DATA TRANSFORMATION (THE "FIX")
# ==========================================
print("   ...Normalizing Currencies to USD")

# Define Average Exchange Rates (2024 Estimates for Simulation)
# Logic: We divide or multiply to get back to USD
exchange_rates = {
    'USD': 1.0,
    'EUR': 1.09,    # 1 EUR = 1.09 USD
    'COP': 0.00026, # 1 COP = 0.00026 USD (approx 1/3900)
    'JPY': 0.0067   # 1 JPY = 0.0067 USD
}

# Apply Logic: Create a new column 'Revenue_USD'
# We use a Lambda function to apply the rate row-by-row
def convert_to_usd(row):
    rate = exchange_rates.get(row['Currency'], 1.0)
    # If the currency is EUR/USD, the raw data was Unit * Price * Rate.
    # Our generator math was: Revenue_Local = (USD_Price * Conversion).
    # So to get back to USD, we can actually just reverse-engineer or re-calculate.
    # SIMPLER APPROACH: We map the rate and multiply.
    
    # Check for COP specifically to handle the billions
    if row['Currency'] == 'COP':
        return row['Revenue_Local'] / 3900 # Divide by rate to get USD
    elif row['Currency'] == 'EUR':
        return row['Revenue_Local'] / 0.92 # Reverse the generator math
    elif row['Currency'] == 'JPY':
        return row['Revenue_Local'] / 150
    else:
        return row['Revenue_Local']

df_sales['Revenue_USD'] = df_sales.apply(convert_to_usd, axis=1)

# Round to 2 decimals for clean reporting
df_sales['Revenue_USD'] = df_sales['Revenue_USD'].round(2)

print("   ...Validating Data Integrity")
# Check if we created any NaN (errors)
if df_sales['Revenue_USD'].isnull().sum() > 0:
    print("⚠️ WARNING: Some rows could not be converted!")
else:
    print("✅ All currencies converted successfully.")

# ==========================================
# 3. EXPORT (LOAD)
# ==========================================
print("   ...Saving Processed Files")

# Save Sales
sales_clean_path = os.path.join(processed_dir, 'Adidas_Sales_Cleaned.csv')
df_sales.to_csv(sales_clean_path, index=False)

# Save Inventory (Just passing it through to keep processed folder complete)
inv_clean_path = os.path.join(processed_dir, 'Adidas_Inventory_Cleaned.csv')
df_inventory.to_csv(inv_clean_path, index=False)

print("="*40)
print("✅ ETL COMPLETE")
print(f"📄 Processed Sales saved to: {sales_clean_path}")
print(f"💰 Total Revenue (USD): ${df_sales['Revenue_USD'].sum():,.2f}")
print("="*40)