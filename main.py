# main.py

from etl.extract import fetch_html_with_productlist, scrape_multiple_pages
from etl.transform import filter_products
from etl.load import init_db, save_products, fetch_saved_products
from etl.email_alert import send_email
import os
from config import *
import json 
import sqlite3
from dotenv import load_dotenv
load_dotenv()

ZYTE_API_KEY = os.getenv("ZYTE_API_KEY")





# Email settings (replace with your credentials or config file)
SMTP_CONFIG = {
    "sender_email": EMAIL_USER,
    "recipient_email": TO_EMAIL,
    "smtp_server": EMAIL_HOST,
    "smtp_port": EMAIL_PORT,
    "smtp_user": EMAIL_USER,
    "smtp_password": EMAIL_PASS
}

with open("site_config.json", "r", encoding="utf-8") as f:
    site_config = json.load(f)

def run_pipeline():
    print("🚀 Starting E-Commerce Discount Alert Pipeline...")
    
    all_filtered = []
    init_db()
    
    # use with cautions - this keeps everything the latest
    conn = sqlite3.connect("db/local.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products")
    conn.commit()
    conn.close()
    print("🧹 Old data cleared from 'products' table.")
    
    # # Ensure source_site column exists
    # conn = sqlite3.connect("db/local.db")
    # cursor = conn.cursor()
    # try:
    #     cursor.execute("ALTER TABLE products ADD COLUMN source_site TEXT")
    #     print("🛠️ Column 'source_site' added to 'products' table.")
    # except sqlite3.OperationalError as e:
    #     if "duplicate column name" in str(e):
    #         print("ℹ️ Column 'source_site' already exists.")
    #     else:
    #         raise
    # conn.commit()
    # conn.close()

    
    
    
    for site in site_config:
        name = site.get("name")
        url = site.get("url")
        pagination_pattern = site.get("pagination_pattern", "")
        brand = site.get("brand", "").lower()
        min_discount = site.get("min_discount", 30)
        currency = site.get("currency", "EUR")

        # 1. Extract (scrape all pages for this site)
        scraped_products = scrape_multiple_pages(site, ZYTE_API_KEY, start_page=1, end_page=10)
        print(f"📦 Scraped {len(scraped_products)} products from {name} ({url})")

        # 2. Transform
        filtered = filter_products(scraped_products, brand=brand, min_discount=min_discount, currency=currency)
        print(f"🔍 Found {len(filtered)} products with significant discounts.")

        # 3. Load
        print(f"🧾 DEBUG: About to save {len(filtered)} filtered products")
        for i, p in enumerate(filtered[:3]):
            print(f"{i+1}. {p['name']} – {p['discounted_price']} {p['currency']} ({p['discount_percent']}%)")

        save_products(filtered, source_site=name)
        all_filtered.extend(filtered)


    # # 4. Email Alerts (optional)
    
    # print("\n🧪 DB VERIFICATION")
    # conn = sqlite3.connect("db/local.db")
    # cursor = conn.cursor()

    # cursor.execute("SELECT COUNT(*) FROM products")
    # total_rows = cursor.fetchone()[0]
    # print(f"📦 Total rows in DB: {total_rows}")

    # cursor.execute("SELECT name, brand, discounted_price, discount_percent, alert_sent FROM products LIMIT 5")
    # rows = cursor.fetchall()
    # for i, row in enumerate(rows):
    #     print(f"{i+1}. Name: {row[0]} | Brand: {row[1]} | Price: {row[2]} | Discount: {row[3]}% | Alert Sent: {row[4]}")

    # conn.close()


    top_alerts = fetch_saved_products()
    
    # Sort by discount percent, descending
    top_alerts_sorted = sorted(
    top_alerts,
    key=lambda x: float(x.get("discount_percent", 0)),
    reverse=True)[:30]
    
    print("\n📧 DEBUG: Products passed to email:")
    print(f"Total: {len(top_alerts_sorted)}")
    for i, p in enumerate(top_alerts_sorted[:3]):
        print(json.dumps(p, indent=2))

    if top_alerts_sorted:
        send_email(top_alerts_sorted, **SMTP_CONFIG)
    else:
        print("ℹ️ No discounted products to email.")

if __name__ == "__main__":
    run_pipeline()
