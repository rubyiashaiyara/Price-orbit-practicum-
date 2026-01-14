import requests
import json
import time

def fetch_swap_products():
    base_url = "https://api.swap.com.bd/api/v1/main-product/list"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    all_products = []
    page = 1
    has_more_pages = True

    print("Starting Swap API scrape...")

    while has_more_pages:
        params = {
            "operation_type": 1,
            "category": 2,
            "per_page": 36,
            "page": page
        }

        response = requests.get(base_url, headers=headers, params=params)

        if response.status_code != 200:
            break

        data = response.json()
        products_list = data.get("data", {}).get("main_products", {}).get("data", [])

        if not products_list:
            break

        print(f"Fetching page {page} - {len(products_list)} products")

        for item in products_list:
            name = item.get("name", "Unknown")
            image_url = item.get("image")

            lowest_unit = item.get("lowest_unit", {})
            regular_price = float(lowest_unit.get("mrp", 0))
            sale_price = float(lowest_unit.get("sale_price", regular_price))

            discount_pct = (
                int(((regular_price - sale_price) / regular_price) * 100)
                if regular_price > sale_price > 0 else 0
            )

            # -------- SHOP LOCATION LOGIC --------
            shop_locations = []
            units = item.get("units", [])

            for unit in units:
                shop = unit.get("shop", {})
                if shop:
                    shop_locations.append({
                        "Shop_Name": shop.get("name"),
                        "Shop_Address": shop.get("address")
                    })

            product_id = item.get("id")

            all_products.append({
                "Name": name,
                "Brand": name.split()[0],
                "Regular_Price": int(regular_price),
                "Discount_Price": int(sale_price),
                "Discount_Percentage": f"{discount_pct}%" if discount_pct else "N/A",
                "Image": image_url,
                "Product_Link": f"https://swap.com.bd/buy/smartphone/{product_id}",
                "Shop_Locations": shop_locations
            })

        if len(products_list) < 36:
            has_more_pages = False
        else:
            page += 1
            time.sleep(1)

    return all_products


if __name__ == "__main__":
    products = fetch_swap_products()
    print(f"Total Products: {len(products)}")

    with open("swap_products_with_shops.json", "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=4)

    print("Saved: swap_products_with_shops.json")
