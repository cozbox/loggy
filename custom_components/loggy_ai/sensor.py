from homeassistant.helpers.entity import Entity
import logging

_LOGGER = logging.getLogger(__name__)

class LoggySensor(Entity):
    """Class to represent a Loggy sensor."""
    def __init__(self, name, api_client):
        self._name = name
        self.api_client = api_client
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    async def async_update(self):
        """Retrieve the latest data from the API."""
        self._state = await self.api_client.get_data(self._name)
