"""The Loggy AI integration."""
import json
import logging
import os
import yaml
from datetime import datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType
from homeassistant.components.persistent_notification import async_create

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
    
    # Create dashboard and send welcome notification
    await _setup_dashboard_and_welcome(hass, entry)
    
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


async def _setup_dashboard_and_welcome(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up the dashboard and send a welcome notification."""
    # Dashboard YAML is located at the repository root, which could be:
    # - For HACS: /config/custom_components/loggy/ (repository root)
    # - For manual install: /config/custom_components/loggy/
    # We look in the parent directory of the custom_components/loggy_ai integration folder
    integration_dir = os.path.dirname(__file__)  # .../custom_components/loggy_ai
    repo_root = os.path.dirname(os.path.dirname(integration_dir))  # .../
    dashboard_yaml_path = os.path.join(repo_root, "loggy_ai_dashboard.yaml")
    
    try:
        # Create the lovelace dashboard
        await _create_lovelace_dashboard(hass, dashboard_yaml_path)
        dashboard_created = True
    except Exception as err:
        _LOGGER.warning(f"Could not auto-create dashboard: {err}")
        dashboard_created = False
    
    # Send welcome notification
    await _send_welcome_notification(hass, entry, dashboard_created)


async def _create_lovelace_dashboard(hass: HomeAssistant, yaml_path: str) -> None:
    """Create a Lovelace dashboard automatically."""
    try:
        # Check if dashboard file exists
        if not os.path.exists(yaml_path):
            _LOGGER.warning(f"Dashboard template not found at: {yaml_path}")
            return
        
        # Read the dashboard YAML
        def read_yaml():
            with open(yaml_path, "r") as f:
                return yaml.safe_load(f)
        
        dashboard_config = await hass.async_add_executor_job(read_yaml)
        
        if not dashboard_config:
            _LOGGER.warning("Dashboard YAML is empty")
            return
        
        # Store dashboard configuration
        storage_path = hass.config.path(".storage")
        os.makedirs(storage_path, exist_ok=True)
        
        dashboard_storage_path = os.path.join(
            storage_path, "lovelace.loggy_ai"
        )
        
        # Create dashboard storage file
        dashboard_data = {
            "data": {
                "config": dashboard_config
            },
            "key": "lovelace.loggy_ai",
            "version": 1
        }
        
        def write_dashboard():
            with open(dashboard_storage_path, "w") as f:
                json.dump(dashboard_data, f, indent=2)
        
        await hass.async_add_executor_job(write_dashboard)
        
        _LOGGER.info("Loggy AI dashboard created successfully")
        
        # Reload lovelace to pick up the new dashboard
        try:
            await hass.services.async_call(
                "lovelace", "reload_resources", blocking=True
            )
        except Exception as reload_err:
            _LOGGER.debug(f"Could not reload lovelace resources: {reload_err}")
            
    except Exception as err:
        _LOGGER.error(f"Failed to create dashboard: {err}")
        raise


async def _send_welcome_notification(
    hass: HomeAssistant, entry: ConfigEntry, dashboard_created: bool
) -> None:
    """Send a welcome notification with setup instructions."""
    provider_name = entry.data.get("provider", "AI").title()
    
    if dashboard_created:
        message = f"""
## 🎉 Welcome to Loggy AI!

Your AI-powered log analyzer is now set up with **{provider_name}**.

### ✅ What's Ready:
- 🤖 AI-powered log analysis
- 📊 **Auto-created Dashboard** - Check your sidebar for "Loggy AI"!
- 🔔 Automated issue tracking
- 📈 Error and warning monitoring

### 🚀 Getting Started:
1. Open the **Loggy AI** dashboard from your sidebar
2. Click **"Analyze Now"** to run your first analysis
3. Review errors, warnings, and AI recommendations
4. Set up automations for notifications (optional)

### 📊 Available Sensors:
- `sensor.loggy_ai_log_analyzer_error_count`
- `sensor.loggy_ai_log_analyzer_warning_count`
- `sensor.loggy_ai_log_analyzer_new_issues_count`
- `sensor.loggy_ai_log_analyzer_analysis`

### 📚 Documentation:
[View full documentation](https://github.com/cozbox/loggy)

---

You can dismiss this notification once you've explored the dashboard.
"""
    else:
        message = f"""
## 🎉 Welcome to Loggy AI!

Your AI-powered log analyzer is now set up with **{provider_name}**.

### ✅ What's Ready:
- 🤖 AI-powered log analysis
- 🔔 Automated issue tracking
- 📈 Error and warning monitoring

### 📊 Set Up Your Dashboard:
The dashboard couldn't be created automatically, but you can easily set it up:

1. Go to **Settings** → **Dashboards** → **+ Add Dashboard**
2. Name it "Loggy AI" with icon `mdi:robot`
3. Download `loggy_ai_dashboard.yaml` from [GitHub](https://github.com/cozbox/loggy)
4. Edit the dashboard → Raw config editor → Paste the YAML
5. Save and enjoy!

### 🚀 Quick Start (Without Dashboard):
Run this service to analyze your logs immediately:
```
service: loggy_ai.analyze_logs
```

### 📊 Available Sensors:
- `sensor.loggy_ai_log_analyzer_error_count`
- `sensor.loggy_ai_log_analyzer_warning_count`
- `sensor.loggy_ai_log_analyzer_new_issues_count`
- `sensor.loggy_ai_log_analyzer_analysis`

### 📚 Documentation:
[View full documentation](https://github.com/cozbox/loggy)

---

You can dismiss this notification once you've reviewed this information.
"""
    
    await async_create(
        hass,
        message,
        title="🤖 Loggy AI - Setup Complete!",
        notification_id="loggy_ai_welcome",
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