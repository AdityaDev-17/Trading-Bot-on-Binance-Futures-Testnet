"""
Streamlit UI for the Binance Futures Testnet Trading Bot.

This file is a thin front-end layer only — all validation, API calls,
and logging logic still live in bot/validators.py, bot/orders.py,
and bot/client.py. Nothing is duplicated here.

Run with:
    streamlit run streamlit_app.py
"""

import os
import logging
from collections import deque

import streamlit as st

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

LOG_PATH = os.path.join("logs", "trading_bot.log")

# ---------------------------------------------------------------------------
# App-level setup (runs once per session, logging config is idempotent-safe
# because setup_logging() only ever gets called here, not also from cli.py
# in the same process)
# ---------------------------------------------------------------------------

if "logging_configured" not in st.session_state:
    setup_logging()
    st.session_state.logging_configured = True

logger = logging.getLogger("bot.streamlit_app")

if "order_history" not in st.session_state:
    st.session_state.order_history = []

st.set_page_config(page_title="Binance Futures Testnet Bot", layout="wide")
st.title("Binance Futures Testnet — Trading Bot")
st.caption("USDT-M Futures | Testnet only — no real funds are at risk.")


# ---------------------------------------------------------------------------
# Sidebar: account balance (optional nice-to-have)
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("Account")

    if st.button("Refresh USDT Balance"):
        try:
            client = get_client()
            balances = client.futures_account_balance()
            usdt = next((b for b in balances if b.get("asset") == "USDT"), None)

            if usdt:
                st.metric("Available USDT", f"{float(usdt['balance']):.2f}")
            else:
                st.warning("USDT balance not found in account response.")

        except Exception as e:
            logger.exception("Failed to fetch account balance.")
            st.error(f"Could not fetch balance: {e}")

    st.divider()
    st.header("Log File")

    if st.button("Clear Log File"):
        try:
            if os.path.exists(LOG_PATH):
                open(LOG_PATH, "w").close()
                st.success("Log file cleared.")
            else:
                st.info("No log file found yet.")
        except Exception as e:
            st.error(f"Could not clear log: {e}")


# ---------------------------------------------------------------------------
# Order form
# ---------------------------------------------------------------------------

st.subheader("Place an Order")

col1, col2 = st.columns(2)

with col1:
    symbol_input = st.text_input("Symbol", value="BTCUSDT")
    side_input = st.radio("Side", options=["BUY", "SELL"], horizontal=True)
    order_type_input = st.radio("Order Type", options=["MARKET", "LIMIT"], horizontal=True)

with col2:
    quantity_input = st.number_input("Quantity", min_value=0.0, value=0.01, step=0.001, format="%.6f")

    price_input = None
    if order_type_input == "LIMIT":
        price_input = st.number_input("Price (required for LIMIT)", min_value=0.0, value=0.0, step=0.1)
    else:
        st.text_input("Price", value="Not applicable for MARKET orders", disabled=True)

submit = st.button("Submit Order", type="primary")


# ---------------------------------------------------------------------------
# Validation + submission
# ---------------------------------------------------------------------------

if submit:
    # --- Validation step -------------------------------------------------
    validation_errors = {}
    symbol = side = order_type = quantity = price = None

    try:
        symbol = validate_symbol(symbol_input)
    except ValueError as e:
        validation_errors["symbol"] = str(e)

    try:
        side = validate_side(side_input)
    except ValueError as e:
        validation_errors["side"] = str(e)

    try:
        order_type = validate_order_type(order_type_input)
    except ValueError as e:
        validation_errors["order_type"] = str(e)

    try:
        quantity = validate_quantity(quantity_input)
    except ValueError as e:
        validation_errors["quantity"] = str(e)

    if order_type is not None:
        try:
            price = validate_price(price_input, order_type)
        except ValueError as e:
            validation_errors["price"] = str(e)

    if validation_errors:
        logger.error("Input validation failed: %s", validation_errors)
        for field, message in validation_errors.items():
            st.warning(f"**{field.replace('_', ' ').title()}**: {message}")

    else:
        # --- Order Request Summary ---------------------------------------
        st.markdown("#### Order Request Summary")
        summary = {
            "Symbol": symbol,
            "Side": side,
            "Order Type": order_type,
            "Quantity": quantity,
        }
        if order_type == "LIMIT":
            summary["Price"] = price
        st.table(summary)

        # --- Submission ----------------------------------------------------
        try:
            client = get_client()
            order_manager = OrderManager(client)

            with st.spinner("Sending order to Binance Futures Testnet..."):
                if order_type == "MARKET":
                    response = order_manager.place_market_order(symbol, side, quantity)
                else:
                    response = order_manager.place_limit_order(symbol, side, quantity, price)

            st.markdown("#### Order Response")
            resp_col1, resp_col2, resp_col3, resp_col4 = st.columns(4)
            resp_col1.metric("Order ID", response.get("orderId"))
            resp_col2.metric("Status", response.get("status"))
            resp_col3.metric("Executed Qty", response.get("executedQty"))
            resp_col4.metric("Avg Price", response.get("avgPrice", "N/A"))

            st.success("Order placed successfully.")

            st.session_state.order_history.append(
                {
                    "Symbol": symbol,
                    "Side": side,
                    "Type": order_type,
                    "Quantity": quantity,
                    "Price": price if price else "-",
                    "Order ID": response.get("orderId"),
                    "Status": response.get("status"),
                }
            )

        except Exception as e:
            # Deliberately broad here: bot/orders.py already logs the
            # specific exception type (BinanceAPIException vs network vs
            # unexpected) before re-raising, so this layer only needs to
            # surface it to the user, not re-classify it.
            logger.error("Order submission failed: %s", e)
            st.error("Order failed.")
            st.exception(e)


# ---------------------------------------------------------------------------
# Order history (this session)
# ---------------------------------------------------------------------------

st.subheader("Order History (this session)")

if st.session_state.order_history:
    st.dataframe(st.session_state.order_history, use_container_width=True)
else:
    st.caption("No orders placed yet this session.")


# ---------------------------------------------------------------------------
# Live log viewer
# ---------------------------------------------------------------------------

st.subheader("Log File (last 20 lines)")

log_lines_to_show = st.slider("Lines to show", min_value=5, max_value=100, value=20, step=5)

if os.path.exists(LOG_PATH):
    with open(LOG_PATH, "r", encoding="utf-8", errors="ignore") as f:
        last_lines = deque(f, maxlen=log_lines_to_show)
    st.code("".join(last_lines) or "(log file is empty)", language="log")
else:
    st.info("Log file has not been created yet — place an order first.")

if st.button("Refresh Log View"):
    st.rerun()