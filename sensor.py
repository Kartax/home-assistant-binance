"""sensor"""

import logging
from datetime import timedelta
import voluptuous as vol
import requests
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
from homeassistant.const import (
    STATE_UNKNOWN, DEVICE_CLASS_MONETARY
)
from .const import (
    CONF_SYMBOLS
)

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_SYMBOLS): vol.All(cv.ensure_list, [cv.string])
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):
    symbols = config.get(CONF_SYMBOLS)

    for symbol in symbols:
        add_entities([KartaxBinanceSensor(symbol)], True)

class KartaxBinanceSensor(Entity):

    def __init__(self, symbol):
        self._attr_device_class = DEVICE_CLASS_MONETARY
        self._name = "Binance "+symbol.upper()
        self._symbol = symbol
        self._state = STATE_UNKNOWN
        self._data = {}

    @property
    def name(self):
        return self._name

    @property
    def symbol(self):
        return self._symbol

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._data

    async def async_added_to_hass(self):
        self.hass.helpers.event.async_track_time_interval(
            self.update, timedelta(seconds=60)
        )

    def update(self):
        url = "https://api.binance.com/api/v3/ticker?symbol="+self._symbol
        response = requests.request("GET", url, headers={}, data={}, timeout=5)
        self._data = response.json()
        self._state = self._data['lastPrice']
