# 🛍️ E-Commerce Discount Alert System + Power BI Dashboard

This project is a fully automated pipeline that monitors extreme discounts for specific brands (e.g., Patagonia) across multiple e-commerce websites. It scrapes product listings, filters based on rule-based logic, stores the results in a local SQLite database, sends email alerts, and provides a Power BI dashboard for rich data analysis.

---

## 🚀 Features

- 🔍 **Scrapes Product Listings** from multiple sites 
- 🧠 **Applies Rule-Based Discount Detection** for extreme deals (e.g., ≥30%)
- 💾 **Stores Data in SQLite** database for historical tracking and querying
- 📧 **Sends Email Alerts** with product details and CSV attachment
- 📊 **Power BI Dashboard** via ODBC for business insights

---

## 🔁 ETL Pipeline Overview

### 🧩 Extract
- Tool: Zyte Smart Proxy Manager (handles JavaScript-rendered sites)
- Functions: `fetch_html_with_productlist()`, `scrape_multiple_pages()`
- Output: Clean product list 

### 🧼 Transform
- Function: `filter_products(products, brand, min_discount, currency)`
- Logic:
  - Filter by brand
  - Calculate discount %
  - Filter by minimum discount threshold
- Output: List of discounted products with min_discount condition

### 🗃 Load
- Database: SQLite (`db/local.db`)
- Functions:
  - `init_db()`: Set up schema
  - `save_products()`: Insert new products
  - `fetch_saved_products()`: Retrieve unalerted deals

---

## 📧 Email Notification System

- Function: `send_email(products, smtp_config)`
- Sends HTML-formatted product list and attaches CSV
- Can be run via scheduler (cron/Task Scheduler) for daily alerts

---

## 📊 Power BI Dashboard

- ODBC Setup: Uses [SQLite ODBC Driver](http://www.ch-werner.de/sqliteodbc/)
- Visuals:
  - discounts distribution by websites
  - Product discount distribution
  - Daily scraped product summary

---

## 📌 Future Enhancements

- Historical price change tracking 
- Product lifecycle pricing curves
- Email click tracking and A/B testing
- Integration with Telegram/Slack alerts
- 

## 👨‍💻 Author

**Charlie2698619**  
Built for learning, automation, and marketing analytics use cases.  
Pull requests and suggestions welcome!
