"""Button platform for Loggy AI integration."""
import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LoggyDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Loggy AI button from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities([LoggyAnalyzeButton(coordinator, config_entry)])


class LoggyAnalyzeButton(CoordinatorEntity, ButtonEntity):
    """Button to trigger manual log analysis."""

    _attr_icon = "mdi:play-circle"
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: LoggyDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._attr_name = "Analyze Now"
        self._attr_unique_id = f"{config_entry.entry_id}_analyze_button"

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

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.info("Analyze button pressed - triggering manual analysis")
        await self.coordinator.async_request_analysis()
