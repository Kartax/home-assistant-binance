[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Kartax&repository=home-assistant-binance&category=integration)

![Binance Logo](images/binance_logo.png)

# Binance Integration for Home Assistant
A Home Assistant Integration for the cryptocurrency trading platform [Binance](https://www.binance.com/en).

Features:
- Pull prices for a configurable list of trading pairs (e.g. BTCUSDT, ETHUSDT)
- Optionally pull Spot wallet balances and total USD value (requires API key)
- Optionally pull Simple Earn (flexible + locked) balances and total USD value (requires API key)


### Installation
I recommend to install this integration via HACS. Simply search for it\
or manually add this repository by using the "three-dots-menu" at the top right in HACS.


### Configuration

This integration is configured entirely through the Home Assistant GUI — no YAML required.

#### Step 1 – Add the integration

Go to **Settings → Integrations → Add Integration**, search for **Binance**, and click it.

Fill in:
- **API Key** (optional – leave empty for ticker-only use)
- **API Secret** (optional – leave empty for ticker-only use)
- **Decimal places** (default: 8)
- **Update interval in seconds** (default: 60)

Click **Submit**.

#### Step 2 – Configure symbols and assets

Click the **gear icon ⚙️** next to Binance → **Options**.

Fill in:
- **Ticker symbols** (comma-separated, e.g. `BTCUSDT,ETHUSDT`) — required
- **Spot wallet assets** (comma-separated, e.g. `BTC,ETH,USDT`) — optional, only useful with API key
- **Earn wallet assets** (comma-separated, e.g. `USDT,BTC`) — optional, only useful with API key

Click **Submit**. Home Assistant will reload the integration and create the sensors.

#### Sensors created

| Sensor | Created when | Description |
|--------|--------------|-------------|
| Binance Ticker {SYMBOL} | always | Current price of the trading pair |
| Binance Wallet Total (USD) | API key set | Estimated Spot wallet value in USD |
| Binance Wallet {ASSET} | Spot wallet assets configured | Spot balance per asset |
| Binance Earn Total (USD) | API key set | Estimated Earn portfolio value in USD (flexible + locked) |
| Binance Earn {ASSET} | Earn wallet assets configured | Earn balance per asset (flexible + locked combined) |

The API key only needs read permissions — no trading permissions required.

#### Migration note

If you had a `configuration.yaml` entry, it is automatically imported when Home Assistant restarts after the update.
You can then safely remove the YAML block.
