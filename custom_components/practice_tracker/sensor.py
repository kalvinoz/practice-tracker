"""Sensor platform for Practice Tracker."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util
from homeassistant.components.recorder import history

from .const import (
    CONF_PLAYER_NAMES,
    CONF_TRACKER_NAME,
    DOMAIN,
    PERIOD_TODAY,
    PERIOD_YESTERDAY,
    PERIOD_7_DAYS,
    PERIOD_28_DAYS,
    DEFAULT_PERIODS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Practice Tracker sensors."""
    tracker_name = entry.data[CONF_TRACKER_NAME]
    player_names = entry.data[CONF_PLAYER_NAMES]

    # Create history stats sensors for each player and period
    sensors = []

    # Build the select entity ID that we'll track
    tracker_slug = tracker_name.lower().replace(" ", "_")
    select_entity_id = f"select.{tracker_slug}_current_player"

    for player_name in player_names:
        for period in DEFAULT_PERIODS:
            sensors.append(
                PracticeHistorySensor(
                    entry.entry_id,
                    tracker_name,
                    tracker_slug,
                    player_name,
                    period,
                    select_entity_id,
                )
            )

    # Create total sensors for each period (sum of all players)
    for period in DEFAULT_PERIODS:
        sensors.append(
            PracticeTotalSensor(
                entry.entry_id,
                tracker_name,
                tracker_slug,
                player_names,
                period,
            )
        )

    _LOGGER.info(
        "Created %d sensors for %s (%d history + %d totals)",
        len(sensors),
        tracker_name,
        len(player_names) * len(DEFAULT_PERIODS),
        len(DEFAULT_PERIODS),
    )

    async_add_entities(sensors)


class PracticeHistorySensor(SensorEntity):
    """Representation of a Practice Tracker history sensor."""

    _attr_device_class = SensorDeviceClass.DURATION
    _attr_state_class = SensorStateClass.TOTAL
    _attr_native_unit_of_measurement = "h"
    _attr_icon = "mdi:clock-time-eight"

    def __init__(
        self,
        entry_id: str,
        tracker_name: str,
        tracker_slug: str,
        player_name: str,
        period: str,
        select_entity_id: str,
    ) -> None:
        """Initialize the sensor."""
        self._entry_id = entry_id
        self._tracker_name = tracker_name
        self._tracker_slug = tracker_slug
        self._player_name = player_name
        self._period = period
        self._select_entity_id = select_entity_id
        self._state: float | None = None

        # Generate entity naming
        player_slug = player_name.lower().replace(" ", "_")
        period_slug = period.replace("_", "_")

        self._attr_name = f"{tracker_name} {player_name} {self._period_display_name()}"
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_sensor_{player_slug}_{period}"
        self.entity_id = f"sensor.{tracker_slug}_{player_slug}_{period}"

        # State attributes
        self._attr_extra_state_attributes = {
            "player": player_name,
            "period": period,
            "source_entity": select_entity_id,
        }

    def _period_display_name(self) -> str:
        """Return human-readable period name."""
        return {
            PERIOD_TODAY: "Today",
            PERIOD_YESTERDAY: "Yesterday",
            PERIOD_7_DAYS: "7 Days",
            PERIOD_28_DAYS: "28 Days",
        }.get(self._period, self._period)

    def _get_period_start_end(self) -> tuple[datetime, datetime]:
        """Calculate start and end times for the period."""
        now = dt_util.now()

        if self._period == PERIOD_TODAY:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now

        elif self._period == PERIOD_YESTERDAY:
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            start = today_start - timedelta(days=1)
            end = today_start

        elif self._period == PERIOD_7_DAYS:
            start = now - timedelta(days=7)
            end = now

        elif self._period == PERIOD_28_DAYS:
            start = now - timedelta(days=28)
            end = now

        else:
            # Default to today
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now

        return start, end

    def _calculate_history(self, start: datetime, end: datetime) -> float:
        """Calculate practice time from history (runs in executor)."""
        if not self.hass:
            return 0.0

        # Query history for the select entity (this is the blocking call)
        history_list = history.state_changes_during_period(
            self.hass,
            start,
            end,
            self._select_entity_id,
        )

        if not history_list or self._select_entity_id not in history_list:
            return 0.0

        # Calculate total time when select entity was set to this player
        total_seconds = 0
        states = history_list[self._select_entity_id]

        for i, state in enumerate(states):
            # Only count time when state matches our player name
            if state.state != self._player_name:
                continue

            # Get the start time of this state
            state_start = state.last_changed

            # Get the end time (either next state change or end of period)
            if i + 1 < len(states):
                state_end = states[i + 1].last_changed
            else:
                state_end = end

            # Don't count time before period start
            if state_start < start:
                state_start = start

            # Don't count time after period end
            if state_end > end:
                state_end = end

            # Add duration to total
            duration = (state_end - state_start).total_seconds()
            total_seconds += duration

        # Convert to hours and round to 2 decimal places
        hours = round(total_seconds / 3600, 2)

        return hours

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self._state

    @property
    def available(self) -> bool:
        """Return if sensor is available."""
        # Check if source select entity exists
        if not self.hass:
            return False

        select_state = self.hass.states.get(self._select_entity_id)
        return select_state is not None

    async def async_update(self) -> None:
        """Update the sensor."""
        if not self.hass:
            self._state = None
            return

        # Check if the select entity exists
        select_state = self.hass.states.get(self._select_entity_id)
        if not select_state:
            _LOGGER.warning(
                "Select entity %s not found for sensor %s",
                self._select_entity_id,
                self.entity_id,
            )
            self._state = None
            return

        # Get period boundaries
        start, end = self._get_period_start_end()

        # Run the blocking history query in an executor
        self._state = await self.hass.async_add_executor_job(
            self._calculate_history, start, end
        )


