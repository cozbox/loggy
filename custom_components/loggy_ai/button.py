from homeassistant.components.button import ButtonEntity
import logging

_LOGGER = logging.getLogger(__name__)

class LoggyButton(ButtonEntity):
    """Class to represent a manual trigger button for Loggy."""
    def __init__(self, api_client):
        self.api_client = api_client

    async def async_press(self):
        """Trigger the manual analysis via the API."""
        await self.api_client.trigger_analysis()
        _LOGGER.info("Manual log analysis triggered.")
