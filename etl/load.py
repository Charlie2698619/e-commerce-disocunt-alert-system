import sqlite3

def init_db(path="db/local.db"):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    
    cursor.execute(""" CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        brand TEXT,
        original_price FLOAT,
        discounted_price FLOAT,
        discount_percent FLOAT,
        url TEXT UNIQUE,
        currency TEXT,
        alert_sent INTEGER DEFAULT 0,
        source_site TEXT
    )""")
    conn.commit()
    conn.close()
    
    
def save_products(products, path="db/local.db",source_site=None):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    for p in products:
        try:
            # Parse and validate numbers with fallbacks
            name = p.get("name", "Unknown")
            original_price = float(p.get("original_price", 0) or 0)
            discounted_price = float(p.get("discounted_price", 0) or 0)
            discount_percent = float(p.get("discount_percent", 0) or 0)
            brand = p.get("brand", "Unknown")
            currency = p.get("currency", "EUR")
            url = p.get("url", "")
            site = source_site or "unknown"

            # Optional logging for debugging
            print(f"✅ Saving: {p.get('name')} – {p.get('discounted_price')} {p.get('currency')} "
      f"({p.get('discount_percent')}% off), Original: {p.get('original_price')}, Site:{site}")

            cursor.execute("""
                INSERT OR REPLACE INTO products
                (name, brand, original_price, discounted_price, discount_percent, url, currency, source_site, alert_sent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name, brand, original_price, discounted_price, discount_percent, url, currency, site, 0)
            )

        except Exception as e:
            print(f"❌ DB error for product {p.get('name')}: {e}")

    conn.commit()
    conn.close()
    print(f"✅ Attempted to save {len(products)} products.")




def fetch_saved_products(path="db/local.db", limit=99999, only_unalerted=False, site_filter=None):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    # Base query
    query = """
        SELECT name, brand, original_price, discounted_price, discount_percent, url, currency, source_site
        FROM products
    """
    conditions = []
    params = []

    if only_unalerted:
        conditions.append("alert_sent = 0")
    if site_filter:
        conditions.append("source_site = ?")
        params.append(site_filter)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " LIMIT ?"
    params.append(limit)

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()

    # Return as list of dicts
    products = [
        {
            "name": row[0],
            "brand": row[1],
            "original_price": row[2],
            "discounted_price": row[3],
            "discount_percent": row[4],
            "url": row[5],
            "currency": row[6],
            "source_site": row[7]
        }
        for row in rows
    ]

    return products