# analysis.py - Analyze your retail data

import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# ============================================
# DATABASE CONNECTION
# ============================================

DB_CONFIG = {
    'host': 'localhost',
    'database': 'retail_intelligence',
    'user': 'root',
    'password': 'Gems@04#'  # Your password
}

def get_connection():
    """Connect to MySQL database"""
    return mysql.connector.connect(**DB_CONFIG)

# ============================================
# ANALYSIS 1: SALES OVERVIEW
# ============================================

def get_sales_overview():
    """Get basic sales statistics"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Total revenue, orders, average
    cursor.execute("""
        SELECT 
            COUNT(*) as total_transactions,
            SUM(revenue) as total_revenue,
            AVG(revenue) as average_order_value,
            SUM(quantity_sold) as total_units,
            COUNT(DISTINCT product_id) as products_sold,
            COUNT(DISTINCT customer_city) as cities
        FROM sales
    """)
    
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return {
        'transactions': result[0],
        'revenue': result[1],
        'avg_order': result[2],
        'units': result[3],
        'products': result[4],
        'cities': result[5]
    }

# ============================================
# ANALYSIS 2: BEST SELLING PRODUCTS
# ============================================

def get_top_products(limit=10):
    """Get top selling products by revenue"""
    conn = get_connection()
    
    query = """
    SELECT 
        p.product_name,
        p.category,
        SUM(s.revenue) as total_revenue,
        SUM(s.quantity_sold) as total_units,
        COUNT(s.sale_id) as times_sold,
        ROUND(AVG(p.rating), 1) as rating
    FROM products p
    JOIN sales s ON p.product_id = s.product_id
    GROUP BY p.product_id, p.product_name, p.category, p.rating
    ORDER BY total_revenue DESC
    LIMIT %s
    """
    
    df = pd.read_sql(query, conn, params=(limit,))
    conn.close()
    return df

# ============================================
# ANALYSIS 3: DAILY TRENDS
# ============================================

def get_daily_trends():
    """Get daily revenue and sales trends"""
    conn = get_connection()
    
    query = """
    SELECT 
        metric_date,
        total_revenue,
        total_units_sold,
        avg_order_value,
        unique_customers
    FROM daily_metrics
    ORDER BY metric_date DESC
    LIMIT 30
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ============================================
# ANALYSIS 4: CATEGORY PERFORMANCE
# ============================================

def get_category_analysis():
    """Analyze performance by category"""
    conn = get_connection()
    
    query = """
    SELECT 
        p.category,
        COUNT(DISTINCT p.product_id) as product_count,
        SUM(s.revenue) as total_revenue,
        SUM(s.quantity_sold) as total_units,
        COUNT(s.sale_id) as transaction_count,
        ROUND(AVG(s.revenue), 2) as avg_transaction
    FROM products p
    JOIN sales s ON p.product_id = s.product_id
    GROUP BY p.category
    ORDER BY total_revenue DESC
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ============================================
# ANALYSIS 5: GEOGRAPHIC ANALYSIS
# ============================================

def get_city_analysis():
    """Analyze sales by city"""
    conn = get_connection()
    
    query = """
    SELECT 
        customer_city,
        COUNT(*) as orders,
        SUM(revenue) as total_revenue,
        SUM(quantity_sold) as total_units,
        AVG(revenue) as avg_order_value
    FROM sales
    GROUP BY customer_city
    ORDER BY total_revenue DESC
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ============================================
# ANALYSIS 6: WEEKDAY VS WEEKEND
# ============================================

def get_weekday_analysis():
    """Compare weekday vs weekend sales"""
    conn = get_connection()
    
    query = """
    SELECT 
        DAYOFWEEK(sale_date) as day_number,
        CASE 
            WHEN DAYOFWEEK(sale_date) IN (1, 7) THEN 'Weekend'
            ELSE 'Weekday'
        END as day_type,
        COUNT(*) as orders,
        SUM(revenue) as total_revenue,
        AVG(revenue) as avg_order
    FROM sales
    GROUP BY day_type, day_number
    ORDER BY day_number
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ============================================
# ANALYSIS 7: PAYMENT METHOD PREFERENCE
# ============================================

def get_payment_analysis():
    """Analyze payment method usage"""
    conn = get_connection()
    
    query = """
    SELECT 
        payment_method,
        COUNT(*) as usage_count,
        SUM(revenue) as total_revenue,
        AVG(revenue) as avg_transaction,
        SUM(quantity_sold) as total_units
    FROM sales
    GROUP BY payment_method
    ORDER BY total_revenue DESC
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ============================================
# VISUALIZATION FUNCTIONS
# ============================================

