"""Sensor platform for Loggy AI integration."""
import logging
from datetime import datetime
from typing import Any, Optional

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    ATTR_LAST_RUN,
    ATTR_ERRORS_FOUND,
    ATTR_WARNINGS_FOUND,
    ATTR_NEW_ISSUES,
    ATTR_ANALYSIS_TEXT,
    ATTR_PROVIDER,
    ATTR_MODEL,
    CONF_PROVIDER,
    CONF_MODEL,
)
from .coordinator import LoggyDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Loggy AI sensors from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    sensors = [
        LoggyErrorSensor(coordinator, config_entry),
        LoggyWarningSensor(coordinator, config_entry),
        LoggyNewIssuesSensor(coordinator, config_entry),
        LoggyAnalysisSensor(coordinator, config_entry),
    ]

    async_add_entities(sensors)


class LoggyBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for Loggy AI sensors."""

    def __init__(
        self,
        coordinator: LoggyDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._attr_has_entity_name = True

    @property
    def device_info(self):
        """Return device information about this entity."""
        return {
            "identifiers": {(DOMAIN, self.config_entry.entry_id)},
            "name": "Loggy AI Log Analyzer",
            "manufacturer": "Loggy AI",
            "model": "Log Analyzer",
            "sw_version": "1.0.0",
        }


class LoggyErrorSensor(LoggyBaseSensor):
    """Sensor for error count."""

    _attr_icon = "mdi:alert-circle"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: LoggyDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the error count sensor."""
        super().__init__(coordinator, config_entry)
        self._attr_name = "Error Count"
        self._attr_unique_id = f"{config_entry.entry_id}_error_count"

    @property
    def native_value(self) -> int:
        """Return the error count."""
        if self.coordinator.data:
            return self.coordinator.data.get("error_count", 0)
        return 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return {}

        return {
            ATTR_LAST_RUN: self.coordinator.data.get("last_run"),
            ATTR_PROVIDER: self.config_entry.data.get(CONF_PROVIDER, "gemini"),
            ATTR_MODEL: self.config_entry.data.get(CONF_MODEL, ""),
        }


class LoggyWarningSensor(LoggyBaseSensor):
    """Sensor for warning count."""

    _attr_icon = "mdi:alert"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: LoggyDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the warning count sensor."""
        super().__init__(coordinator, config_entry)
        self._attr_name = "Warning Count"
        self._attr_unique_id = f"{config_entry.entry_id}_warning_count"

    @property
    def native_value(self) -> int:
        """Return the warning count."""
        if self.coordinator.data:
            return self.coordinator.data.get("warning_count", 0)
        return 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return {}

        return {
            ATTR_LAST_RUN: self.coordinator.data.get("last_run"),
            ATTR_PROVIDER: self.config_entry.data.get(CONF_PROVIDER, "gemini"),
            ATTR_MODEL: self.config_entry.data.get(CONF_MODEL, ""),
        }


class LoggyNewIssuesSensor(LoggyBaseSensor):
    """Sensor for new issues count."""

    _attr_icon = "mdi:new-box"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: LoggyDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the new issues count sensor."""
        super().__init__(coordinator, config_entry)
        self._attr_name = "New Issues Count"
        self._attr_unique_id = f"{config_entry.entry_id}_new_issues_count"

    @property
    def native_value(self) -> int:
        """Return the new issues count."""
        if self.coordinator.data:
            return self.coordinator.data.get("new_issues_count", 0)
        return 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return {}

        return {
            ATTR_LAST_RUN: self.coordinator.data.get("last_run"),
            ATTR_PROVIDER: self.config_entry.data.get(CONF_PROVIDER, "gemini"),
            ATTR_MODEL: self.config_entry.data.get(CONF_MODEL, ""),
        }


class LoggyAnalysisSensor(LoggyBaseSensor):
    """Sensor for full analysis text."""

    _attr_icon = "mdi:text-box-search"

    def __init__(
        self,
        coordinator: LoggyDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the analysis text sensor."""
        super().__init__(coordinator, config_entry)
        self._attr_name = "Analysis"
        self._attr_unique_id = f"{config_entry.entry_id}_analysis"

    @property
    def native_value(self) -> str:
        """Return the analysis summary."""
        if self.coordinator.data:
            analysis = self.coordinator.data.get("analysis_text", "")
            # Return first 255 chars for state, full text in attributes
            return analysis[:255] if analysis else "No analysis available"
        return "No analysis available"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return {}

        return {
            ATTR_LAST_RUN: self.coordinator.data.get("last_run"),
            ATTR_ERRORS_FOUND: self.coordinator.data.get("error_count", 0),
            ATTR_WARNINGS_FOUND: self.coordinator.data.get("warning_count", 0),
            ATTR_NEW_ISSUES: self.coordinator.data.get("new_issues_count", 0),
            ATTR_ANALYSIS_TEXT: self.coordinator.data.get("analysis_text", ""),
            ATTR_PROVIDER: self.config_entry.data.get(CONF_PROVIDER, "gemini"),
            ATTR_MODEL: self.config_entry.data.get(CONF_MODEL, ""),
        }
