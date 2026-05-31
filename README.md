[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Kartax&repository=home-assistant-binance&category=integration)

![Binance Logo](images/binance_logo.png)

# Binance Integration for Home Assistant
A Home Assistant Integration for the cryptocurrency trading platform [Binance](https://www.binance.com/en).

Features:
 - [x] pull prices of a configurable list of currency pairs (e.g. BTCUSDT, XRPBTC...)
 - [x] additional attributes for each currency pair (priceChange, highPrice, lowPrice, volume, ...)
 - [x] optionally pull wallet balances for configured assets (requires Binance API key & secret)

![screenshot_2](images/screenshot_2.png) ![screenshot_1](images/screenshot_1.png) 


### Installation
I recommend to install this integration via HACS. Simply search for it\
or manually add this repository by using the "three-dots-menu" at the top right in HACS.


### Configuration
Configure the sensor(s) in ``configuration.yaml``.

#### Ticker only (no API key required)
```yaml
sensor:
  - platform: binance
    decimals: 8
    update_interval: 60
    symbols:
      - BTCUSDT
      - ETHUSDT
```

#### Ticker + Wallet balances (API key required)

To enable wallet balance sensors you need a Binance API key with **read permissions** (no trading permissions required).
Create one at [Binance API Management](https://www.binance.com/en/my/settings/api-management).

```yaml
sensor:
  - platform: binance
    decimals: 8
    update_interval: 60
    symbols:
      - BTCUSDT
      - ETHUSDT
    api_key: "YOUR_BINANCE_API_KEY"
    api_secret: "YOUR_BINANCE_API_SECRET"
    wallet_assets:
      - BTC
      - ETH
      - USDT
      - BNB
```

Each `wallet_assets` entry creates a dedicated sensor named `sensor.binance_wallet_<ASSET>` with the following attributes:

| Attribute | Description |
|-----------|-------------|
| `free`    | Available (spendable) balance |
| `locked`  | Balance currently locked in open orders |
| `total`   | `free` + `locked` |

The sensor **state** is the `free` balance. Unit of measurement is the asset symbol (e.g. `BTC`).

> **Security note:** It is recommended to store your API credentials in `secrets.yaml` and reference them via `!secret`:
> ```yaml
> api_key: !secret binance_api_key
> api_secret: !secret binance_api_secret
> ```
