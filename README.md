# Trading-Bot-on-Binance-Futures-Testnet
# Binance Futures Testnet Trading Bot

A simplified Python trading bot that places Market and Limit orders on Binance
Futures Testnet (USDT-M), with a CLI, an optional Streamlit UI, structured
logging, input validation, and layered error handling.

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py           # Binance client wrapper (auth + testnet URL config)
│   ├── orders.py            # Order placement logic (MARKET / LIMIT) + logging
│   ├── validators.py         # Input validation (symbol, side, type, qty, price)
│   ├── logging_config.py     # Logging setup (file + console handlers)
│   └── cli.py                # CLI entry point (argparse)
├── logs/
│   └── trading_bot.log       # Request/response/error logs (generated at runtime)
├── main.py                    # Wires up and runs bot/cli.py
├── streamlit_app.py           # Optional web UI (bonus) — same bot/ modules, no logic duplication
├── test_connection.py         # Standalone script to sanity-check API connectivity
├── requirements.txt
├── .env                       # API credentials (not committed — see .gitignore)
├── .gitignore
└── README.md
```

## API Used

- **Library:** [`python-binance`](https://github.com/sammchardy/python-binance)
- **Product:** Binance Futures USDT-M (FAPI)
- **Endpoint used for orders:** `futures_create_order()`

## Testnet Base URL

```
https://demo-fapi.binance.com/fapi
```

**Note:** Binance migrated the Futures Testnet REST API base URL from the
older `https://testnet.binancefuture.com` to `https://demo-fapi.binance.com`
as part of a Futures Testnet/Demo Trading revamp. The older URL still
resolves but returns `502 Bad Gateway` for order-placement requests, since
its backend for that path is no longer live. `client.py` is configured with
the current, working URL:

```python
client.FUTURES_URL = "https://demo-fapi.binance.com/fapi"
```

If you generated your API keys via the older `testnet.binancefuture.com`
portal, they should still work against the new base URL (confirmed during
testing) — no new keys were required after switching the URL.

## Setup

1. **Clone the repository**
   ```powershell
   git clone <your-repo-url>
   cd trading_bot
   ```

2. **Create and activate a virtual environment**
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Set up API credentials**

   Register on Binance Futures Testnet, generate an API key/secret, then
   create a `.env` file in the project root:
   ```
   BINANCE_API_KEY=your_api_key_here
   BINANCE_API_SECRET=your_api_secret_here
   ```

5. **(Optional) Verify connectivity before placing orders**
   ```powershell
   python test_connection.py
   ```
   Or a quick manual check:
   ```powershell
   python -c "from bot.client import get_client; c = get_client(); print(c.futures_ping())"
   ```
   An empty successful response confirms the client can reach the testnet.

## How to Run — CLI

**Market order (BUY):**
```powershell
python main.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

**Market order (SELL):**
```powershell
python main.py --symbol BTCUSDT --side SELL --type MARKET --quantity 0.01
```

**Limit order (BUY):**
```powershell
python main.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.01 --price 50000
```

**Limit order (SELL):**
```powershell
python main.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 60000
```

Each run prints an Order Request Summary, then the Order Response
(`orderId`, `status`, `executedQty`, `avgPrice`), and logs the full
request/response/error trail to `logs/trading_bot.log`.

## How to Run — Streamlit UI (Bonus)

```powershell
streamlit run streamlit_app.py
```

Opens at `http://localhost:8501`. The UI provides:
- The same order form (symbol, side, order type, quantity, price)
- Order Request Summary + Order Response, same fields as the CLI
- Inline per-field validation warnings
- Order history table for the current session
- A live log file viewer (adjustable line count, manual refresh)
- A sidebar option to check USDT futures balance and to clear the log file

## Assumptions

- **Order status on response:** Even MARKET orders frequently return
  `status: NEW` and `executedQty: 0.0000` in the immediate API response,
  rather than `FILLED`. This is expected testnet behavior — the response
  reflects the matching engine's initial acknowledgment, and the fill can
  lag slightly behind, especially on testnet where liquidity/matching can
  be inconsistent. This is not treated as an error condition by the bot.
- **Symbol validation** assumes standard USDT-M perpetual pairs (e.g.
  `BTCUSDT`, `ETHUSDT`, `1000SHIBUSDT`) — a regex checks for an
  alphanumeric prefix followed by `USDT`. It does not validate against the
  live exchange's actual listed symbols; a well-formatted but non-existent
  symbol will still be rejected, just later, by Binance's own API error.
- **LIMIT order `timeInForce`** is hardcoded to `GTC` (Good-Til-Canceled),
  since the assignment didn't specify a different policy.
- **Credentials** are read from a local `.env` file and are never logged or
  printed; `.env` is excluded from version control via `.gitignore`.

## Logging

All requests, responses, and errors are logged to `logs/trading_bot.log`
with timestamps, log level, and logger name, e.g.:

```
2026-07-04 18:24:10 | INFO | bot.orders | Placing MARKET order | Symbol=BTCUSDT | Side=BUY | Quantity=0.01
2026-07-04 18:24:11 | INFO | bot.orders | MARKET order successful | Order ID=18978307164 | Status=NEW
2026-07-04 18:25:05 | INFO | bot.orders | Placing LIMIT order | Symbol=BTCUSDT | Side=BUY | Quantity=0.01 | Price=50000.0
2026-07-04 18:25:06 | INFO | bot.orders | LIMIT order successful | Order ID=18978501009 | Status=NEW
```

Errors are logged with the specific failure type (Binance API error, network
error, or validation error) rather than a single generic catch-all, so the
log file is diagnostic rather than just a stack trace dump.

## Error Handling

- **Input validation errors** (bad symbol format, invalid side/type, missing
  LIMIT price, non-positive quantity/price) are caught before any API call
  is made, and reported clearly without contacting Binance.
- **Binance API errors** (`BinanceAPIException`) are caught and logged with
  the specific error code and message returned by Binance.
- **Network/connectivity errors** (`BinanceRequestException`, connection
  timeouts) are caught separately and reported as a connectivity issue
  rather than an API rejection.
- **Unexpected errors** are logged with full traceback via
  `logger.exception()` as a final fallback.