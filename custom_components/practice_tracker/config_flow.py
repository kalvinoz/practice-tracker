"""Config flow for Practice Tracker integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_NUM_PLAYERS,
    CONF_PLAYER_NAMES,
    CONF_TRACKER_NAME,
    CONF_TRIGGER_ENTITY,
    DEFAULT_NAME,
    DEFAULT_NUM_PLAYERS,
    DOMAIN,
    MAX_PLAYERS,
    MIN_PLAYERS,
)

_LOGGER = logging.getLogger(__name__)


class PracticeTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Practice Tracker."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self.config_data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - basic tracker info."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Store basic info
            self.config_data[CONF_TRACKER_NAME] = user_input[CONF_TRACKER_NAME]
            self.config_data[CONF_NUM_PLAYERS] = user_input[CONF_NUM_PLAYERS]

            # Set unique ID based on tracker name
            await self.async_set_unique_id(user_input[CONF_TRACKER_NAME].lower().replace(" ", "_"))
            self._abort_if_unique_id_configured()

            # Move to player names step
            return await self.async_step_players()

        # Show form
        data_schema = vol.Schema(
            {
                vol.Required(CONF_TRACKER_NAME, default=DEFAULT_NAME): str,
                vol.Required(CONF_NUM_PLAYERS, default=DEFAULT_NUM_PLAYERS): vol.All(
                    vol.Coerce(int), vol.Range(min=MIN_PLAYERS, max=MAX_PLAYERS)
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_players(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle player names configuration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Extract player names
            player_names = []
            num_players = self.config_data[CONF_NUM_PLAYERS]

            for i in range(num_players):
                name = user_input.get(f"player_{i}")
                if name:
                    player_names.append(name.strip())

            # Validate no duplicates
            if len(player_names) != len(set(player_names)):
                errors["base"] = "duplicate_names"
            else:
                self.config_data[CONF_PLAYER_NAMES] = player_names
                return await self.async_step_trigger()

        # Build dynamic schema based on number of players
        num_players = self.config_data[CONF_NUM_PLAYERS]
        schema_dict = {}

        for i in range(num_players):
            schema_dict[vol.Required(f"player_{i}", default=f"Player {i+1}")] = str

        return self.async_show_form(
            step_id="players",
            data_schema=vol.Schema(schema_dict),
            errors=errors,
            description_placeholders={"num_players": str(num_players)},
        )

    async def async_step_trigger(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle trigger configuration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Store trigger entity
            self.config_data[CONF_TRIGGER_ENTITY] = user_input[CONF_TRIGGER_ENTITY]

            # Create the entry
            return self.async_create_entry(
                title=self.config_data[CONF_TRACKER_NAME],
                data=self.config_data,
            )

        # Show form with binary sensor selector
        data_schema = vol.Schema(
            {
                vol.Required(CONF_TRIGGER_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="binary_sensor")
                ),
            }
        )

        return self.async_show_form(
            step_id="trigger",
            data_schema=data_schema,
            errors=errors,
        )
