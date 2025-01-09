"""binance_ticker_sensor"""

import logging
from datetime import timedelta
import decimal
import aiohttp
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import STATE_UNKNOWN

logger = logging.getLogger(__name__)

class BinanceTickerSensor(Entity):

    def __init__(self, symbol, decimals, updateInterval):
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._name = "Binance Ticker " + symbol.upper()
        self._symbol = symbol
        self._decimals = decimals
        self._updateInterval = updateInterval
        self._state = STATE_UNKNOWN
        self._data = {}

    @property
    def name(self):
        return self._name

    @property
    def symbol(self):
        return self._symbol

    @property
    def decimals(self):
        return self._decimals

    @property
    def updateInterval(self):
        return self._updateInterval

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._data

    async def async_added_to_hass(self):
        self.async_on_remove(
            self.hass.helpers.event.async_track_time_interval(
                self.async_update, timedelta(seconds=self._updateInterval)
            )
        )

    async def async_update(self, *_):
        logger.debug("Updating %s", self._name)

        url = f"https://api.binance.com/api/v3/ticker?symbol={self._symbol}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status != 200:
                        raise Exception(f"Error response: {await response.text()}")
                    self._data = await response.json()
                    self._state = round(decimal.Decimal(self._data['lastPrice']), self._decimals)
        except Exception as e:
            logger.error("Error updating %s - %s", self._name, e)
