import re
from typing import Optional


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{2,15}USDT$")


def validate_symbol(symbol: str) -> str:
    """
    Validate trading symbol.
    """

    symbol = symbol.upper().strip()

    if not symbol:
        raise ValueError("Trading symbol cannot be empty.")

    if not SYMBOL_PATTERN.match(symbol):
        raise ValueError(
            f"Invalid symbol format: '{symbol}'. "
            "Expected a USDT-M futures pair, e.g. BTCUSDT."
        )

    return symbol


def validate_side(side: str) -> str:
    """
    Validate BUY or SELL.
    """

    side = side.upper().strip()

    if side not in VALID_SIDES:
        raise ValueError("Side must be either BUY or SELL.")

    return side


def validate_order_type(order_type: str) -> str:
    """
    Validate MARKET or LIMIT.
    """

    order_type = order_type.upper().strip()

    if order_type not in VALID_ORDER_TYPES:
        raise ValueError("Order type must be MARKET or LIMIT.")

    return order_type


def validate_quantity(quantity: float) -> float:
    """
    Quantity must be greater than zero.
    """

    quantity = float(quantity)

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")

    return quantity


def validate_price(price: Optional[float], order_type: str) -> Optional[float]:
    """
    Price is mandatory only for LIMIT orders.
    """

    if order_type.upper() == "LIMIT":

        if price is None:
            raise ValueError("Price is required for LIMIT orders.")

        price = float(price)

        if price <= 0:
            raise ValueError("Price must be greater than zero.")

        return price

    return None