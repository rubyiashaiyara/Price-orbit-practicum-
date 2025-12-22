import requests
import json

# --- ১. Dazzle API থেকে ডেটা আনা ও ফিল্টার করা (সংশোধিত) ---
def fetch_dazzle():
    url = "https://api.dazzle.com.bd/api/v2/categories/phones/products?fields=id%2Cname%2Cslug%2Cmeta%2Ccreated_at%2Cbrand_id&sort=-hot&filter%5Bbrand_id%5D=&page%5Bsize%5D=24&page%5Bnumber%5D=1&include=price%2Ccategory%2Cbrand%2CvariantsCount%2Cstock%2Cattributes%2Ccampaigns.discounts"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            products = []
            
            for item in data.get("data", []):
                # Price অবজেক্ট থেকে দাম বের করা
                price_obj = item.get("price", {})
                price = price_obj.get("price") if price_obj else 0
                
                # ব্র্যান্ড অবজেক্ট থেকে নাম বের করা (এটিই নিশ্চিতভাবে নাম দেবে)
                brand_obj = item.get("brand", {})
                brand_name = brand_obj.get("name") if brand_obj else "Unknown"
                
                # প্রোডাক্টের মূল ডেটা থেকে আসল brand_id বের করা 
                # (এটি '3' নয়, এটি প্রতিটি ব্র্যান্ডের জন্য আলাদা আইডি)
                true_brand_id = item.get("brand_id") 
                
                # Stock অবজেক্ট চেক করা
                stock_obj = item.get("stock")
                stock_status = "Available" if stock_obj else "Out of Stock"
                
                products.append({
                    "Source": "Dazzle",
                    "Name": item.get("name"),
                    "Price": price,
                    "Stock": stock_status,
                    "Brand": brand_name,     # <-- এখানে ব্র্যান্ডের নাম সেভ হবে
                    "Brand_ID": true_brand_id, # <-- অতিরিক্ত হিসেবে আসল ব্র্যান্ড আইডি সেভ হবে
                    "Image": item.get("thumbnail")
                })
            return products
        else:
            print(f"Dazzle API Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"Dazzle Connection Error: {e}")
        return []

# --- ২. Mobile Club API থেকে ডেটা আনা ও ফিল্টার করা (অপরিবর্তিত) ---
def fetch_mobile_club():
    url = "https://www.outletexpense.xyz/api/public/categorywise-products/6576?page=1&limit=20"
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            products = []
            
            for item in data.get("data", []):
                products.append({
                    "Source": "Mobile Club",
                    "Name": item.get("name"),
                    "Price": item.get("retails_price"),
                    "Stock": item.get("current_stock"),
                    # এখানে brand_name ঠিকঠাক আসছে ধরে নেওয়া হলো
                    "Brand": item.get("brand_name"), 
                    "Brand_ID": "N/A", # এই API-এ Brand_ID না থাকলে N/A দেওয়া হলো
                    "Image": item.get("image_path")
                })
            return products
        else:
            print(f"Mobile Club API Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"Mobile Club Connection Error: {e}")
        return []

# --- ৩. মেইন ফাংশন: সব ডেটা একসাথে করা এবং JSON সেভ করা ---
def main():
    print("API থেকে ডেটা আনা হচ্ছে...")
    
    # ফাংশনগুলো কল করা হচ্ছে
    dazzle_list = fetch_dazzle()
    club_list = fetch_mobile_club()
    
    # সব প্রোডাক্ট লিস্ট একত্র করা
    all_products = dazzle_list + club_list
    
    print(f"\nমোট {len(all_products)} টি প্রোডাক্ট পাওয়া গেছে।")
    
    # --- JSON ফরম্যাটে সেভ করা ---
    try:
        # ফাইলটি যেখানে স্ক্রিপ্ট আছে সেখানেই 'products.json' নামে সেভ হবে
        with open("products.json", "w", encoding="utf-8") as f:
            json.dump(all_products, f, ensure_ascii=False, indent=4)
        
        print("ডেটা সফলভাবে 'products.json' ফাইলে সেভ করা হয়েছে।")
        
        # দেখার সুবিধার জন্য প্রথম ১টি আইটেম প্রিন্ট করা হলো
        if all_products:
            print("\nSample Data Preview (First Item):")
            print(json.dumps(all_products[0], ensure_ascii=False, indent=4))
            
    except Exception as e:
        print(f"ফাইল সেভ করতে সমস্যা হয়েছে: {e}")

if __name__ == "__main__":
    main()