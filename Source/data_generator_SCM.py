import pandas as pd
import numpy as np
import os
import random
from datetime import datetime, timedelta

# ==========================================
# 0. FILE SYSTEM SETUP
# ==========================================
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, '..', '01_Data_Raw')

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

print(f"📍 Target Folder: {output_dir}")

# ==========================================
# 1. CONFIGURATION
# ==========================================
np.random.seed(42)

markets = ['NAM', 'EMEA', 'LATAM', 'APAC']
product_lines = ['Messi Spark Gen10 Pro', 'Messi Spark Gen10 Academy', 'Messi Spark Gen10 Club']
sizes = ['US 6', 'US 7', 'US 8', 'US 9', 'US 10', 'US 11', 'US 12', 'US 13'] 
colors = ['Solar Red', 'Core Black', 'Lucid Blue'] 

# ==========================================
# 2. GENERATE INVENTORY DATA (SKU MASTER)
# ==========================================
print("⏳ Generating Inventory & SKU Master...")
inventory_data = []

for market in markets:
    for product in product_lines:
        for size in sizes:
            for color in colors:
                
                # --- THE FIX IS HERE ---
                # Old Logic: product[:5] -> "MESSI" (Duplicate!)
                # New Logic: Grab the LAST word (Pro/Academy/Club)
                tier = product.split(' ')[-1].upper()
                
                # SKU ID: Market-Tier-Color-Size
                # Example: NAM-PRO-RED-US9
                sku_id = f"{market}-{tier}-{color.split(' ')[1].upper()}-{size.replace(' ', '')}"
                # -----------------------

                # Scenario Logic
                if market == 'NAM':
                    stock_level = np.random.randint(2000, 8000)
                elif market == 'LATAM':
                    stock_level = np.random.randint(50, 400)
                elif market == 'EMEA':
                    stock_level = np.random.randint(1000, 3000)
                else:
                    stock_level = np.random.randint(500, 2000)
                
                blocked_pct = 0.35 if market in ['LATAM', 'APAC'] else 0.05
                blocked_stock = int(stock_level * blocked_pct)
                available_stock = stock_level - blocked_stock

                inventory_data.append([
                    sku_id, market, product, color, size, 
                    stock_level, available_stock, blocked_stock
                ])

df_inventory = pd.DataFrame(inventory_data, columns=[
    'SKU_ID', 'Market', 'Product', 'Color', 'Size', 
    'Total_Stock', 'Available_Stock', 'Blocked_Stock'
])

# ==========================================
# 3. GENERATE SALES DATA
# ==========================================
print("⏳ Generating Sales Transactions (Wait ~30s)...")

sales_data = []
start_date = datetime(2024, 1, 1)
days_to_simulate = 365 

for i in range(days_to_simulate):
    current_date = start_date + timedelta(days=i)
    
    if i % 30 == 0: print(f"   ...Processing Month {int(i/30)+1}")

    for index, row in df_inventory.iterrows():
        # Demand Logic
        is_weekend = current_date.weekday() >= 5
        weekend_multiplier = 1.5 if is_weekend else 1.0
        base_demand = np.random.randint(5, 30) 
        
        if row['Market'] == 'LATAM': mkt_mult = 4.0 
        elif row['Market'] == 'NAM': mkt_mult = 0.6 
        else: mkt_mult = 1.0
        
        final_demand = int(base_demand * mkt_mult * weekend_multiplier)
        units_sold = min(final_demand, row['Available_Stock'])
        
        if units_sold > 0:
            if 'Pro' in row['Product']: unit_price = 250
            elif 'Academy' in row['Product']: unit_price = 140
            else: unit_price = 80
            
            if row['Market'] == 'NAM':
                revenue = units_sold * unit_price
                curr = 'USD'
            elif row['Market'] == 'EMEA':
                revenue = units_sold * unit_price * 0.92
                curr = 'EUR'
            elif row['Market'] == 'LATAM':
                revenue = units_sold * unit_price * 3900 
                curr = 'COP' 
            elif row['Market'] == 'APAC':
                revenue = units_sold * unit_price * 150
                curr = 'JPY'

            sales_data.append([
                current_date, row['SKU_ID'], row['Market'], 
                row['Product'], row['Color'], row['Size'], 
                units_sold, round(revenue, 2), curr
            ])

df_sales = pd.DataFrame(sales_data, columns=[
    'Date', 'SKU_ID', 'Market', 'Product', 'Color', 'Size', 
    'Units_Sold', 'Revenue_Local', 'Currency'
])

# ==========================================
# 4. EXPORT
# ==========================================
print(f"💾 Saving Data to {output_dir}...")
inventory_path = os.path.join(output_dir, 'Adidas_Inventory_Snapshot.csv')
sales_path = os.path.join(output_dir, 'Adidas_Global_Sales.csv')

df_inventory.to_csv(inventory_path, index=False)
df_sales.to_csv(sales_path, index=False)

print("="*40)
print(f"✅ DATA RE-GENERATED (UNIQUE SKUs FIXED)!")
print(f"📊 Inventory SKUs: {len(df_inventory):,}")
print(f"📈 Sales Transactions: {len(df_sales):,}")
print("="*40)