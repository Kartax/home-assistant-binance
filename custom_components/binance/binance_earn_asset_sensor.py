"""Binance Earn Asset Sensor - combined flexible + locked Simple Earn position per asset"""

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


class BinanceEarnAssetSensor(Entity):
    """Sensor showing combined earn (flexible + locked) holdings for one asset."""

    def __init__(self, asset, api_key, api_secret, decimals, update_interval):
        self._asset = asset.upper()
        self._api_key = api_key
        self._api_secret = api_secret
        self._decimals = decimals
        self._update_interval = update_interval
        self._name = f"Binance Earn {self._asset}"
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
        return "mdi:piggy-bank-outline"

    @property
    def extra_state_attributes(self):
        return self._data

    def _sign_params(self, params: str) -> str:
        return hmac.new(
            self._api_secret.encode("utf-8"),
            params.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    async def _fetch_flexible(self, session, headers):
        rows = []
        current = 1
        size = 100
        while True:
            timestamp = int(time.time() * 1000)
            query_string = f"asset={self._asset}&current={current}&size={size}&timestamp={timestamp}"
            signature = self._sign_params(query_string)
            url = f"{BINANCE_API_BASE}/sapi/v1/simple-earn/flexible/position?{query_string}&signature={signature}"
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status != 200:
                    raise Exception(f"Flexible earn error ({response.status}): {await response.text()}")
                data = await response.json()
            page_rows = data.get("rows", [])
            rows.extend(page_rows)
            if len(rows) >= int(data.get("total", 0)) or not page_rows:
                break
            current += 1
        return rows

    async def _fetch_locked(self, session, headers):
        rows = []
        current = 1
        size = 100
        while True:
            timestamp = int(time.time() * 1000)
            query_string = f"asset={self._asset}&current={current}&size={size}&timestamp={timestamp}"
            signature = self._sign_params(query_string)
            url = f"{BINANCE_API_BASE}/sapi/v1/simple-earn/locked/position?{query_string}&signature={signature}"
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status != 200:
                    raise Exception(f"Locked earn error ({response.status}): {await response.text()}")
                data = await response.json()
            page_rows = data.get("rows", [])
            rows.extend(page_rows)
            if len(rows) >= int(data.get("total", 0)) or not page_rows:
                break
            current += 1
        return rows

    async def async_added_to_hass(self):
        logger.debug(
            "Adding earn asset sensor %s with update interval of %s seconds",
            self._name,
            self._update_interval,
        )
        await self.schedule_update()

    async def schedule_update(self):
        logger.debug("Updating earn asset sensor %s at %s", self._name, datetime.now())

        headers = {"X-MBX-APIKEY": self._api_key}

        try:
            async with aiohttp.ClientSession() as session:
                flexible_rows, locked_rows = await asyncio.gather(
                    self._fetch_flexible(session, headers),
                    self._fetch_locked(session, headers),
                )

                flexible_amount = round(
                    sum(float(r.get("totalAmount", 0)) for r in flexible_rows),
                    self._decimals,
                )
                flexible_rewards = round(
                    sum(float(r.get("cumulativeRealTimeRewards", 0)) for r in flexible_rows),
                    self._decimals,
                )
                locked_amount = round(
                    sum(float(r.get("amount", 0)) for r in locked_rows),
                    self._decimals,
                )
                locked_rewards = round(
                    sum(float(r.get("rewardAmt", 0)) for r in locked_rows),
                    self._decimals,
                )

                self._state = round(flexible_amount + locked_amount, self._decimals)
                self._data = {
                    "flexible_amount": flexible_amount,
                    "locked_amount": locked_amount,
                    "flexible_rewards": flexible_rewards,
                    "locked_rewards": locked_rewards,
                }
                logger.debug(
                    "Earn %s: flexible=%s, locked=%s",
                    self._asset,
                    flexible_amount,
                    locked_amount,
                )
        except Exception as e:
            logger.error("Error updating earn asset sensor %s - %s", self._name, e)

        await asyncio.sleep(self._update_interval)
        asyncio.create_task(self.schedule_update())
