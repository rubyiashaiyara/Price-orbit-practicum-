# products/scrapers.py
import requests
import time
from .models import Product 
import logging

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

# --- Helper Function ---
def save_product(data, store):
    try:
        obj, created = Product.objects.update_or_create(
            link=data['Link'],
            defaults={
                'name': data['Name'],
                'brand': data['Brand'],
                'image': data['Image'],
                'regular_price': data['Regular_Price'],
                'discount_price': data['Discount_Price'],
                'discount_percentage': data['Discount_Percentage'],
                'store_name': store
            }
        )
        print(f"[{store}] {'Created' if created else 'Updated'}: {data['Name']}")
    except Exception as e:
        print(f"Error saving {data['Name']} from {store}: {e}")

# --- Scraper Functions ---

def fetch_kry_products():
    print("\n--- Starting KRY International ---")
    base_url = "https://api.kryinternational.com/api/v1/product/get-category-wise-products/phone"
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    
    # [FIXED] Start from Page 1
    page = 1
    
    while True:
        try:
            params = {
                "page": page,
                "size": 12,
                "sortOrder": "desc",
                "inStock": "true",
                "categories": '["phone"]',
                "subCategories": '["Smart Phone"]'
            }
            response = requests.get(base_url, headers=headers, params=params, timeout=30)
            if response.status_code != 200:
                print(f"KRY: HTTP {response.status_code} on page {page}")
                break
            
            data = response.json()
            products = data.get("data", [])
            if not products:
                print(f"KRY: No more products on page {page}")
                break
            
            print(f"KRY: Processing page {page} ({len(products)} items)...")

            for item in products:
                imgs = item.get("ProductImage", [])
                img_url = imgs[0].get("imageUrl") if imgs else "N/A"
                
                variations = item.get("VariationProduct", [])
                price = variations[0].get("price", 0) if variations else 0
                disc_price = variations[0].get("discountPrice", price) if variations else price
                
                pct = "N/A"
                if price > disc_price > 0:
                    pct = f"{int(((price - disc_price) / price) * 100)}%"
                
                slug = item.get("productLink") or item.get("slug")
                link = f"https://kryinternational.com/products/{slug}" if slug else "N/A"

                save_product({
                    "Name": item.get("productName", "Unknown"),
                    "Brand": item.get("Brand", "Unknown"),
                    "Image": img_url,
                    "Regular_Price": price,
                    "Discount_Price": disc_price,
                    "Discount_Percentage": pct,
                    "Link": link
                }, "KRY International")
            
            page += 1
            time.sleep(1)
        except Exception as e:
            print(f"KRY Error on page {page}: {e}")
            break

def fetch_dazzle_products():
    print("\n--- Starting Dazzle ---")
    base_url = "https://api.dazzle.com.bd/api/v2/categories/phones/products"
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    
    page = 1
    
    while True:
        try:
            params = {"page[size]": 24, "page[number]": page, "include": "price,brand"}
            response = requests.get(base_url, headers=headers, params=params, timeout=30)
            
            if response.status_code != 200 or not response.json().get("data"):
                break
            
            data = response.json().get("data", [])
            if not data:
                print(f"Dazzle: No more products on page {page}")
                break
                
            print(f"Dazzle: Processing page {page} ({len(data)} items)...")
            
            for item in data:
                # --- FIX 1: Safe Price Extraction ---
                # use (item.get("price") or {}) to handle cases where price is null
                price_data = item.get("price") or {} 
                
                offer = int(float(price_data.get("price", 0) or 0))
                reg = int(float(price_data.get("compare_price") or offer))
                
                pct = "N/A"
                if reg > offer > 0:
                    pct = f"{int(((reg - offer) / reg) * 100)}%"
                
                slug = item.get("slug")
                link = f"https://dazzle.com.bd/product/{slug}" if slug else "N/A"

                # --- FIX 2: Safe Brand Extraction ---
                # use (item.get("brand") or {}) to handle cases where brand is null
                brand_obj = item.get("brand") or {}
                brand_name = brand_obj.get("name", "Unknown")

                save_product({
                    "Name": item.get("name", "Unknown"),
                    "Brand": brand_name,
                    "Image": item.get("thumbnail", "N/A"),
                    "Regular_Price": reg,
                    "Discount_Price": offer,
                    "Discount_Percentage": pct,
                    "Link": link
                }, "Dazzle")
            
            page += 1
            time.sleep(1)
        except Exception as e:
            print(f"Dazzle Error on page {page}: {e}")
            break

