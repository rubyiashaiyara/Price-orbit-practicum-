from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# ---------------- Chrome Setup ----------------
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)  # Keep browser open after script
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()

# ---------------- Loop through 8 pages ----------------
for page in range(1, 8):
    url = f"https://www.pickaboo.com/product/smartphone?page={page}"
    driver.get(url)
    time.sleep(3)  # wait for page to load
    
    # ---------------- Scroll down to load all products ----------------
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # wait for lazy load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    # ---------------- Find all product divs ----------------
    products = driver.find_elements(By.CSS_SELECTOR, "div.sc-aa1edcf3-0.bqhQsw.product-one")
    
    # ---------------- Extract data for each product ----------------
    for product in products:
        # Name
        try:
            name = product.find_element(By.CLASS_NAME, "product-title").text
        except:
            name = "N/A"
        
        # Price
        try:
            price = product.find_element(By.CLASS_NAME, "product-price").text
        except:
            price = "N/A"
        
        # Link
        try:
            link = product.find_element(By.TAG_NAME, "a").get_attribute("href")
           
        except:
            link = "N/A"
        
        print(f"Name: {name}")
        print(f"Price: {price}")
        print(f"Link: {link}")
        print("-" * 40)

driver.quit()
