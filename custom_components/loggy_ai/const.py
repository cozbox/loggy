"""Constants for the Loggy AI integration."""
from datetime import timedelta

DOMAIN = "loggy_ai"
CONF_API_KEY = "api_key"
CONF_PROVIDER = "provider"
CONF_MODEL = "model"
CONF_DAYS_TO_REVIEW = "days_to_review"
CONF_SCHEDULE_ENABLED = "schedule_enabled"
CONF_SCHEDULE_DAY = "schedule_day"
CONF_SCHEDULE_TIME = "schedule_time"
CONF_THINKING_LEVEL = "thinking_level"
CONF_LOG_PATH = "log_path"

DEFAULT_DAYS_TO_REVIEW = 14
DEFAULT_SCHEDULE_DAY = "sunday"
DEFAULT_SCHEDULE_TIME = "22:00:00"
DEFAULT_THINKING_LEVEL = "high"
DEFAULT_LOG_PATH = "/config/home-assistant.log"
DEFAULT_PROVIDER = "gemini"

PROVIDERS = {
    "gemini": {
        "name": "Google Gemini",
        "models": ["gemini-2.5-pro", "gemini-2.5-flash-latest", "gemini-3.0-pro-preview"],
        "default_model": "gemini-2.5-pro"
    },
    "openai": {
        "name": "OpenAI",
        "models": ["gpt-4o", "gpt-4o-mini", "o1-preview"],
        "default_model": "gpt-4o"
    },
    "anthropic": {
        "name": "Anthropic Claude",
        "models": ["claude-3-7-sonnet-20250219", "claude-3-5-sonnet-20241022"],
        "default_model": "claude-3-7-sonnet-20250219"
    }
}

THINKING_LEVELS = ["low", "medium", "high"]
DAYS_OF_WEEK = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

UPDATE_INTERVAL = timedelta(hours=1)

ATTR_LAST_RUN = "last_run"
ATTR_ERRORS_FOUND = "errors_found"
ATTR_WARNINGS_FOUND = "warnings_found"
ATTR_NEW_ISSUES = "new_issues"
ATTR_ANALYSIS_TEXT = "analysis_text"
ATTR_PROVIDER = "provider"
ATTR_MODEL = "model"

SERVICE_ANALYZE_LOGS = "analyze_logs"
