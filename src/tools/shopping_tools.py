import os
import json
from typing import List, Dict, Optional
from urllib.parse import urlparse, urlunparse, quote
from dotenv import load_dotenv

load_dotenv()

# Import SerpAPI
from serpapi import GoogleSearch

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

if not SERPAPI_KEY:
    raise ValueError("❌ SERPAPI_KEY not found in .env file!")

DISCOUNTS = {
    "HAPPYDAY10": {"type": "percent", "value": 10},
    "FIRST20": {"type": "percent", "value": 20},
    "SUMMER50K": {"type": "fixed", "value": 50000},
    "VIP30": {"type": "percent", "value": 30},
}


def search_products(query: str, max_price: int = None) -> List[Dict]:
    """Search products from Google Shopping API (SerpAPI only)."""
    
    try:
        params = {
            "q": query,
            "api_key": SERPAPI_KEY,
            "engine": "google_shopping",
            "google_domain": "google.com.vn",
            "num": 10
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        products = []
        
        for item in results.get("shopping_results", []):
            try:
                # Parse price
                price_str = str(item.get("price", "0")).strip()
                price_str = price_str.replace("₫", "").replace("$", "").replace(",", "").strip()
                price = int(float(price_str)) if price_str and price_str != "0" else 0
                
            except:
                price = 0
            
            # Skip if no valid price
            if price == 0:
                continue
            
            # Filter by max_price
            if max_price and price > max_price:
                continue
            
            raw_link = item.get("product_link", "#")
            if raw_link != "#":
                # Tách URL ra thành các phần để tránh mã hóa sai các dấu :, /, ?
                parsed = urlparse(raw_link)
                # Chỉ mã hóa các ký tự đặc biệt/dấu cách ở phần query (sau dấu ?), giữ lại các dấu =, &
                safe_query = quote(parsed.query, safe='=&?')
                # Ghép URL lại
                safe_link = urlunparse(parsed._replace(query=safe_query))
            else:
                safe_link = "#"

            products.append({
                "name": item.get("title", "Unknown"),
                "price": price,
                "currency": "VND",
                "product_link": safe_link,
                "rating": item.get("rating", "N/A"),
            })
        
        if products:
            return products
        else:
            return [{"error": f"Không tìm được sản phẩm: {query}"}]
    
    except Exception as e:
        return [{"error": f"SerpAPI error: {str(e)}"}]


def get_discount(discount_code: str) -> Dict:
    """Validate discount code."""
    code = discount_code.upper().strip()
    
    if code not in DISCOUNTS:
        return {"error": f"Mã giảm không hợp lệ: {code}", "valid": False}
    
    d = DISCOUNTS[code]
    return {
        "code": code,
        "type": d["type"],
        "value": d["value"],
        "valid": True
    }


def calc_final_price(original_price: float, discount_percent: float = 0, 
                     discount_fixed: float = 0, quantity: int = 1) -> Dict:
    """Calculate final price after discount."""
    
    price_after_fixed = max(0, original_price - discount_fixed)
    discount_amount_percent = price_after_fixed * (discount_percent / 100)
    final_unit_price = price_after_fixed - discount_amount_percent
    total_final_price = final_unit_price * quantity
    total_savings = (original_price - final_unit_price) * quantity
    
    return {
        "original_price_per_unit": int(original_price),
        "discount_fixed": int(discount_fixed),
        "discount_percent": discount_percent,
        "total_discount": int(discount_fixed + discount_amount_percent),
        "final_price_per_unit": int(final_unit_price),
        "quantity": quantity,
        "total_final_price": int(total_final_price),
        "total_savings": int(total_savings),
        "currency": "VND"
    }