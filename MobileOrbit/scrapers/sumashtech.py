import json
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==========================================
# 🔧 CONFIGURATION
# ==========================================
BASE_URL = "https://www.sumashtech.com/category/phone-smartphone?page="
START_PAGE = 1
END_PAGE = 49

# Generalized XPath to find the Product Link (based on your input)
# We use this to identify the product card location
LINK_XPATH = '//*[@id="__nuxt"]/div/div[2]/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div/a'

# ==========================================

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)

def clean_price(price_text):
    """Extracts the first number from text like '৳ 54,000' -> 54000"""
    if not price_text: return 0
    try:
        # Remove non-digits (except decimal)
        clean = re.sub(r'[^\d]', '', price_text)
        return int(clean) if clean else 0
    except:
        return 0

def scrape_sumash_formatted():
    driver = get_driver()
    all_products = []

    try:
        for page in range(START_PAGE, END_PAGE + 1):
            url = f"{BASE_URL}{page}"
            print(f"\n--- Scraping Page {page} ---")
            driver.get(url)
            
            # Wait for content
            try:
                WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located((By.XPATH, LINK_XPATH))
                )
            except:
                print(f"Skipping page {page} (Time out or empty).")
                continue

            # Scroll to trigger lazy loading
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 1.5);")
            time.sleep(2)

            # Find all link elements
            link_elements = driver.find_elements(By.XPATH, LINK_XPATH)
            print(f"Found {len(link_elements)} items...")

            page_data = []
            for link_el in link_elements:
                try:
                    # 1. Product Link
                    product_link = link_el.get_attribute("href")
                    
                    # 2. Identify the "Card" (Parent of the link)
                    # This helps us find the price/image relative to this specific product
                    # We go up one level to the wrapper div
                    card = link_el.find_element(By.XPATH, "./..") 

                    # 3. Name & Brand
                    # Usually text inside the link or an image alt
                    full_name = link_el.text.strip()
                    if not full_name:
                        try:
                            img = link_el.find_element(By.TAG_NAME, "img")
                            full_name = img.get_attribute("alt")
                        except:
                            full_name = "Unknown Name"
                    
                    # Simple Brand extraction (First word of name)
                    brand = full_name.split(" ")[0] if full_name else "Unknown"

                    # 4. Image
                    try:
                        img_el = link_el.find_element(By.TAG_NAME, "img")
                        image_url = img_el.get_attribute("src")
                    except:
                        image_url = "N/A"

                    # 5. Price Logic
                    # We grab all text from the card to find prices
                    card_text = card.text
                    # Regex to find numbers that look like prices (e.g., 24,500)
                    # Sumash uses the ৳ symbol often, or just numbers in specific divs
                    price_matches = re.findall(r'৳\s*([\d,]+)', card_text)
                    
                    regular_price = 0
                    discount_price = 0
                    
                    if len(price_matches) >= 2:
                        # Two prices found (Sale + Regular)
                        p1 = clean_price(price_matches[0])
                        p2 = clean_price(price_matches[1])
                        regular_price = max(p1, p2)
                        discount_price = min(p1, p2)
                    elif len(price_matches) == 1:
                        # One price found (Regular only)
                        regular_price = clean_price(price_matches[0])
                        discount_price = 0
                    
                    # 6. Discount Percentage
                    if regular_price > 0 and discount_price > 0:
                        pct = int(((regular_price - discount_price) / regular_price) * 100)
                        discount_pct = f"{pct}%"
                    else:
                        discount_pct = "N/A"

                    # 7. Structure Data
                    item = {
                        "Image": image_url,
                        "Name": full_name,
                        "Brand": brand,
                        "Regular Price": regular_price,
                        "Discount Price": discount_price,
                        "Discount Percentage": discount_pct,
                        "Product Link": product_link
                    }
                    
                    # Basic validation
                    if product_link and "sumashtech.com" in product_link:
                        page_data.append(item)

                except Exception as e:
                    continue

            # Deduplicate by Link (Grid sometimes returns dupes)
            seen_links = set()
            unique_data = []
            for p in page_data:
                if p["Product Link"] not in seen_links:
                    unique_data.append(p)
                    seen_links.add(p["Product Link"])

            all_products.extend(unique_data)
            print(f"Added {len(unique_data)} products.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

    # Save to JSON
    filename = "sumash_final_output.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_products, f, indent=4, ensure_ascii=False)
    
    print(f"\n✅ Data saved to '{filename}' with {len(all_products)} items.")

if __name__ == "__main__":
    scrape_sumash_formatted()