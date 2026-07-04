import argparse
import logging

from binance.exceptions import BinanceAPIException, BinanceRequestException
from requests.exceptions import ConnectionError, Timeout

from bot.client import get_client
from bot.logging_config import setup_logging
from bot.orders import OrderManager
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
)


def parse_arguments():

    parser = argparse.ArgumentParser(
        description="Binance Futures Testnet Trading Bot"
    )

    parser.add_argument("--symbol", required=True, help="Trading Symbol (Example: BTCUSDT)")
    parser.add_argument("--side", required=True, help="BUY or SELL")
    parser.add_argument("--type", required=True, dest="order_type", help="MARKET or LIMIT")
    parser.add_argument("--quantity", required=True, type=float, help="Order Quantity")
    parser.add_argument("--price", type=float, help="Price (Required for LIMIT)")

    return parser.parse_args()


def main():

    setup_logging()

    logger = logging.getLogger(__name__)

    try:
        args = parse_arguments()

        symbol = validate_symbol(args.symbol)
        side = validate_side(args.side)
        order_type = validate_order_type(args.order_type)
        quantity = validate_quantity(args.quantity)
        price = validate_price(args.price, order_type)

    except ValueError as e:
        logger.error("Input validation failed: %s", e)
        print("\nInvalid input.")
        print(e)
        return

    try:
        client = get_client()
        order_manager = OrderManager(client)

        print("\nOrder Request Summary")
        print("-" * 30)
        print(f"Symbol      : {symbol}")
        print(f"Side        : {side}")
        print(f"Order Type  : {order_type}")
        print(f"Quantity    : {quantity}")

        if order_type == "LIMIT":
            print(f"Price       : {price}")

        print()

        if order_type == "MARKET":
            response = order_manager.place_market_order(symbol, side, quantity)
        else:
            response = order_manager.place_limit_order(symbol, side, quantity, price)

        print("Order Response")
        print("-" * 30)
        print(f"Order ID      : {response.get('orderId')}")
        print(f"Status        : {response.get('status')}")
        print(f"Executed Qty  : {response.get('executedQty')}")
        print(f"Average Price : {response.get('avgPrice', 'N/A')}")

        print("\nOrder placed successfully.")

    except BinanceAPIException as e:
        logger.error("Binance API rejected the order [%s]: %s", e.code, e.message)
        print("\nOrder failed: Binance rejected the request.")
        print(f"[{e.code}] {e.message}")

    except (BinanceRequestException, ConnectionError, Timeout) as e:
        logger.error("Network/connectivity error: %s", e)
        print("\nOrder failed: could not reach Binance Testnet.")
        print("Check your internet connection and try again.")

    except ValueError as e:
        logger.error("Configuration error: %s", e)
        print("\nOrder failed: configuration issue.")
        print(e)

    except Exception as e:
        logger.exception("Unexpected application error.")
        print("\nOrder failed: unexpected error.")
        print(e)


if __name__ == "__main__":
    main()