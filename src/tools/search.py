from typing import List, Dict

def search_products(query: str, max_price: int) -> List[Dict]:
    """
    Mock search sản phẩm (sau này thay bằng API Shopee/Lazada)
    """
    products = [
        {"id": "p1", "name": "Tai nghe Sony", "price": 950000, "link": "https://example.com/sony"},
        {"id": "p2", "name": "Tai nghe JBL", "price": 850000, "link": "https://example.com/jbl"},
        {"id": "p3", "name": "Tai nghe Logitech", "price": 1050000, "link": "https://example.com/logitech"},
    ]

    # filter theo giá
    filtered = [p for p in products if p["price"] <= max_price]

    return filtered