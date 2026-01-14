import requests
import json
import time

def fetch_swap_products():
    # Keep this URL - it is the best one for paging through all products
    base_url = "https://api.swap.com.bd/api/v1/main-product/list"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    
    all_products = []
    
    # --- FIX: Start from Page 1, not 18 ---
    page = 1 
    has_more_pages = True
    
    print("Starting Swap API scrape...")

    while has_more_pages:
        try:
            # params for 'Smartphones' (category 2 usually)
            params = {
                "operation_type": 1,
                "category": 2, 
                "per_page": 36,
                "page": page
            }
            
            response = requests.get(base_url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if 'data' exists safely
                if not data.get("data"):
                    print(f"Page {page}: API returned no data object. Stopping.")
                    break

                # Navigate to the product list
                # The structure is data -> data -> main_products -> data
                main_data = data.get("data", {})
                main_products = main_data.get("main_products", {})
                products_list = main_products.get("data", [])
                
                if not products_list:
                    print(f"No more products found on page {page}. Stopping.")
                    has_more_pages = False
                    break
                
                print(f"Fetching page {page} - Found {len(products_list)} items...")
                
                for item in products_list:
                    # 1. Product Name
                    name = item.get("name", "Unknown Name")
                    
                    # 2. Product Image
                    image_url = item.get("image")
                    
                    # 3. Pricing Logic
                    lowest_unit = item.get("lowest_unit", {})
                    
                    raw_mrp = lowest_unit.get("mrp")
                    regular_price = float(raw_mrp) if raw_mrp else 0.0
                    
                    raw_sale = lowest_unit.get("sale_price")
                    sale_price = float(raw_sale) if raw_sale else regular_price
                    
                    # --- CALCULATE DISCOUNT PERCENTAGE ---
                    discount_pct = 0
                    if regular_price > 0 and sale_price > 0 and regular_price > sale_price:
                        discount_pct = int(((regular_price - sale_price) / regular_price) * 100)
                    
                    discount_display = f"{discount_pct}%" if discount_pct > 0 else "N/A"
                    
                    # 4. Brand Logic
                    brand_name = name.split()[0] if name else "Unknown"

                    # 5. Product Link Logic
                    product_id = item.get("id")
                    product_link = f"https://swap.com.bd/buy/smartphone/{product_id}" if product_id else "N/A"
                    
                    all_products.append({
                        "Name": name,
                        "Brand": brand_name,
                        "Regular_Price": int(regular_price),
                        "Discount_Price": int(sale_price),
                        "Discount Percentage": discount_display,
                        "Image": image_url,
                        "Product_Link": product_link
                    })
                
                # Pagination Check
                # If we got fewer items than 'per_page' (36), it's the last page
                if len(products_list) < 36:
                    has_more_pages = False
                else:
                    page += 1
                    time.sleep(1) 
                    
            else:
                print(f"API Error on page {page}: {response.status_code}")
                has_more_pages = False
                
        except Exception as e:
            print(f"Connection Failed on page {page}: {e}")
            has_more_pages = False

    return all_products

# --- Main Execution ---
if __name__ == "__main__":
    products = fetch_swap_products()
    
    print(f"\nScrape Complete. Total Products Fetched: {len(products)}")
    
    if products:
        filename = "swap_products_fixed.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=4)
            
        print(f"Data saved to '{filename}'")