# ============================================================
# PROJECT 2: Sales Performance Dashboard
# Author: Bittu Kumar | Data Analyst
# Tools: Python | Pandas | SQL (SQLite) | Matplotlib | Seaborn
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import sqlite3
from datetime import datetime, timedelta
import random
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("  SALES PERFORMANCE DASHBOARD ANALYSIS")
print("=" * 60)

# ─────────────────────────────────────────
# STEP 1: GENERATE SAMPLE SALES DATA
# (Replace this with your own CSV/database)
# ─────────────────────────────────────────
random.seed(42)
np.random.seed(42)

regions = ['North', 'South', 'East', 'West']
products = ['Laptop', 'Smartphone', 'Tablet', 'Monitor', 'Keyboard']
reps = ['Alice', 'Bob', 'Charlie', 'Diana', 'Evan',
        'Fiona', 'George', 'Hannah']

dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
n = 10000

data = {
    'Date': np.random.choice(dates, n),
    'Region': np.random.choice(regions, n, p=[0.35, 0.20, 0.25, 0.20]),
    'Product': np.random.choice(products, n),
    'Sales_Rep': np.random.choice(reps, n),
    'Units_Sold': np.random.randint(1, 20, n),
    'Unit_Price': np.random.choice([800, 500, 350, 250, 75], n),
}

df = pd.DataFrame(data)
df['Revenue'] = df['Units_Sold'] * df['Unit_Price']
df['Month'] = pd.to_datetime(df['Date']).dt.to_period('M')
df['Month_Num'] = pd.to_datetime(df['Date']).dt.month
df['Month_Name'] = pd.to_datetime(df['Date']).dt.strftime('%b')

print(f"✅ Data Generated: {df.shape[0]:,} records")
print(df.head())


# ─────────────────────────────────────────
# STEP 2: SQL ANALYSIS (using SQLite)
# ─────────────────────────────────────────
conn = sqlite3.connect(':memory:')
df.to_sql('sales', conn, index=False, if_exists='replace')

print("\n" + "─" * 50)
print("  SQL ANALYSIS RESULTS")
print("─" * 50)

# Query 1: Revenue by Region
q1 = pd.read_sql("""
    SELECT Region,
           SUM(Revenue) AS Total_Revenue,
           COUNT(*) AS Num_Transactions,
           ROUND(AVG(Revenue), 2) AS Avg_Revenue
    FROM sales
    GROUP BY Region
    ORDER BY Total_Revenue DESC
""", conn)
print("\n📊 Revenue by Region:\n", q1.to_string(index=False))

# Query 2: Top Products
q2 = pd.read_sql("""
    SELECT Product,
           SUM(Units_Sold) AS Total_Units,
           SUM(Revenue) AS Total_Revenue
    FROM sales
    GROUP BY Product
    ORDER BY Total_Revenue DESC
""", conn)
print("\n📊 Top Products:\n", q2.to_string(index=False))

# Query 3: Monthly Revenue Trend
q3 = pd.read_sql("""
    SELECT Month_Num, Month_Name,
           SUM(Revenue) AS Monthly_Revenue
    FROM sales
    GROUP BY Month_Num, Month_Name
    ORDER BY Month_Num
""", conn)
print("\n📊 Monthly Revenue Trend:\n", q3.to_string(index=False))

# Query 4: Top 5 Sales Reps
q4 = pd.read_sql("""
    SELECT Sales_Rep,
           SUM(Revenue) AS Total_Revenue,
           SUM(Units_Sold) AS Total_Units
    FROM sales
    GROUP BY Sales_Rep
    ORDER BY Total_Revenue DESC
    LIMIT 5
""", conn)
print("\n📊 Top 5 Sales Reps:\n", q4.to_string(index=False))

conn.close()


# ─────────────────────────────────────────
# STEP 3: KPI CALCULATIONS
# ─────────────────────────────────────────
total_revenue = df['Revenue'].sum()
total_units = df['Units_Sold'].sum()
avg_order = df['Revenue'].mean()
top_region = df.groupby('Region')['Revenue'].sum().idxmax()
bot_region = df.groupby('Region')['Revenue'].sum().idxmin()
revenue_gap = (
    df.groupby('Region')['Revenue'].sum().max() -
    df.groupby('Region')['Revenue'].sum().min()
) / df.groupby('Region')['Revenue'].sum().max() * 100

print("\n" + "=" * 50)
print("  KEY PERFORMANCE INDICATORS (KPIs)")
print("=" * 50)
print(f"  Total Revenue    : ₹{total_revenue:>12,.0f}")
print(f"  Total Units Sold : {total_units:>12,}")
print(f"  Avg Order Value  : ₹{avg_order:>12,.2f}")
print(f"  Top Region       : {top_region}")
print(f"  Lowest Region    : {bot_region}")
print(f"  Revenue Gap (N-S): {revenue_gap:.1f}%")


