from typing import List, Dict

def select_cheapest(products: List[Dict]) -> Dict:
    """
    Chọn sản phẩm rẻ nhất sau khi đã có final_price
    """
    if not products:
        return {}

    return min(products, key=lambda x: x["final_price"])