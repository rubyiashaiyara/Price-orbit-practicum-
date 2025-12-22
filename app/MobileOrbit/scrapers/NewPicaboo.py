import requests
import json
import time

# --- ১. ডেটা এক্সট্র্যাকশন ফাংশন ---
def fetch_and_extract_pickaboo():
    # API URL (স্মার্টফোন ক্যাটাগরি)
    url = "https://www.pickaboo.com/rest/V1/categorypageapi/smartphone?prodLimit=20&currentPage=1&featProdLimit=6&web=1"

    # Headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    print("--- Pickaboo API থেকে ডেটা আনা হচ্ছে ---")
    
    try:
        response = requests.get(url, headers=headers, timeout=10) # 10 সেকেন্ড টাইমআউট যোগ করা হলো
        
        if response.status_code != 200:
            print(f"❌ API Error: HTTP Status Code {response.status_code}")
            return

        data = response.json()
        products_list = data.get("items", [])
        extracted_products = []

        # ডেটার কাঠামো চেক করা
        if not products_list:
            print("🛑 সতর্কতা: ডেটা পাওয়া গেছে, কিন্তু 'items' কী-এর ভেতরে কোনো প্রোডাক্ট লিস্ট নেই।")
            # ডিবাগিং এর জন্য র' ডেটা সেভ করা
            with open("pickaboo_debug_raw.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("   দয়া করে 'pickaboo_debug_raw.json' ফাইলটি খুলে দেখুন প্রোডাক্ট লিস্ট কোন নামে আছে।")
            return

        print(f"✅ মোট {len(products_list)} টি প্রোডাক্ট পাওয়া গেছে। পার্সিং করা হচ্ছে...")

        for item in products_list:
            brand_name = None
            
            # ১. সরাসরি 'brand' ফিল্ড থেকে নাম নেওয়ার চেষ্টা
            if item.get("brand"):
                brand_name = item.get("brand")
            
            # ২. যদি সরাসরি না পাওয়া যায়, তবে custom_attributes-এর ভেতরে খোঁজা
            if not brand_name:
                custom_attributes = item.get("custom_attributes", [])
                for attr in custom_attributes:
                    code = attr.get("attribute_code")
                    if code == "manufacturer" or code == "brand":
                        brand_name = attr.get("value")
                        break
            
            # ৩. ফাইনাল চেক
            if not brand_name:
                brand_name = "Unknown Brand (Check Attributes)"
            
            # ডেটা সংগ্রহ
            extracted_products.append({
                "Source": "Pickaboo",
                "Name": item.get("name"),
                "Brand": brand_name,
                "Price": item.get("final_price"),
                "SKU": item.get("sku")
            })

        # --- ২. এক্সট্র্যাক্ট করা ডেটা সেভ করা ---
        if extracted_products:
            try:
                filename = "pickaboo_extracted_products.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(extracted_products, f, indent=4, ensure_ascii=False)
                
                print(f"\n✅ এক্সট্র্যাকশন সফল! ডেটা সেভ করা হয়েছে: '{filename}'")
                print("--- Sample Data Preview (First Item) ---")
                print(json.dumps(extracted_products[0], ensure_ascii=False, indent=4))
                
            except Exception as e:
                print(f"❌ ফাইল সেভ করতে সমস্যা হয়েছে: {e}")

    except requests.exceptions.RequestException as e:
        print(f"❌ কানেকশন এরর: {e}")

# --- মেইন ফাংশন ---
if __name__ == "__main__":
    fetch_and_extract_pickaboo()