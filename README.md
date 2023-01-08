[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)



![Binance Logo](images/binance_logo.png)

# Binance Integration for Home Assistant
A Home Assistant Integration for the cryptocurrency trading platform [Binance](https://www.binance.com/en).

Features:
 - pull prices of a configurable list of currency pairs (e.g. BTCUSDT, XRPBTC...)
 - additional attributes for each currency pair (priceChange, highPrice, lowPrice, volume, ...)
 - **[in progress]** support configuration via the UI
 - **[planned]** fetch personal account balance over secured api

### Installation
Manually add this repository by using the "three-dots-menu" at the top right in HACS.

### Configuration
Configure the sensor(s) in ``configuration.yaml``. 
```
sensor:
  - platform: binance
    symbols:
      - BTCUSDT
      - ETHUSDT
      - ...
```
