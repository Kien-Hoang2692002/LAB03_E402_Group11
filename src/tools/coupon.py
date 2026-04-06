import random

def apply_coupon(product: dict) -> float:
    """
    Giả lập áp mã giảm giá
    """
    # discount_percent = random.choice([0.05, 0.1, 0.15])  # 5% - 15%
    # final_price = product["extracted_old_price"] * (1 - discount_percent)

    final_price = product["extracted_price"]

    return final_price