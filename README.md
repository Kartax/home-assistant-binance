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

This integration is configured via the Home Assistant GUI — no YAML required.

> **Migrating from YAML?** Existing `configuration.yaml` entries are automatically imported on first startup. You can then remove them from your YAML file.

#### Step 1 — Add the integration

Go to **Settings → Integrations → Add Integration** and search for **Binance**.

Enter your credentials and preferences:

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| API Key | No | _(empty)_ | Binance API key — needed for wallet and earn sensors |
| API Secret | No | _(empty)_ | Binance API secret |
| Decimal places | No | 8 | Number of decimal places for sensor values |
| Update interval (seconds) | No | 60 | How often sensors refresh |

#### Step 2 — Configure symbols and assets

After the integration is added, click the **gear icon** (Configure) to set up your ticker symbols and wallet assets:

| Field | Description | Example |
|-------|-------------|---------|
| Ticker symbols | Comma-separated trading pairs (required) | `BTCUSDT,ETHUSDT` |
| Spot wallet assets | Comma-separated assets for per-asset Spot sensors (optional) | `BTC,ETH,USDT` |
| Earn wallet assets | Comma-separated assets for per-asset Earn sensors (optional) | `USDT,BTC` |

#### Sensors created

| Sensor | Created when | Description |
|--------|--------------|-------------|
| Binance Ticker {SYMBOL} | always | Current price of the trading pair |
| Binance Wallet Total (USD) | API key set | Estimated Spot wallet value in USD |
| Binance Wallet {ASSET} | Spot wallet assets configured | Spot balance per asset |
| Binance Earn Total (USD) | API key set | Estimated Earn portfolio value in USD (flexible + locked) |
| Binance Earn {ASSET} | Earn wallet assets configured | Earn balance per asset (flexible + locked combined) |

The API key only needs read permissions — no trading permissions required.
