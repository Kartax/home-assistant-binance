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

#### Without API key (ticker only)

```yaml
sensor:
  - platform: binance
    decimals: 8
    update_interval: 60
    symbols:
      - BTCUSDT
      - ETHUSDT
```

Creates one price sensor per symbol.

#### With API key (ticker + wallet + earn)

```yaml
sensor:
  - platform: binance
    symbols:
      - BTCUSDT
      - ETHUSDT
    api_key: !secret binance_api_key
    api_secret: !secret binance_api_secret
    wallet_assets:            # optional: per-asset Spot sensors
      - BTC
      - ETH
      - USDT
    wallet_earn_assets:       # optional: per-asset Earn sensors
      - USDT
      - BTC
```

| Sensor | Created when | Description |
|--------|--------------|-------------|
| Binance Ticker {SYMBOL} | always | Current price of the trading pair |
| Binance Wallet Total (USD) | api_key set | Estimated Spot wallet value in USD |
| Binance Wallet {ASSET} | wallet_assets configured | Spot balance per asset |
| Binance Earn Total (USD) | api_key set | Estimated Earn portfolio value in USD (flexible + locked) |
| Binance Earn {ASSET} | wallet_earn_assets configured | Earn balance per asset (flexible + locked combined) |

Store your API credentials in `secrets.yaml` and reference them with `!secret`. The API key only needs read permissions — no trading permissions required.
