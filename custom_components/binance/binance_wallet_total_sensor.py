"""Binance Wallet Total Sensor - estimated Spot wallet value in USD"""

import logging
import asyncio
import aiohttp
import hashlib
import hmac
import time
from datetime import datetime
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import STATE_UNKNOWN

logger = logging.getLogger(__name__)

BINANCE_API_BASE = "https://api.binance.com"


class BinanceWalletTotalSensor(Entity):
    """Sensor showing estimated total Spot wallet value in USD."""

    def __init__(self, api_key, api_secret, decimals, update_interval):
        self._api_key = api_key
        self._api_secret = api_secret
        self._decimals = decimals
        self._update_interval = update_interval
        self._name = "Binance Wallet Total (USD)"
        self._state = STATE_UNKNOWN
        self._data = {}

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return "USD"

    @property
    def icon(self):
        return "mdi:cash-multiple"

    @property
    def device_class(self):
        return SensorDeviceClass.MONETARY

    @property
    def extra_state_attributes(self):
        return self._data

    def _sign_params(self, params: str) -> str:
        return hmac.new(
            self._api_secret.encode("utf-8"),
            params.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    async def async_added_to_hass(self):
        logger.debug(
            "Adding wallet total sensor %s with update interval of %s seconds",
            self._name,
            self._update_interval,
        )
        await self.schedule_update()

    async def schedule_update(self):
        logger.debug("Updating wallet total sensor %s at %s", self._name, datetime.now())

        timestamp = int(time.time() * 1000)
        body_params = f"needBtcValuation=true&timestamp={timestamp}"
        signature = self._sign_params(body_params)
        post_body = f"{body_params}&signature={signature}"

        headers = {"X-MBX-APIKEY": self._api_key}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{BINANCE_API_BASE}/sapi/v3/asset/getUserAsset",
                    data=post_body,
                    headers={**headers, "Content-Type": "application/x-www-form-urlencoded"},
                    timeout=10,
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Error response ({response.status}): {await response.text()}")
                    assets = await response.json()

                total_btc = sum(float(a.get("btcValuation", 0)) for a in assets)

                async with session.get(
                    f"{BINANCE_API_BASE}/api/v3/ticker/price?symbol=BTCUSDT",
                    timeout=10,
                ) as price_response:
                    if price_response.status != 200:
                        raise Exception(f"Error fetching BTC price ({price_response.status}): {await price_response.text()}")
                    price_data = await price_response.json()
                    btc_price = float(price_data["price"])

                total_usd = round(total_btc * btc_price, 2)

                asset_breakdown = {
                    a["asset"]: round(float(a.get("btcValuation", 0)), 8)
                    for a in assets
                    if float(a.get("btcValuation", 0)) > 0
                }

                self._state = total_usd
                self._data = {
                    "total_btc": round(total_btc, 8),
                    "btc_price_usd": btc_price,
                    "asset_breakdown": asset_breakdown,
                }
                logger.debug(
                    "Wallet total: %.8f BTC @ %.2f USD = %.2f USD",
                    total_btc,
                    btc_price,
                    total_usd,
                )
        except Exception as e:
            logger.error("Error updating wallet total sensor %s - %s", self._name, e)

        await asyncio.sleep(self._update_interval)
        asyncio.create_task(self.schedule_update())
