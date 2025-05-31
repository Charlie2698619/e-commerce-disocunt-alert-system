import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import pandas as pd
import json
from typing import Dict, List

load_dotenv()



def fetch_html_with_productlist(url: str, api_key: str):
    api_response = requests.post(
        "https://api.zyte.com/v1/extract",
        auth=(api_key, ""),
        json={
            "url": url,
            "browserHtml": True,
            "productList": True,
            "productListOptions": {"extractFrom": "browserHtml"},
            "actions":[{"action": "scrollBottom",},]
        },
    )

    # Save browser-rendered HTML for inspection
    browser_html: str = api_response.json()["browserHtml"]
    product_list = api_response.json()["productList"]
    
    return browser_html, product_list


def scrape_multiple_pages(site: Dict, api_key: str, start_page=1, end_page=3) -> List[Dict]:
    """
    Scrape multiple pages from a site config using Zyte API.

    Args:
        site (dict): Dictionary with keys 'url', 'pagination_pattern', etc.
        api_key (str): Zyte API key.
        start_page (int): First page number to scrape.
        end_page (int): Last page number to scrape.

    Returns:
        list: Combined list of scraped products.
    """
    all_products = []
    print(f"\n📦 Scraping {site['name']} from page {start_page} to {end_page}...\n")

    

    base_url = site.get("url")
    pagination_pattern = site.get("pagination_pattern")

    for page_num in range(start_page, end_page + 1):
        # Build URL based on page number
        if page_num == 1:
            url = base_url
        elif pagination_pattern:
            url = pagination_pattern.format(page=page_num)
        else:
            url = base_url

        print(f"  → Scraping page {page_num}: {url}")

        try:
            html, products = fetch_html_with_productlist(url, api_key)
            if isinstance(products, dict):
                products = products.get("products", [])
            for p in products:
                p["source_site"] = site["name"]
                p["scraped_from_page"] = page_num
            print(f"✅ Found {len(products)} products on page {page_num}")
            all_products.extend(products)
        except Exception as e:
            print(f"❌ Error on page {page_num}: {e}")

    return all_products

    





