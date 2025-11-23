"""The Loggy AI integration."""
import json
import logging
import os
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

# Embedded dashboard configuration
DASHBOARD_CONFIG = {
    "title": "Loggy AI",
    "icon": "mdi:robot",
    "path": "loggy-ai",
    "views": [
        {
            "title": "Log Analysis",
            "icon": "mdi:text-box-search",
            "badges": [],
            "cards": [
                # Main Loggy AI Card
                {
                    "type": "custom:loggy-card",
                    "entity": "sensor.loggy_ai_log_analyzer_analysis"
                },
                # Entity cards for quick access
                {
                    "type": "entities",
                    "title": "Quick Actions",
                    "show_header_toggle": False,
                    "entities": [
                        {
                            "entity": "button.loggy_ai_log_analyzer_analyze_now",
                            "name": "Analyze Logs Now",
                            "icon": "mdi:play-circle"
                        }
                    ]
                },
                # Statistics Grid
                {
                    "type": "grid",
                    "columns": 3,
                    "square": False,
                    "cards": [
                        {
                            "type": "statistic",
                            "entity": "sensor.loggy_ai_log_analyzer_error_count",
                            "name": "Errors",
                            "icon": "mdi:alert-circle",
                            "period": {
                                "calendar": {
                                    "period": "day"
                                }
                            }
                        },
                        {
                            "type": "statistic",
                            "entity": "sensor.loggy_ai_log_analyzer_warning_count",
                            "name": "Warnings",
                            "icon": "mdi:alert",
                            "period": {
                                "calendar": {
                                    "period": "day"
                                }
                            }
                        },
                        {
                            "type": "statistic",
                            "entity": "sensor.loggy_ai_log_analyzer_new_issues_count",
                            "name": "New Issues",
                            "icon": "mdi:new-box",
                            "period": {
                                "calendar": {
                                    "period": "day"
                                }
                            }
                        }
                    ]
                },
                # History Graph
                {
                    "type": "history-graph",
                    "title": "Error & Warning Trends",
                    "hours_to_show": 168,
                    "entities": [
                        {
                            "entity": "sensor.loggy_ai_log_analyzer_error_count",
                            "name": "Errors"
                        },
                        {
                            "entity": "sensor.loggy_ai_log_analyzer_warning_count",
                            "name": "Warnings"
                        },
                        {
                            "entity": "sensor.loggy_ai_log_analyzer_new_issues_count",
                            "name": "New Issues"
                        }
                    ]
                },
                # Full Analysis Text
                {
                    "type": "markdown",
                    "title": "Latest Analysis Details",
                    "content": (
                        "{% set last_run = state_attr('sensor.loggy_ai_log_analyzer_analysis', 'last_run') %}\n"
                        "{% set provider = state_attr('sensor.loggy_ai_log_analyzer_analysis', 'provider') %}\n"
                        "{% set model = state_attr('sensor.loggy_ai_log_analyzer_analysis', 'model') %}\n"
                        "{% set analysis = state_attr('sensor.loggy_ai_log_analyzer_analysis', 'analysis_text') %}\n"
                        "{% if states('sensor.loggy_ai_log_analyzer_analysis') != 'unknown' %}\n"
                        "**Last Run:** {{ last_run | default('Never') }}\n"
                        "\n"
                        "**Provider:** {{ provider | default('N/A') }}\n"
                        "**Model:** {{ model | default('N/A') }}\n"
                        "\n"
                        "---\n"
                        "\n"
                        "{{ analysis | default('No analysis available yet. Click \"Analyze Now\" to run your first analysis.') }}\n"
                        "{% else %}\n"
                        "Integration not found. Please ensure Loggy AI is installed and configured.\n"
                        "{% endif %}"
                    )
                }
            ]
        }
    ]
}



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
    dashboard_created = False
    
    # Try to create dashboard from embedded config
    try:
        await _create_lovelace_dashboard(hass)
        dashboard_created = True
        _LOGGER.info("Created dashboard in storage (accessible from UI)")
    except Exception as err:
        _LOGGER.warning(f"Could not auto-create dashboard in storage: {err}")
    
    # Register frontend panel for sidebar visibility
    try:
        await _register_frontend_panel(hass)
        _LOGGER.info("Registered Loggy AI panel in sidebar")
    except Exception as err:
        _LOGGER.warning(f"Could not register frontend panel: {err}")
    
    # Send welcome notification
    await _send_welcome_notification(hass, entry, dashboard_created)


async def _register_frontend_panel(hass: HomeAssistant) -> None:
    """Register Loggy AI dashboard as a frontend panel for sidebar visibility."""
    try:
        # Register the panel using the lovelace dashboard
        hass.components.frontend.async_register_built_in_panel(
            "lovelace",
            "Loggy AI",
            "mdi:robot",
            "loggy_ai",
            {"mode": "storage"},
            require_admin=False,
        )
        _LOGGER.info("Loggy AI panel registered in sidebar")
    except Exception as err:
        _LOGGER.error(f"Failed to register frontend panel: {err}")
        raise


async def _create_lovelace_dashboard(hass: HomeAssistant) -> None:
    """Create a Lovelace dashboard automatically from embedded config."""
    try:
        # Use embedded dashboard configuration
        dashboard_config = DASHBOARD_CONFIG
        
        if not dashboard_config:
            _LOGGER.warning("Dashboard config is empty")
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
        # Dashboard was created successfully
        message = f"""
## 🎉 Welcome to Loggy AI!

Your AI-powered log analyzer is now set up with **{provider_name}**.

### ✅ What's Ready:
- 🤖 AI-powered log analysis with auto-detect log file path
- 📊 **Dashboard available in sidebar** - Look for "Loggy AI" in your Home Assistant sidebar!
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
- 🤖 AI-powered log analysis with auto-detect log file path
- 🔔 Automated issue tracking
- 📈 Error and warning monitoring

### 📊 Dashboard Setup:
The dashboard could not be auto-created. You can manually set it up:

**Option 1: UI Dashboard (Recommended)**
1. Go to **Settings** → **Dashboards** → **+ Add Dashboard**
2. Name it "Loggy AI" with icon `mdi:robot`
3. Edit dashboard → Raw config editor
4. Copy contents from `loggy_ai_dashboard.yaml`
5. Save and enjoy!

**Option 2: Lovelace YAML Mode**
1. Copy view from `ui-lovelace-loggy-example.yaml`
2. Add to your `ui-lovelace.yaml` file
3. Restart Home Assistant

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