def fetch_pickaboo_products():
    print("\n--- Starting Pickaboo ---")
    base_url = "https://www.pickaboo.com/rest/V1/categorypageapi/smartphone"
    headers = {"User-Agent": "Mozilla/5.0"}

    # [FIXED] Start from Page 1
    page = 1
    
    while True:
        try:
            params = {"currentPage": page, "web": 1}
            response = requests.get(base_url, headers=headers, params=params, timeout=30)
            if response.status_code != 200:
                break
            
            prods = response.json().get("cat_prods", [])
            if not prods:
                break
            
            print(f"Pickaboo: Processing page {page} ({len(prods)} items)...")

            for prod in prods:
                reg = prod.get("product_price", 0)
                special = prod.get("product_specialPrice", reg) or reg
                pct = "N/A"
                if reg > special > 0:
                    pct = f"{int(((reg - special) / reg) * 100)}%"
                
                slug = prod.get("url_key") or prod.get("slug")
                link = f"https://www.pickaboo.com/product-detail/{slug}" if slug else "N/A"

                save_product({
                    "Name": prod.get("product_name", "Unknown"),
                    "Brand": prod.get("product_name", "").split(maxsplit=1)[0] if prod.get("product_name") else "Unknown",
                    "Image": prod.get("product_img", "N/A"),
                    "Regular_Price": reg,
                    "Discount_Price": special,
                    "Discount_Percentage": pct,
                    "Link": link
                }, "Pickaboo")
            
            page += 1
            time.sleep(1)
        except Exception as e:
            print(f"Pickaboo Error on page {page}: {e}")
            break

def fetch_swap_products():
    print("\n--- Starting Swap ---")
    base_url = "https://api.swap.com.bd/api/v1/main-product/list"
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    
    # [ALREADY FIXED] Starts at 1
    page = 1
    
    while True:
        try:
            params = {"operation_type": 1, "category": 2, "per_page": 36, "page": page}
            response = requests.get(base_url, headers=headers, params=params, timeout=30)
            if response.status_code != 200:
                break
            
            data_list = response.json().get("data", {}).get("main_products", {}).get("data", [])
            if not data_list:
                break
            
            print(f"Swap: Processing page {page} ({len(data_list)} items)...")

            for item in data_list:
                unit = item.get("lowest_unit", {})
                reg = float(unit.get("mrp") or 0)
                sale = float(unit.get("sale_price") or reg)
                pct = "N/A"
                if reg > sale > 0:
                    pct = f"{int(((reg - sale) / reg) * 100)}%"
                
                pid = item.get("id")
                link = f"https://swap.com.bd/buy/smartphone/{pid}" if pid else "N/A"

                save_product({
                    "Name": item.get("name", "Unknown"),
                    "Brand": item.get("name", "").split(maxsplit=1)[0] if item.get("name") else "Unknown",
                    "Image": item.get("image", "N/A"),
                    "Regular_Price": int(reg),
                    "Discount_Price": int(sale),
                    "Discount_Percentage": pct,
                    "Link": link
                }, "Swap")
            
            page += 1
            time.sleep(1)
        except Exception as e:
            print(f"Swap Error on page {page}: {e}")
            break

# --- Main Runner ---
def run_all_scrapers():
    fetch_kry_products()
    fetch_dazzle_products()
    fetch_pickaboo_products()
    fetch_swap_products()
    print("\nAll scrapers completed!")