"""sensor"""

import logging
from datetime import timedelta
import voluptuous as vol
import requests
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
from homeassistant.const import (
    CONF_ICON,
    CONF_UNIT_OF_MEASUREMENT,
    STATE_UNKNOWN,
)
from .const import (
    CONF_SYMBOL
)

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_SYMBOL): cv.string,
        vol.Optional(CONF_ICON): cv.string,
        vol.Optional(CONF_UNIT_OF_MEASUREMENT): cv.string,
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):
    symbol = config.get(CONF_SYMBOL)
    icon = config.get(CONF_ICON)
    unit = config.get(CONF_UNIT_OF_MEASUREMENT, )    
    name = "Binance "+symbol.upper()

    add_entities([KartaxBinanceSensor(name, symbol, icon, unit)], True)


class KartaxBinanceSensor(Entity):
    
    def __init__(self, name, symbol, icon, unit):
        self._name = name
        self._symbol = symbol
        self._icon = icon
        self._unit = unit
        self._state = STATE_UNKNOWN
        
    @property
    def name(self):
        return self._name

    @property
    def symbol(self):
        return self._symbol

    @property
    def icon(self):
        return self._icon

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return self._unit

    async def async_added_to_hass(self):
        self.hass.helpers.event.async_track_time_interval(
            self.update, timedelta(seconds=60)
        )

    def update(self, now=None):
        url = "https://api.binance.com/api/v3/ticker?symbol="+self._symbol
        response = requests.request("GET", url, headers={}, data={}, timeout=5)
        self._state = response.json()['lastPrice']
