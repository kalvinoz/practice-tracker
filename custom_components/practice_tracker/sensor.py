"""Sensor platform for Practice Tracker."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Practice Tracker sensors."""
    # TODO: Implement history stats sensors in next phase
    _LOGGER.info("Sensor platform loaded (placeholder - history sensors coming soon)")
    async_add_entities([])