# ─────────────────────────────────────────
# STEP 4: DASHBOARD VISUALIZATION
# ─────────────────────────────────────────
fig = plt.figure(figsize=(18, 12))
fig.suptitle('Sales Performance Dashboard - 2024', fontsize=18,
             fontweight='bold', color='#2c3e50', y=0.98)

colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']

# ── Chart 1: Monthly Revenue Trend ──────
ax1 = fig.add_subplot(3, 3, (1, 2))
ax1.plot(q3['Month_Name'], q3['Monthly_Revenue'] / 1e6,
         marker='o', color='#3498db', linewidth=2.5, markersize=7)
ax1.fill_between(range(len(q3)), q3['Monthly_Revenue'] / 1e6,
                 alpha=0.15, color='#3498db')
ax1.set_xticks(range(len(q3)))
ax1.set_xticklabels(q3['Month_Name'], fontsize=9)
ax1.set_title('Monthly Revenue Trend (₹ Millions)', fontweight='bold')
ax1.set_ylabel('Revenue (₹ M)')
ax1.grid(axis='y', alpha=0.3)
ax1.yaxis.set_major_formatter(mticker.FormatStrFormatter('₹%.1fM'))

# ── Chart 2: Revenue by Region ──────────
ax2 = fig.add_subplot(3, 3, 3)
region_rev = df.groupby('Region')['Revenue'].sum().sort_values(ascending=True)
bars = ax2.barh(region_rev.index, region_rev.values / 1e6,
                color=colors[:4], edgecolor='white')
ax2.set_title('Revenue by Region (₹ M)', fontweight='bold')
ax2.set_xlabel('Revenue (₹ M)')
for bar, val in zip(bars, region_rev.values / 1e6):
    ax2.text(val + 0.1, bar.get_y() + bar.get_height() / 2,
             f'₹{val:.1f}M', va='center', fontsize=9)

# ── Chart 3: Product Performance ────────
ax3 = fig.add_subplot(3, 3, 4)
prod_rev = df.groupby('Product')['Revenue'].sum().sort_values(ascending=False)
ax3.bar(prod_rev.index, prod_rev.values / 1e6, color=colors, edgecolor='white')
ax3.set_title('Revenue by Product (₹ M)', fontweight='bold')
ax3.set_ylabel('Revenue (₹ M)')
plt.setp(ax3.get_xticklabels(), rotation=20, ha='right', fontsize=9)

# ── Chart 4: Sales Rep Performance ──────
ax4 = fig.add_subplot(3, 3, 5)
rep_rev = df.groupby('Sales_Rep')['Revenue'].sum().sort_values(ascending=False)
ax4.bar(rep_rev.index, rep_rev.values / 1e6, color='#9b59b6', edgecolor='white')
ax4.set_title('Sales Rep Performance (₹ M)', fontweight='bold')
ax4.set_ylabel('Revenue (₹ M)')
plt.setp(ax4.get_xticklabels(), rotation=30, ha='right', fontsize=9)

# ── Chart 5: Units Sold by Product ──────
ax5 = fig.add_subplot(3, 3, 6)
prod_units = df.groupby('Product')['Units_Sold'].sum()
ax5.pie(prod_units, labels=prod_units.index, autopct='%1.1f%%',
        colors=colors, startangle=90)
ax5.set_title('Units Sold by Product', fontweight='bold')

# ── Chart 6: KPI Summary Box ────────────
ax6 = fig.add_subplot(3, 3, (7, 9))
ax6.axis('off')
kpi_text = (
    f"📌  KEY METRICS SUMMARY\n\n"
    f"  💰 Total Revenue    :  ₹{total_revenue/1e6:.2f} Million\n"
    f"  📦 Total Units Sold :  {total_units:,}\n"
    f"  🧾 Avg Order Value  :  ₹{avg_order:,.0f}\n"
    f"  🏆 Top Region       :  {top_region}\n"
    f"  📉 Lowest Region    :  {bot_region}\n"
    f"  📊 Revenue Gap      :  {revenue_gap:.1f}% between top & bottom regions\n"
)
ax6.text(0.05, 0.5, kpi_text, transform=ax6.transAxes,
         fontsize=13, va='center', fontfamily='monospace',
         bbox=dict(boxstyle='round,pad=1', facecolor='#eaf4fb', alpha=0.8))

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('sales_dashboard.png', dpi=150, bbox_inches='tight')
plt.show()
print("\n✅ Dashboard saved as 'sales_dashboard.png'")
print("✅ Sales Performance Analysis Complete!")
