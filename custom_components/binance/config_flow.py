"""Config flow for Binance integration."""

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

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


class BinanceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Binance."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Step 1: credentials and basic setup."""
        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="Binance", data=user_input)

        schema = vol.Schema(
            {
                vol.Optional(CONF_API_KEY, default=""): str,
                vol.Optional(CONF_API_SECRET, default=""): str,
                vol.Optional(CONF_DECIMALS, default=8): int,
                vol.Optional(CONF_UPDATE_INVERVAL, default=60): int,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_import(self, import_data):
        """Handle import from YAML configuration."""
        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        symbols = import_data.get(CONF_SYMBOLS, [])
        symbols_str = ",".join(symbols) if isinstance(symbols, list) else symbols

        wallet_assets = import_data.get(CONF_WALLET_ASSETS, [])
        wallet_assets_str = ",".join(wallet_assets) if isinstance(wallet_assets, list) else (wallet_assets or "")

        wallet_earn_assets = import_data.get(CONF_WALLET_EARN_ASSETS, [])
        wallet_earn_assets_str = (
            ",".join(wallet_earn_assets) if isinstance(wallet_earn_assets, list) else (wallet_earn_assets or "")
        )

        entry_data = {
            CONF_API_KEY: import_data.get(CONF_API_KEY, ""),
            CONF_API_SECRET: import_data.get(CONF_API_SECRET, ""),
            CONF_DECIMALS: import_data.get(CONF_DECIMALS, 8),
            CONF_UPDATE_INVERVAL: import_data.get(CONF_UPDATE_INVERVAL, 60),
        }

        entry_options = {
            CONF_SYMBOLS: symbols_str,
            CONF_WALLET_ASSETS: wallet_assets_str,
            CONF_WALLET_EARN_ASSETS: wallet_earn_assets_str,
        }

        return self.async_create_entry(title="Binance", data=entry_data, options=entry_options)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler()


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for Binance."""

    async def async_step_init(self, user_input=None):
        """Manage symbols and asset lists."""

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_options = self.config_entry.options

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SYMBOLS,
                    default=current_options.get(CONF_SYMBOLS, ""),
                ): str,
                vol.Optional(
                    CONF_WALLET_ASSETS,
                    default=current_options.get(CONF_WALLET_ASSETS, ""),
                ): str,
                vol.Optional(
                    CONF_WALLET_EARN_ASSETS,
                    default=current_options.get(CONF_WALLET_EARN_ASSETS, ""),
                ): str,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )
