from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time


def scrape_dazzle(start_page=1, end_page=30):
    # ----------- Chrome Setup -----------
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()

    base_url = "https://dazzle.com.bd/categories/phones?page={}"

    all_products = []

    for page_num in range(start_page, end_page + 1):
        print(f"Scraping page {page_num}...")
        driver.get(base_url.format(page_num))
        time.sleep(3)

        # Scroll to load all content
        scroll_pause_time = 2
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # ----------- Scrape Product Cards -----------
        product_cards = driver.find_elements(
            By.CSS_SELECTOR,
            "div.rounded.group.shadow-md.shadow-primary\\/30.bg-white.relative.flex.flex-col.overflow-hidden"
        )

        print("Total products found:", len(product_cards))

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

            product = {
                "name": name,
                "price": price,
                "link": link
            }

            all_products.append(product)

            print(product)
            print("-----------------------------------")

    driver.quit()
    return all_products


#Example usage:
data = scrape_dazzle(1, 8)
print(data)
