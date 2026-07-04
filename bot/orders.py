import logging

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException


logger = logging.getLogger(__name__)


class OrderManager:
    def __init__(self, client: Client):
        self.client = client

    def place_market_order(self, symbol: str, side: str, quantity: float):
        """
        Place a MARKET order on Binance Futures Testnet.
        """

        logger.info("Placing MARKET order | Symbol=%s | Side=%s | Quantity=%s", symbol, side, quantity)

        try:
            response = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type="MARKET",
                quantity=quantity,
            )

            logger.info(
                "MARKET order successful | Order ID=%s | Status=%s",
                response.get("orderId"),
                response.get("status"),
            )
            logger.debug("Full MARKET order response: %s", response)

            return response

        except BinanceAPIException as e:
            logger.error("Binance API Error [%s]: %s", e.code, e.message)
            raise

        except BinanceRequestException as e:
            logger.error("Network Error: %s", e)
            raise

        except Exception:
            logger.exception("Unexpected error while placing MARKET order.")
            raise

    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float):
        """
        Place a LIMIT order on Binance Futures Testnet.
        """

        logger.info(
            "Placing LIMIT order | Symbol=%s | Side=%s | Quantity=%s | Price=%s",
            symbol, side, quantity, price,
        )

        try:
            response = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type="LIMIT",
                quantity=quantity,
                price=price,
                timeInForce="GTC",
            )

            logger.info(
                "LIMIT order successful | Order ID=%s | Status=%s",
                response.get("orderId"),
                response.get("status"),
            )
            logger.debug("Full LIMIT order response: %s", response)

            return response

        except BinanceAPIException as e:
            logger.error("Binance API Error [%s]: %s", e.code, e.message)
            raise

        except BinanceRequestException as e:
            logger.error("Network Error: %s", e)
            raise

        except Exception:
            logger.exception("Unexpected error while placing LIMIT order.")
            raise