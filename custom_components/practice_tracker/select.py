"""Select platform for Practice Tracker."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_PLAYER_NAMES,
    CONF_TRACKER_NAME,
    DOMAIN,
    OPTION_NONE,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Practice Tracker select entity."""
    tracker_name = entry.data[CONF_TRACKER_NAME]
    player_names = entry.data[CONF_PLAYER_NAMES]

    # Create the player selection entity
    async_add_entities([PracticeTrackerPlayerSelect(entry.entry_id, tracker_name, player_names)])


class PracticeTrackerPlayerSelect(SelectEntity):
    """Representation of a Practice Tracker player selection."""

    _attr_icon = "mdi:account-music"

    def __init__(
        self,
        entry_id: str,
        tracker_name: str,
        player_names: list[str],
    ) -> None:
        """Initialize the select entity."""
        self._entry_id = entry_id
        self._tracker_name = tracker_name
        self._player_names = player_names

        # Build options: None + players (Other excluded for now)
        self._attr_options = [OPTION_NONE] + player_names
        self._attr_current_option = OPTION_NONE

        # Entity naming: tracker_name + "Current Player"
        tracker_slug = tracker_name.lower().replace(" ", "_")
        self._attr_name = f"{tracker_name} Current Player"
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_current_player"
        self.entity_id = f"select.{tracker_slug}_current_player"

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option in self._attr_options:
            self._attr_current_option = option
            self.async_write_ha_state()
            _LOGGER.debug("Player selected: %s", option)
