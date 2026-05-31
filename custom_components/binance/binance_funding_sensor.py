"""Binance Funding Wallet Sensor - fetches funding wallet balances using signed API requests"""

import logging
import asyncio
import aiohttp
import hashlib
import hmac
import time
from datetime import datetime
from homeassistant.helpers.entity import Entity
from homeassistant.const import STATE_UNKNOWN

logger = logging.getLogger(__name__)

BINANCE_API_BASE = "https://api.binance.com"


class BinanceFundingSensor(Entity):
    """Sensor for a single Binance funding wallet asset balance."""

    def __init__(self, asset, api_key, api_secret, decimals, update_interval):
        self._asset = asset.upper()
        self._api_key = api_key
        self._api_secret = api_secret
        self._decimals = decimals
        self._update_interval = update_interval
        self._name = f"Binance Funding {self._asset}"
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
        return self._asset

    @property
    def icon(self):
        return "mdi:bank-transfer"

    @property
    def extra_state_attributes(self):
        return self._data

    def _sign_params(self, params: str) -> str:
        """Create HMAC-SHA256 signature for Binance API."""
        return hmac.new(
            self._api_secret.encode("utf-8"),
            params.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    async def async_added_to_hass(self):
        logger.debug(
            "Adding funding sensor %s with update interval of %s seconds",
            self._name,
            self._update_interval,
        )
        await self.schedule_update()

    async def schedule_update(self):
        logger.debug("Updating funding sensor %s at %s", self._name, datetime.now())

        timestamp = int(time.time() * 1000)
        body_params = f"asset={self._asset}&timestamp={timestamp}"
        signature = self._sign_params(body_params)
        post_body = f"{body_params}&signature={signature}"

        headers = {
            "X-MBX-APIKEY": self._api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{BINANCE_API_BASE}/sapi/v1/asset/get-funding-asset",
                    data=post_body,
                    headers=headers,
                    timeout=10,
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Error response ({response.status}): {await response.text()}")
                    assets = await response.json()

                    asset_entry = next(
                        (a for a in assets if a["asset"] == self._asset),
                        None,
                    )

                    if asset_entry is None:
                        logger.warning("Asset %s not found in Binance funding wallet", self._asset)
                        self._state = 0.0
                        self._data = {"free": 0.0, "locked": 0.0, "freeze": 0.0, "withdrawing": 0.0, "total": 0.0}
                    else:
                        free = round(float(asset_entry.get("free", 0)), self._decimals)
                        locked = round(float(asset_entry.get("locked", 0)), self._decimals)
                        freeze = round(float(asset_entry.get("freeze", 0)), self._decimals)
                        withdrawing = round(float(asset_entry.get("withdrawing", 0)), self._decimals)
                        self._state = free
                        self._data = {
                            "free": free,
                            "locked": locked,
                            "freeze": freeze,
                            "withdrawing": withdrawing,
                            "total": round(free + locked + freeze, self._decimals),
                        }
                        logger.debug(
                            "Funding %s: free=%s, locked=%s, freeze=%s",
                            self._asset,
                            free,
                            locked,
                            freeze,
                        )
        except Exception as e:
            logger.error("Error updating funding sensor %s - %s", self._name, e)

        await asyncio.sleep(self._update_interval)
        asyncio.create_task(self.schedule_update())