def create_visualizations():
    """Create all charts and save them"""
    
    # Set style for better looking charts
    plt.style.use('seaborn-v0_8-darkgrid')
    
    # 1. Top Products Chart
    print("\n📊 Creating top products chart...")
    top_products = get_top_products(5)
    
    plt.figure(figsize=(10, 6))
    plt.barh(top_products['product_name'].str[:30], top_products['total_revenue'])
    plt.xlabel('Total Revenue ($)')
    plt.ylabel('Product')
    plt.title('Top 5 Products by Revenue')
    plt.tight_layout()
    plt.savefig('top_products.png', dpi=100)
    plt.close()
    print("   ✅ Saved: top_products.png")
    
    # 2. Daily Revenue Trend
    print("\n📈 Creating daily revenue chart...")
    daily = get_daily_trends()
    daily = daily.sort_values('metric_date')
    
    plt.figure(figsize=(12, 5))
    plt.plot(daily['metric_date'], daily['total_revenue'], marker='o', linewidth=2)
    plt.xlabel('Date')
    plt.ylabel('Revenue ($)')
    plt.title('Daily Revenue Trend (Last 30 Days)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('daily_revenue.png', dpi=100)
    plt.close()
    print("   ✅ Saved: daily_revenue.png")
    
    # 3. Category Revenue Pie Chart
    print("\n🥧 Creating category pie chart...")
    categories = get_category_analysis()
    
    plt.figure(figsize=(8, 8))
    plt.pie(categories['total_revenue'][:5], labels=categories['category'][:5], 
            autopct='%1.1f%%', startangle=90)
    plt.title('Revenue by Category')
    plt.tight_layout()
    plt.savefig('category_revenue.png', dpi=100)
    plt.close()
    print("   ✅ Saved: category_revenue.png")
    
    # 4. City Revenue Bar Chart
    print("\n🏙️ Creating city analysis chart...")
    cities = get_city_analysis().head(8)
    
    plt.figure(figsize=(10, 6))
    plt.bar(cities['customer_city'], cities['total_revenue'])
    plt.xlabel('City')
    plt.ylabel('Revenue ($)')
    plt.title('Top Cities by Revenue')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('city_revenue.png', dpi=100)
    plt.close()
    print("   ✅ Saved: city_revenue.png")
    
    # 5. Payment Methods
    print("\n💳 Creating payment methods chart...")
    payments = get_payment_analysis()
    
    plt.figure(figsize=(8, 6))
    plt.pie(payments['usage_count'], labels=payments['payment_method'], 
            autopct='%1.1f%%')
    plt.title('Payment Method Distribution')
    plt.tight_layout()
    plt.savefig('payment_methods.png', dpi=100)
    plt.close()
    print("   ✅ Saved: payment_methods.png")

# ============================================
# PRINT REPORTS
# ============================================

def print_analysis_report():
    """Print a complete analysis report"""
    
    print("\n" + "=" * 70)
    print("📊 RETAIL INTELLIGENCE ANALYSIS REPORT")
    print("=" * 70)
    print(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 1. Overview
    print("\n📈 1. SALES OVERVIEW")
    print("-" * 50)
    overview = get_sales_overview()
    print(f"   Total Transactions: {overview['transactions']:,}")
    print(f"   Total Revenue: ${overview['revenue']:,.2f}")
    print(f"   Average Order Value: ${overview['avg_order']:.2f}")
    print(f"   Total Units Sold: {overview['units']:,}")
    print(f"   Products Sold: {overview['products']}")
    print(f"   Cities Served: {overview['cities']}")
    
    # 2. Top Products
    print("\n🏆 2. TOP 5 PRODUCTS")
    print("-" * 50)
    top = get_top_products(5)
    for i, row in top.iterrows():
        print(f"   {i+1}. {row['product_name'][:40]:40} | ${row['total_revenue']:,.2f}")
    
    # 3. Category Analysis
    print("\n📂 3. CATEGORY PERFORMANCE")
    print("-" * 50)
    categories = get_category_analysis()
    for i, row in categories.iterrows():
        print(f"   {row['category']:20} | ${row['total_revenue']:,.2f} | {row['total_units']} units")
    
    # 4. City Analysis
    print("\n🌆 4. TOP 5 CITIES")
    print("-" * 50)
    cities = get_city_analysis().head(5)
    for i, row in cities.iterrows():
        print(f"   {i+1}. {row['customer_city']:15} | ${row['total_revenue']:,.2f} | {row['orders']} orders")
    
    # 5. Payment Methods
    print("\n💳 5. PAYMENT METHODS")
    print("-" * 50)
    payments = get_payment_analysis()
    for i, row in payments.iterrows():
        print(f"   {row['payment_method']:15} | {row['usage_count']} transactions | ${row['total_revenue']:,.2f}")
    
    # 6. Weekday vs Weekend
    print("\n📅 6. WEEKDAY VS WEEKEND")
    print("-" * 50)
    weekday_data = get_weekday_analysis()
    weekend_total = weekday_data[weekday_data['day_type'] == 'Weekend']['total_revenue'].sum()
    weekday_total = weekday_data[weekday_data['day_type'] == 'Weekday']['total_revenue'].sum()
    print(f"   Weekday Revenue: ${weekday_total:,.2f}")
    print(f"   Weekend Revenue: ${weekend_total:,.2f}")
    
    if weekend_total > weekday_total:
        print(f"   📈 Weekend sales are {((weekend_total/weekday_total)-1)*100:.1f}% higher!")
    else:
        print(f"   📈 Weekday sales are {((weekday_total/weekend_total)-1)*100:.1f}% higher!")
    
    print("\n" + "=" * 70)
    print("✅ REPORT COMPLETE")
    print("=" * 70)

# ============================================
# MAIN FUNCTION
# ============================================

def main():
    """Run all analysis"""
    print("\n🚀 Starting Retail Data Analysis...")
    
    # Print the report
    print_analysis_report()
    
    # Create visualizations
    print("\n📊 Creating visualizations...")
    create_visualizations()
    
    print("\n✅ Analysis Complete!")
    print("\n📁 Files created in your project folder:")
    print("   • top_products.png")
    print("   • daily_revenue.png")
    print("   • category_revenue.png")
    print("   • city_revenue.png")
    print("   • payment_methods.png")
    print("\n💡 Next: Open these images to see your data visualized!")

# ============================================
# RUN
# ============================================

if __name__ == "__main__":
    # First install required packages if needed
    try:
        import pandas
        import matplotlib
    except ImportError:
        print("📦 Installing required packages...")
        import subprocess
        subprocess.run(['pip', 'install', 'pandas', 'matplotlib'])
        print("✅ Packages installed!")
    
    main()