"""sensor"""

import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from .const import (
    CONF_SYMBOLS,
    CONF_DECIMALS
)

from .binance_ticker_sensor import BinanceTickerSensor


logger = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_SYMBOLS): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(CONF_DECIMALS, default=8): cv.positive_int
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):
    symbols = config.get(CONF_SYMBOLS)
    decimals = config.get(CONF_DECIMALS)

    for symbol in symbols:
        logger.debug("Setup BinanceTickerSensor %s %s", symbol, decimals)
        add_entities([BinanceTickerSensor(symbol, decimals)], True)
