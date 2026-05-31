"""Binance Integration for Home Assistant"""

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import (
    CONF_API_KEY,
    CONF_API_SECRET,
    CONF_DECIMALS,
    CONF_SYMBOLS,
    CONF_UPDATE_INVERVAL,
    CONF_WALLET_ASSETS,
    CONF_WALLET_EARN_ASSETS,
    DOMAIN,
)

PLATFORMS = [Platform.SENSOR]

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.All(
            cv.ensure_list,
            [
                vol.Schema(
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
            ],
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Trigger import flow for existing YAML configs."""
    if DOMAIN not in config:
        return True
    for entry_config in config[DOMAIN]:
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": "import"},
                data=entry_config,
            )
        )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
