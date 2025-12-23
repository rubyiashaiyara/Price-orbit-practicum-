from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# ---------------- Chrome Setup ----------------
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()

# ---------------- Loop through pages ----------------
for page in range(1, 5):
    url = f"https://riointernational.com.bd/category/mobile?page={page}"
    driver.get(url)
    time.sleep(3)

    # ---------------- Scroll to load all products ----------------
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # ---------------- Find product blocks ----------------
    products = driver.find_elements(
        By.CSS_SELECTOR, "div.product.style-2" # inselenuum we have to use '.' 

    )

    # ---------------- Extract data for each product ----------------
    for product in products:

        # Name
        try:
            name = product.find_element(By.CSS_SELECTOR, "p.product-name").text
        except:
            name = "N/A"

        # Price
        try:
            price = product.find_element(By.CSS_SELECTOR, "ins.new-price").text
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
