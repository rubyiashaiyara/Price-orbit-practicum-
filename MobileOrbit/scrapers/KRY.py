import requests
import json
import time

def fetch_all_kry_products():
    base_url = "https://api.kryinternational.com/api/v1/product/get-category-wise-products/phone"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    
    all_products = []
    current_page = 1
    total_pages = 35
    
    print("Starting scrape...")

    while current_page <= total_pages:
        try:
            params = {
                "page": current_page,
                "size": 12,
                "sortOrder": "desc",
                "search": "",
                "minPrice": 0,
                "inStock": "true",
                "categories": '["phone"]',
                "subCategories": '["Smart Phone"]'
            }
            
            response = requests.get(base_url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Update total pages on the first loop
                if current_page == 1:
                    meta = data.get("meta", {})
                    total_pages = meta.get("totalPage", 1)
                    print(f"Total pages found: {total_pages}")
                
                print(f"Fetching page {current_page} of {total_pages}...")
                
                for item in data.get("data", []):
                    # 1. Product Name
                    name = item.get("productName", "Unknown Name")
                    
                    # 2. Brand Logic
                    brand_obj = item.get("brand", {})
                    brand_name = brand_obj.get("name")
                    if not brand_name and name:
                        brand_name = name.split()[0]  # Fallback
                    
                    # 3. Product Image
                    image_list = item.get("ProductImage", [])
                    image_url = image_list[0].get("imageUrl") if image_list else None
                    
                    # 4. Price & Discount Logic
                    variations = item.get("VariationProduct", [])
                    price = 0
                    discount_price = 0
                    discount_display = "N/A"
                    
                    if variations:
                        first_variant = variations[0]
                        price = first_variant.get("price", 0)
                        discount_price = first_variant.get("discountPrice", 0)
                        
                        # Calculate Percentage
                        # Logic: Only if both prices exist and Regular Price > Discount Price
                        if price > 0 and discount_price > 0 and price > discount_price:
                            discount_val = int(((price - discount_price) / price) * 100)
                            discount_display = f"{discount_val}%"
                        else:
                            discount_display = "N/A"
                    
                    # 5. Product Link Logic (New Addition)
                    # The API returns the slug in 'productLink' or 'slug'
                    slug = item.get("productLink") or item.get("slug")
                    
                    if slug:
                        # Construct the link as requested
                        full_product_link = f"https://kryinternational.com/products/{slug}"
                    else:
                        full_product_link = "N/A"

                    # 6. Append Object
                    all_products.append({
                        "Name": name,
                        "Brand": brand_name,
                        "Price": price,
                        "Discount_Price": discount_price,
                        "Discount Percentage": discount_display,
                        "Image": image_url,
                        "Product_Link": full_product_link  # Added field
                    })
                
                current_page += 1
                time.sleep(1) # Pause
                
            else:
                print(f"Error on page {current_page}: Status {response.status_code}")
                break
                
        except Exception as e:
            print(f"Connection Failed on page {current_page}: {e}")
            break
            
    return all_products

if __name__ == "__main__":
    products = fetch_all_kry_products()
    
    print(f"\nScrape Complete. Total Products Fetched: {len(products)}")
    
    if products:
        filename = "kry_all_products_with_links.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=4)
            
        print(f"Data saved to '{filename}'")