class PracticeTotalSensor(SensorEntity):
    """Representation of a Practice Tracker total sensor (sum of all players)."""

    _attr_device_class = SensorDeviceClass.DURATION
    _attr_state_class = SensorStateClass.TOTAL
    _attr_native_unit_of_measurement = "h"
    _attr_icon = "mdi:sigma"

    def __init__(
        self,
        entry_id: str,
        tracker_name: str,
        tracker_slug: str,
        player_names: list[str],
        period: str,
    ) -> None:
        """Initialize the sensor."""
        self._entry_id = entry_id
        self._tracker_name = tracker_name
        self._tracker_slug = tracker_slug
        self._player_names = player_names
        self._period = period

        # Generate entity naming
        self._attr_name = f"{tracker_name} Total {self._period_display_name()}"
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_total_{period}"
        self.entity_id = f"sensor.{tracker_slug}_total_{period}"

        # State attributes
        self._attr_extra_state_attributes = {
            "period": period,
            "player_count": len(player_names),
        }

    def _period_display_name(self) -> str:
        """Return human-readable period name."""
        return {
            PERIOD_TODAY: "Today",
            PERIOD_YESTERDAY: "Yesterday",
            PERIOD_7_DAYS: "7 Days",
            PERIOD_28_DAYS: "28 Days",
        }.get(self._period, self._period)

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor (sum of all player sensors)."""
        if not self.hass:
            return None

        total = 0.0

        # Sum all player sensors for this period
        for player_name in self._player_names:
            player_slug = player_name.lower().replace(" ", "_")
            sensor_id = f"sensor.{self._tracker_slug}_{player_slug}_{self._period}"

            state = self.hass.states.get(sensor_id)
            if state and state.state not in ["unavailable", "unknown", "none"]:
                try:
                    total += float(state.state)
                except (ValueError, TypeError):
                    _LOGGER.warning(
                        "Invalid state for %s: %s", sensor_id, state.state
                    )

        # Round to 2 decimal places
        return round(total, 2)

    @property
    def available(self) -> bool:
        """Return if sensor is available."""
        if not self.hass:
            return False

        # Check if at least one player sensor is available
        for player_name in self._player_names:
            player_slug = player_name.lower().replace(" ", "_")
            sensor_id = f"sensor.{self._tracker_slug}_{player_slug}_{self._period}"

            state = self.hass.states.get(sensor_id)
            if state and state.state not in ["unavailable", "unknown"]:
                return True

        return False

    async def async_update(self) -> None:
        """Update the sensor."""
        # The native_value property calculates on-demand
        pass
