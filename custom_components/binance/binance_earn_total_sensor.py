"""Binance Earn Total Sensor - combined Simple Earn (flexible + locked) value in USD"""

import json
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


class BinanceEarnTotalSensor(Entity):
    """Sensor showing estimated total Simple Earn value in USD (flexible + locked)."""

    def __init__(self, api_key, api_secret, decimals, update_interval):
        self._api_key = api_key
        self._api_secret = api_secret
        self._decimals = decimals
        self._update_interval = update_interval
        self._name = "Binance Earn Total (USD)"
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
        return "mdi:piggy-bank"

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

    async def _fetch_all_flexible(self, session, headers):
        rows = []
        current = 1
        size = 100
        while True:
            timestamp = int(time.time() * 1000)
            query_string = f"current={current}&size={size}&timestamp={timestamp}"
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

    async def _fetch_all_locked(self, session, headers):
        rows = []
        current = 1
        size = 100
        while True:
            timestamp = int(time.time() * 1000)
            query_string = f"current={current}&size={size}&timestamp={timestamp}"
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
            "Adding earn total sensor %s with update interval of %s seconds",
            self._name,
            self._update_interval,
        )
        await self.schedule_update()

    async def schedule_update(self):
        logger.debug("Updating earn total sensor %s at %s", self._name, datetime.now())

        headers = {"X-MBX-APIKEY": self._api_key}

        try:
            async with aiohttp.ClientSession() as session:
                flexible_rows, locked_rows = await asyncio.gather(
                    self._fetch_all_flexible(session, headers),
                    self._fetch_all_locked(session, headers),
                )

                flexible_by_asset: dict[str, float] = {}
                for r in flexible_rows:
                    asset = r.get("asset", "")
                    flexible_by_asset[asset] = flexible_by_asset.get(asset, 0.0) + float(r.get("totalAmount", 0))

                locked_by_asset: dict[str, float] = {}
                for r in locked_rows:
                    asset = r.get("asset", "")
                    locked_by_asset[asset] = locked_by_asset.get(asset, 0.0) + float(r.get("amount", 0))

                all_assets = set(flexible_by_asset) | set(locked_by_asset)

                if not all_assets:
                    self._state = 0.0
                    self._data = {
                        "flexible_total_usd": 0.0,
                        "locked_total_usd": 0.0,
                        "asset_breakdown": {},
                    }
                    await asyncio.sleep(self._update_interval)
                    asyncio.create_task(self.schedule_update())
                    return

                # Build price map: stable USD assets default to 1.0, rest fetched from API
                USD_STABLE = {"USDT", "BUSD", "FDUSD", "TUSD", "USDC"}
                prices = {a: 1.0 for a in all_assets if a in USD_STABLE}
                non_stable = [a for a in all_assets if a not in USD_STABLE]

                if non_stable:
                    symbols_param = json.dumps([f"{a}USDT" for a in non_stable], separators=(",", ":"))
                    async with session.get(
                        f"{BINANCE_API_BASE}/api/v3/ticker/price",
                        params={"symbols": symbols_param},
                        timeout=10,
                    ) as pr:
                        if pr.status != 200:
                            raise Exception(f"Price fetch error ({pr.status}): {await pr.text()}")
                        price_data = await pr.json()
                    for item in price_data:
                        sym = item["symbol"]
                        if sym.endswith("USDT"):
                            prices[sym[:-4]] = float(item["price"])

                asset_breakdown = {}
                flexible_total_usd = 0.0
                locked_total_usd = 0.0

                for asset in sorted(all_assets):
                    price = prices.get(asset, 0.0)
                    if price == 0.0:
                        logger.warning("No USDT price found for earn asset %s, skipping", asset)
                    flex = flexible_by_asset.get(asset, 0.0)
                    lock = locked_by_asset.get(asset, 0.0)
                    flex_usd = round(flex * price, 2)
                    lock_usd = round(lock * price, 2)
                    flexible_total_usd += flex_usd
                    locked_total_usd += lock_usd
                    asset_breakdown[asset] = {
                        "flexible": round(flex, self._decimals),
                        "locked": round(lock, self._decimals),
                        "total_usd": round(flex_usd + lock_usd, 2),
                    }

                total_usd = round(flexible_total_usd + locked_total_usd, 2)

                self._state = total_usd
                self._data = {
                    "flexible_total_usd": round(flexible_total_usd, 2),
                    "locked_total_usd": round(locked_total_usd, 2),
                    "asset_breakdown": asset_breakdown,
                }
                logger.debug(
                    "Earn total: flexible=%.2f USD, locked=%.2f USD, total=%.2f USD",
                    flexible_total_usd,
                    locked_total_usd,
                    total_usd,
                )
        except Exception as e:
            logger.error("Error updating earn total sensor %s - %s", self._name, e, exc_info=True)

        await asyncio.sleep(self._update_interval)
        asyncio.create_task(self.schedule_update())
