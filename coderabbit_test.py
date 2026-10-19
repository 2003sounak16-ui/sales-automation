"""
Temporary test module to verify CodeRabbit automated code review integration.
"""

def calculate_discount(price: float, discount_percent: float) -> float:
    """Calculate the final price after applying a discount percentage."""
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount percent must be between 0 and 100.")
    return price * (1 - discount_percent / 100)
