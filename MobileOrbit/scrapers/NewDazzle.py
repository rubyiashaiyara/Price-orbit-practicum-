import requests
import json
import time

def fetch_dazzle_offers():
    base_url = "https://api.dazzle.com.bd/api/v2/categories/phones/products"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    
    all_products = []
    print("Starting data fetch for 33 pages...")

    # Loop from page 1 to 33
    for page in range(1, 30):
        params = {
            "fields": "id,name,slug,meta,created_at,brand_id",
            "sort": "-hot",
            "filter[brand_id]": "",
            "page[size]": 24,
            "page[number]": page,
            "include": "price,category,brand,variantsCount,stock,attributes,campaigns.discounts"
        }

        try:
            print(f"Fetching page {page}...")
            response = requests.get(base_url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                page_items = data.get("data", [])
                
                if not page_items:
                    print(f"No more products found on page {page}.")
                    break
                
                for item in page_items:
                    # --- Price Logic ---
                    price_data = item.get("price", {}) 
                    
                    # 1. Offer Price
                    raw_offer = price_data.get("price", 0)
                    offer_price = int(float(raw_offer)) if raw_offer else 0
                    
                    # 2. Regular Price
                    raw_regular = price_data.get("compare_price")
                    
                    if raw_regular is None or raw_regular == 0:
                        regular_price = offer_price
                    else:
                        regular_price = int(float(raw_regular))

                    # 3. Calculate Discount Percentage
                    discount_pct = 0
                    if regular_price > 0 and regular_price > offer_price:
                        discount_pct = int(((regular_price - offer_price) / regular_price) * 100)
                    
                    discount_display = f"{discount_pct}%" if discount_pct > 0 else "N/A"

                    # 4. Brand Name
                    brand_name = item.get("brand", {}).get("name", "Unknown")

                    # 5. Product Link Logic (New Addition)
                    slug = item.get("slug")
                    # Construct the link using the base URL + slug
                    product_link = f"https://dazzle.com.bd/product/{slug}" if slug else "N/A"

                    all_products.append({
                        "Image": item.get("thumbnail"),
                        "Name": item.get("name"),
                        "Regular_Price": regular_price,
                        "Offer_Price": offer_price,
                        "Discount Percentage": discount_display,
                        "Brand": brand_name,
                        "Product_Link": product_link  # Added field
                    })
            else:
                print(f"Failed to fetch page {page}. Status: {response.status_code}")
                
            # Polite delay
            time.sleep(1)
            
        except Exception as e:
            print(f"Error on page {page}: {e}")

    return all_products

# --- Main Execution ---
if __name__ == "__main__":
    offer_items = fetch_dazzle_offers()
    
    print(f"\nTotal Products Fetched: {len(offer_items)}")
    
    if offer_items:
        filename = "dazzle_products_with_links.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(offer_items, f, ensure_ascii=False, indent=4)
            
        print(f"Successfully saved data to '{filename}'")
    else:
        print("No products found.")