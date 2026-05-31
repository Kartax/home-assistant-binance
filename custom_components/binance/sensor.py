"""sensor"""

import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from .const import (
    CONF_SYMBOLS,
    CONF_DECIMALS,
    CONF_UPDATE_INVERVAL,
    CONF_API_KEY,
    CONF_API_SECRET,
    CONF_WALLET_ASSETS,
    CONF_WALLET_EARN_ASSETS,
)

from .binance_ticker_sensor import BinanceTickerSensor
from .binance_wallet_sensor import BinanceWalletSensor
from .binance_wallet_total_sensor import BinanceWalletTotalSensor
from .binance_earn_total_sensor import BinanceEarnTotalSensor
from .binance_earn_asset_sensor import BinanceEarnAssetSensor


logger = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_SYMBOLS): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(CONF_DECIMALS, default=8): cv.positive_int,
        vol.Optional(CONF_UPDATE_INVERVAL, default=60): cv.positive_int,
        vol.Optional(CONF_API_KEY): cv.string,
        vol.Optional(CONF_API_SECRET): cv.string,
        vol.Optional(CONF_WALLET_ASSETS): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(CONF_WALLET_EARN_ASSETS): vol.All(cv.ensure_list, [cv.string]),
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    symbols = config.get(CONF_SYMBOLS)
    decimals = config.get(CONF_DECIMALS)
    update_interval = config.get(CONF_UPDATE_INVERVAL)
    api_key = config.get(CONF_API_KEY)
    api_secret = config.get(CONF_API_SECRET)
    wallet_assets = config.get(CONF_WALLET_ASSETS, [])
    wallet_earn_assets = config.get(CONF_WALLET_EARN_ASSETS, [])

    for symbol in symbols:
        logger.debug("Setup BinanceTickerSensor %s %s %s", symbol, decimals, update_interval)
        add_entities([BinanceTickerSensor(symbol, decimals, update_interval)], True)

    if api_key and api_secret:
        logger.debug("Setup BinanceWalletTotalSensor")
        add_entities([BinanceWalletTotalSensor(api_key, api_secret, decimals, update_interval)], True)
        for asset in wallet_assets:
            logger.debug("Setup BinanceWalletSensor %s", asset)
            add_entities([BinanceWalletSensor(asset, api_key, api_secret, decimals, update_interval)], True)

        logger.debug("Setup BinanceEarnTotalSensor")
        add_entities([BinanceEarnTotalSensor(api_key, api_secret, decimals, update_interval)], True)
        for asset in wallet_earn_assets:
            logger.debug("Setup BinanceEarnAssetSensor %s", asset)
            add_entities([BinanceEarnAssetSensor(asset, api_key, api_secret, decimals, update_interval)], True)
