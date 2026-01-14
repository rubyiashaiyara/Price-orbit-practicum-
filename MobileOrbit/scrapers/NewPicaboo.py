import requests
import json
import time

def fetch_pickaboo_data():
    base_url = "https://www.pickaboo.com/rest/V1/categorypageapi/smartphone"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    all_products = []
    print("Starting data fetch...")

    # Loop through pages 1 to 10
    for page in range(1, 10):
        params = {
            "currentPage": page,
            "featProdLimit": 6,
            "web": 1
        }

        try:
            print(f"Fetching page {page}...")
            response = requests.get(base_url, params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                products = data.get("cat_prods", [])
                
                if not products:
                    print(f"No more products found on page {page}.")
                    break

                for prod in products:
                    name = prod.get("product_name", "Unknown")
                    brand = name.split(" ")[0] if name else "Unknown"
                    
                    # Get Prices
                    regular_price = prod.get("product_price", 0)
                    special_price = prod.get("product_specialPrice", 0)
                    
                    # --- CALCULATE DISCOUNT PERCENTAGE ---
                    discount_pct = 0
                    if regular_price and special_price and regular_price > special_price:
                        # Formula: ((Regular - Special) / Regular) * 100
                        discount_pct = int(((regular_price - special_price) / regular_price) * 100)
                    
                    discount_display = f"{discount_pct}%" if discount_pct > 0 else "N/A"

                    # --- PRODUCT LINK LOGIC ---
                    # Retrieve the slug. Common keys in this API are 'url_key' or 'slug'.
                    # We check 'url_key' first, then 'slug', then 'product_url_key' just in case.
                    slug = prod.get("url_key") or prod.get("slug") or prod.get("product_url_key")
                    
                    # Construct the link
                    if slug:
                        product_link = f"https://www.pickaboo.com/product-detail/{slug}"
                    else:
                        product_link = "N/A"

                    # Extract specific fields
                    product_info = {
                        "Image": prod.get("product_img"),
                        "Name": name,
                        "Brand": brand,
                        "Regular Price": regular_price,
                        "Discount Price": special_price,
                        "Discount Percentage": discount_display,
                        "Product Link": product_link  # <--- Added Field
                    }
                    
                    # Only add valid products (Price check)
                    if product_info["Regular Price"]:
                        all_products.append(product_info)
            else:
                print(f"Failed to fetch page {page}. Status Code: {response.status_code}")
        
        except Exception as e:
            print(f"An error occurred on page {page}: {e}")

        # Politeness delay
        time.sleep(1)

    print(f"\nSuccessfully fetched {len(all_products)} products.")
    
    # Save to JSON format
    output_filename = "pickaboo_smartphones_with_links.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(all_products, f, indent=4, ensure_ascii=False)
    
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    fetch_pickaboo_data()