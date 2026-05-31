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
    CONF_WALLET_TOTAL,
    CONF_FUNDING_ASSETS,
    CONF_EARN_FLEXIBLE_ASSETS,
    CONF_EARN_LOCKED_ASSETS,
)

from .binance_ticker_sensor import BinanceTickerSensor
from .binance_wallet_sensor import BinanceWalletSensor
from .binance_wallet_total_sensor import BinanceWalletTotalSensor
from .binance_funding_sensor import BinanceFundingSensor
from .binance_earn_flexible_sensor import BinanceEarnFlexibleSensor
from .binance_earn_locked_sensor import BinanceEarnLockedSensor


logger = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_SYMBOLS): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(CONF_DECIMALS, default=8): cv.positive_int,
        vol.Optional(CONF_UPDATE_INVERVAL, default=60): cv.positive_int,
        vol.Optional(CONF_API_KEY): cv.string,
        vol.Optional(CONF_API_SECRET): cv.string,
        vol.Optional("wallet_assets"): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(CONF_WALLET_TOTAL, default=False): cv.boolean,
        vol.Optional(CONF_FUNDING_ASSETS): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(CONF_EARN_FLEXIBLE_ASSETS): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(CONF_EARN_LOCKED_ASSETS): vol.All(cv.ensure_list, [cv.string]),
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):
    symbols = config.get(CONF_SYMBOLS)
    decimals = config.get(CONF_DECIMALS)
    updateInterval = config.get(CONF_UPDATE_INVERVAL)
    api_key = config.get(CONF_API_KEY)
    api_secret = config.get(CONF_API_SECRET)
    wallet_assets = config.get("wallet_assets", [])
    wallet_total = config.get(CONF_WALLET_TOTAL, False)
    funding_assets = config.get(CONF_FUNDING_ASSETS, [])
    earn_flexible_assets = config.get(CONF_EARN_FLEXIBLE_ASSETS, [])
    earn_locked_assets = config.get(CONF_EARN_LOCKED_ASSETS, [])

    # Ticker sensors (always created)
    for symbol in symbols:
        logger.debug("Setup BinanceTickerSensor %s %s %s", symbol, decimals, updateInterval)
        add_entities([BinanceTickerSensor(symbol, decimals, updateInterval)], True)

    # Wallet sensors (only if api_key and api_secret are provided)
    if api_key and api_secret:
        if not wallet_assets:
            logger.warning(
                "Binance API key and secret provided, but no 'wallet_assets' configured. "
                "Add a 'wallet_assets' list to track your balances."
            )
        for asset in wallet_assets:
            logger.debug("Setup BinanceWalletSensor %s", asset)
            add_entities([BinanceWalletSensor(asset, api_key, api_secret, decimals, updateInterval)], True)
        if wallet_total:
            logger.debug("Setup BinanceWalletTotalSensor")
            add_entities([BinanceWalletTotalSensor(api_key, api_secret, decimals, updateInterval)], True)
        for asset in funding_assets:
            logger.debug("Setup BinanceFundingSensor %s", asset)
            add_entities([BinanceFundingSensor(asset, api_key, api_secret, decimals, updateInterval)], True)
        for asset in earn_flexible_assets:
            logger.debug("Setup BinanceEarnFlexibleSensor %s", asset)
            add_entities([BinanceEarnFlexibleSensor(asset, api_key, api_secret, decimals, updateInterval)], True)
        for asset in earn_locked_assets:
            logger.debug("Setup BinanceEarnLockedSensor %s", asset)
            add_entities([BinanceEarnLockedSensor(asset, api_key, api_secret, decimals, updateInterval)], True)
    elif wallet_assets:
        logger.warning(
            "Binance 'wallet_assets' configured but 'api_key' and/or 'api_secret' are missing. "
            "Wallet sensors will not be created."
        )
