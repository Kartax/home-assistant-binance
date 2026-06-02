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
1. Install via HACS: search for "Binance Integration" in HACS → Download
2. Restart Home Assistant
3. Go to Settings → Integrations → Add Integration → search "Binance" → click it

### Configuration (first setup)
In the setup dialog:
- **API Key**: leave empty for ticker-only, or enter your Binance API key (read-only)
- **API Secret**: enter your Binance API secret (required if API key is set)
- **Decimal places**: default 8
- **Update interval**: default 60 seconds

>The API Key requires read permission only!

### Configuration (symbols & assets)
After adding, click the gear icon ⚙️ → Options:
- **Ticker symbols** (required): comma-separated, e.g. `BTCUSDT,ETHUSDT`
- **Spot wallet assets** (optional): comma-separated, e.g. `BTC,ETH,USDT`
- **Earn wallet assets** (optional): comma-separated, e.g. `USDT,BTC`

### Sensors created

| Sensor | Created when | Description |
|--------|--------------|-------------|
| Binance Ticker {SYMBOL} | always | Current price of the trading pair |
| Binance Wallet Total (USD) | API key set | Estimated Spot wallet value in USD |
| Binance Wallet {ASSET} | Spot wallet assets configured | Spot balance per asset |
| Binance Earn Total (USD) | API key set | Estimated Earn portfolio value in USD (flexible + locked) |
| Binance Earn {ASSET} | Earn wallet assets configured | Earn balance per asset (flexible + locked combined) |



# Screenshots
<img width="1028" height="396" alt="image" src="https://github.com/user-attachments/assets/1a7bf21c-e6e8-4d5f-b469-4a462cb69ec0" />
<img width="1024" height="690" alt="image" src="https://github.com/user-attachments/assets/77a2f3b6-ba91-411f-b61f-e13f36b98f8c" />
<img width="1032" height="666" alt="image" src="https://github.com/user-attachments/assets/ec549d70-396c-42eb-a635-49901d5c772d" />

<img width="1055" height="548" alt="image" src="https://github.com/user-attachments/assets/f8f5ce48-d767-40a7-90e3-9b7c66279318" />
<img width="561" height="470" alt="image" src="https://github.com/user-attachments/assets/058c74d6-508b-47ca-83fc-64b6e4cc2a97" />

