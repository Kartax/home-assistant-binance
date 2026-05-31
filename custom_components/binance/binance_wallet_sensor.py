"""Binance Wallet Sensor - fetches account balances using signed API requests"""

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


class BinanceWalletSensor(Entity):
    """Sensor for a single Binance wallet asset balance."""

    def __init__(self, asset, api_key, api_secret, decimals, update_interval):
        self._asset = asset.upper()
        self._api_key = api_key
        self._api_secret = api_secret
        self._decimals = decimals
        self._update_interval = update_interval
        self._name = f"Binance Wallet {self._asset}"
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
        return "mdi:wallet"

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
            "Adding wallet sensor %s with update interval of %s seconds",
            self._name,
            self._update_interval,
        )
        asyncio.create_task(self.schedule_update())

    async def schedule_update(self):
        logger.debug("Updating wallet sensor %s at %s", self._name, datetime.now())

        timestamp = int(time.time() * 1000)
        query_string = f"timestamp={timestamp}"
        signature = self._sign_params(query_string)
        url = f"{BINANCE_API_BASE}/api/v3/account?{query_string}&signature={signature}"

        headers = {"X-MBX-APIKEY": self._api_key}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=10) as response:
                    if response.status != 200:
                        raise Exception(f"Error response ({response.status}): {await response.text()}")
                    account_data = await response.json()
                    balances = account_data.get("balances", [])

                    # Find the balance for this asset
                    asset_balance = next(
                        (b for b in balances if b["asset"] == self._asset),
                        None,
                    )

                    if asset_balance is None:
                        logger.warning("Asset %s not found in Binance account", self._asset)
                        self._state = 0.0
                        self._data = {"free": 0.0, "locked": 0.0}
                    else:
                        free = round(float(asset_balance["free"]), self._decimals)
                        locked = round(float(asset_balance["locked"]), self._decimals)
                        self._state = free
                        self._data = {
                            "free": free,
                            "locked": locked,
                            "total": round(free + locked, self._decimals),
                        }
                        logger.debug(
                            "Wallet %s: free=%s, locked=%s",
                            self._asset,
                            free,
                            locked,
                        )
        except Exception as e:
            logger.error("Error updating wallet sensor %s - %s", self._name, e)

        await asyncio.sleep(self._update_interval)
        asyncio.create_task(self.schedule_update())
