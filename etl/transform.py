def filter_products(products, brand="patagonia", min_discount=30, currency="EUR"):
    """
    Filter products based on rule-based discount criteria.
    
    Args:
        products: List of product dictionaries or dict with 'products' key
        rule_based_discount: Dict with 'brands' and 'min_discount' keys
    
    Returns:
        List of filtered products
    """
    # Handle both formats: direct list or nested in 'products' key
    if isinstance(products, dict) and 'products' in products:
        product_list = products['products']
    else:
        product_list = products
    
    
    filtered_products = []
    total_processed = 0
    brand_matches = 0
    with_discounts = 0
    
    for i, product in enumerate(product_list):
        try:
            total_processed += 1
            
            # Handle string products (JSON strings) - though yours seem to be dicts
            if isinstance(product, str):
                try:
                    import json
                    product = json.loads(product)
                except json.JSONDecodeError:
                    print(f"Skipping item {i}: invalid JSON string")
                    continue
            
            # Check if it's a dictionary
            if not isinstance(product, dict):
                print(f"Skipping item {i}: not a dictionary, type: {type(product)}")
                continue
            
            
            # Check if product has regular price (discount available)
            if 'regularPrice' not in product:
                print(f"  No discount available for: {product.get('name', 'Unknown')}")
                continue
            
            # Check discount criteria
            price_str = product.get('price', '0')
            regular_price_str = product.get('regularPrice', '0')
            
            # Handle string prices
            try:
                current_price = float(price_str) if price_str else 0
                regular_price = float(regular_price_str) if regular_price_str else 0
            except (ValueError, TypeError):
                print(f"Skipping product due to price conversion error: {product.get('name', 'Unknown')}")
                continue
            
            # Skip if no regular price (no discount)
            if regular_price == 0 or regular_price <= current_price:
                continue
            
            with_discounts += 1
            
            # Calculate discount percentage
            discount_percentage = ((regular_price - current_price) / regular_price) * 100
            
            print(f"  Discount: {discount_percentage:.1f}% (€{regular_price} -> €{current_price})")
            
            # Check if discount meets minimum requirement
            
            if discount_percentage >= min_discount:
                product_copy = product.copy()
                product_copy['brand'] = brand
                product_copy['original_price'] = regular_price
                product_copy['discounted_price'] = current_price
                product_copy['discount_percent'] = round(discount_percentage, 2)
                product_copy['savings'] = round(regular_price - current_price, 2)
                product_copy['currency'] = currency
                filtered_products.append(product_copy)
                print(f"  ✓ Meets {min_discount}% minimum discount requirement")
            else:
                print(f"  ✗ Below {min_discount}% minimum discount requirement")

        except Exception as e:
            print(f"Skipped product {i} due to error: {e}")
            continue

    print(f"\nSummary:")
    print(f"Total products processed: {total_processed}")
    print(f"Brand matches found: {brand_matches}")
    print(f"Products with discounts: {with_discounts}")
    print(f"Products meeting discount criteria: {len(filtered_products)}")

    return filtered_products