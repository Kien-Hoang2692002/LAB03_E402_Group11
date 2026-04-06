from typing import List, Dict
import serpapi
import os
import re
from dotenv import load_dotenv

load_dotenv()

def parse_price(price_str):
    if not price_str:
        return None

    # lấy số từ string "$12.99" → 129900 (VND giả lập)
    numbers = re.findall(r"\d+[\.,]?\d*", price_str)
    if not numbers:
        return None

    price = float(numbers[0].replace(",", ""))
    
    # ⚠️ Google trả USD → convert tạm sang VND
    return int(price * 25000)


def search_products(query: str, max_price: int = None) -> List[Dict]:
    # client = serpapi.Client(
    #     api_key=os.getenv(SERPAPI_KEY)
    # )
    client = serpapi.Client(api_key="75badc137666675b5da3057a212e2ccd1cd62972c443ec3aac4654d4d3847278") 
    results = client.search({ 
        "engine": "google_shopping", 
         "q": query, 
         "location": "Vietnam", 
         "hl": "vi", 
         "gl": "vn", 
         "google_domain": "google.com", 
         "start": "0", 
         "safe": "active" 
    }) 
    shopping_results = results["shopping_results"]

    products = []

    for result in shopping_results:
        title = result.get("title")
        price_str = result.get("extracted_price")

        price = parse_price(price_str)

        products.append({
            "name": title,
            "price": price,
            "price_str": price_str,
        })

    print(products)

    return products