import requests
import json

# API URL
url = "https://www.outletexpense.xyz/api/public/categorywise-products/6576?page=1&limit=20"

# Headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

# Fetch data
response = requests.get(url, headers=headers)

# Check status
if response.status_code == 200:
    data = response.json()  # Parse JSON

    # Save as JSON file
    with open("outletexpense_products.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print("JSON file saved as 'outletexpense_products.json'.")
else:
    print("Failed to fetch data. Status code:", response.status_code)
