"""binance_ticker_sensor"""

import logging
from datetime import timedelta
import decimal
import requests
from requests import RequestException
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import (
    STATE_UNKNOWN
)


logger = logging.getLogger(__name__)


class BinanceTickerSensor(Entity):

    def __init__(self, symbol, decimals, updateInterval):
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._name = "Binance Ticker "+symbol.upper()
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
        self.hass.helpers.event.async_track_time_interval(
            self.update, timedelta(seconds=self._updateInterval)
        )

    def update(self, *args):
        logger.debug("Updating %s - args", self._name, args)
        
        url = "https://api.binance.com/api/v3/ticker?symbol="+self._symbol
        
        try:
            response = requests.request("GET", url, headers={}, data={}, timeout=5)
            
            if response.status_code != 200:
                raise RequestException(response.json())
            
            self._data = response.json()
            self._state = round(decimal.Decimal(self._data['lastPrice']), self._decimals)
            
        except RequestException as request_exception:
            logger.error("Error updating %s - %s", self._name, request_exception)
        
