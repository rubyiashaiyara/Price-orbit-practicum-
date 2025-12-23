from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time


# -----------------------------
# COMMON BROWSER SETUP
# -----------------------------
def start_driver():
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", False)
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    return driver


# =============================
# SCRAPER 1 — DAZZLE
# =============================
def scrape_dazzle(start_page=1, end_page=8):
    driver = start_driver()
    base_url = "https://dazzle.com.bd/categories/phones?page={}"

    all_products = []

    for page_num in range(start_page, end_page + 1):
        print(f"Scraping Dazzle — page {page_num}")

        driver.get(base_url.format(page_num))
        time.sleep(3)

        # Scroll to bottom (lazy loading)
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        product_cards = driver.find_elements(
            By.CSS_SELECTOR,
            "div.rounded.group.shadow-md.shadow-primary\\/30.bg-white.relative.flex.flex-col.overflow-hidden"
        )

        for card in product_cards:
            try:
                name = card.find_element(
                    By.CSS_SELECTOR,
                    "a.text-center.text-gray-700.line-clamp-2"
                ).text
            except:
                name = "N/A"

            try:
                price = card.find_element(By.CSS_SELECTOR, "span.font-semibold.text-sm").text
            except:
                price = "N/A"

            try:
                link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
            except:
                link = "N/A"

            all_products.append({
                "name": name,
                "price": price,
                "link": link
            })

    driver.quit()
    return all_products


# =============================
# SCRAPER 2 — PICKABOO
# =============================
def scrape_pickaboo(start_page=1, end_page=8):
    driver = start_driver()

    all_products = []

    for page in range(start_page, end_page + 1):
        print(f"Scraping Pickaboo — page {page}")

        url = f"https://www.pickaboo.com/product/smartphone?page={page}"
        driver.get(url)
        time.sleep(3)

        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        products = driver.find_elements(By.CSS_SELECTOR, "div.sc-aa1edcf3-0.bqhQsw.product-one")

        for product in products:

            try:
                name = product.find_element(By.CLASS_NAME, "product-title").text
            except:
                name = "N/A"

            try:
                price = product.find_element(By.CLASS_NAME, "product-price").text
            except:
                price = "N/A"

            try:
                link = product.find_element(By.TAG_NAME, "a").get_attribute("href")
            except:
                link = "N/A"

            all_products.append({
                "name": name,
                "price": price,
                "link": link,
            })

    driver.quit()
    return all_products


# =============================
# SCRAPER 3 — RIO INTERNATIONAL
# =============================
def scrape_rio(start_page=1, end_page=4):
    driver = start_driver()

    all_products = []

    for page in range(start_page, end_page + 1):
        print(f"Scraping Rio International — page {page}")

        url = f"https://riointernational.com.bd/category/mobile?page={page}"
        driver.get(url)
        time.sleep(3)

        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        products = driver.find_elements(
            By.CSS_SELECTOR, "div.product.style-2"
        )

        for product in products:

            try:
                name = product.find_element(By.CSS_SELECTOR, "p.product-name").text
            except:
                name = "N/A"

            try:
                price = product.find_element(By.CSS_SELECTOR, "ins.new-price").text
            except:
                price = "N/A"

            try:
                link = product.find_element(By.TAG_NAME, "a").get_attribute("href")
            except:
                link = "N/A"

            all_products.append({
                "name": name,
                "price": price,
                "link": link
            })

    driver.quit()
    return all_products


import requests

# =============================
# SCRAPER 4 — MOBILE CLUB (API)
# =============================
def scrape_mobileclub(page=1, limit=20):

    url = f"https://www.outletexpense.xyz/api/public/categorywise-products/6576?page={page}&limit={limit}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        all_products = []

        for item in data.get("data", []):
            all_products.append({
                "name": item.get("name", "N/A"),
                "price": item.get("retails_price", 0),
                "brand": item.get("brand_name", "Unknown"),
                "stock": item.get("current_stock"),
                "link": "",
            })

        return all_products

    except Exception as e:
        print("Mobile Club API error:", e)
        return []
