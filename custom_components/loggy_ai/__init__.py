"""The Loggy AI integration."""
import logging
from datetime import datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, CONF_SCHEDULE_ENABLED, CONF_SCHEDULE_DAY, CONF_SCHEDULE_TIME, DAYS_OF_WEEK
from .coordinator import LoggyDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "button"]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Loggy AI component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Loggy AI from a config entry."""
    coordinator = LoggyDataUpdateCoordinator(hass, entry)
    
    await coordinator.async_config_entry_first_refresh()
    
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    if entry.data.get(CONF_SCHEDULE_ENABLED, False):
        await _setup_scheduled_analysis(hass, coordinator, entry)
    
    await _register_services(hass, coordinator)
    
    _LOGGER.info("Loggy AI integration set up successfully")
    
    return True


async def _setup_scheduled_analysis(
    hass: HomeAssistant, 
    coordinator: LoggyDataUpdateCoordinator, 
    entry: ConfigEntry
) -> None:
    """Set up scheduled log analysis."""
    schedule_day = entry.data.get(CONF_SCHEDULE_DAY, "sunday")
    schedule_time_str = entry.data.get(CONF_SCHEDULE_TIME, "22:00:00")
    
    try:
        hour, minute, second = map(int, schedule_time_str.split(":"))
        
        async def scheduled_analysis_callback(now):
            """Run scheduled analysis."""
            _LOGGER.info("Running scheduled log analysis")
            await coordinator.async_request_analysis()
        
        now = datetime.now()
        days_ahead = (DAYS_OF_WEEK.index(schedule_day.lower()) - now.weekday()) % 7
        next_run = now.replace(hour=hour, minute=minute, second=second, microsecond=0)
        if days_ahead > 0:
            next_run += timedelta(days=days_ahead)
        elif days_ahead == 0 and next_run <= now:
            next_run += timedelta(days=7)
        
        hass.helpers.event.async_track_point_in_time(
            scheduled_analysis_callback, next_run
        )
        
        _LOGGER.info(
            f"Scheduled log analysis for every {schedule_day} at {schedule_time_str}. "
            f"Next run: {next_run}"
        )
        
    except (ValueError, AttributeError) as err:
        _LOGGER.error(f"Failed to set up scheduled analysis: {err}")


async def _register_services(hass: HomeAssistant, coordinator: LoggyDataUpdateCoordinator) -> None:
    """Register Loggy AI services."""
    from .const import SERVICE_ANALYZE_LOGS
    
    async def handle_analyze_logs(call):
        """Handle the analyze_logs service call."""
        _LOGGER.info("Manual log analysis triggered via service")
        await coordinator.async_request_analysis()
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_ANALYZE_LOGS,
        handle_analyze_logs
    )


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)